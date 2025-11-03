"""
Crypto Price Tools Module
Provides functions to fetch cryptocurrency prices from Binance
"""
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger('CryptoPrice.Tools')

# Binance API endpoint
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"

# Mapping Vietnamese/English names to symbols for better understanding
CRYPTO_NAME_TO_SYMBOL = {
    'bitcoin': 'BTC',
    'btc': 'BTC',
    'ethereum': 'ETH',
    'eth': 'ETH',
    'binance': 'BNB',
    'bnb': 'BNB',
    'cardano': 'ADA',
    'ada': 'ADA',
    'ripple': 'XRP',
    'xrp': 'XRP',
    'solana': 'SOL',
    'sol': 'SOL',
    'dogecoin': 'DOGE',
    'doge': 'DOGE',
    'polkadot': 'DOT',
    'dot': 'DOT',
    'avalanche': 'AVAX',
    'avax': 'AVAX',
    'shiba': 'SHIB',
    'shib': 'SHIB',
    'matic': 'MATIC',
    'polygon': 'MATIC',
    'litecoin': 'LTC',
    'ltc': 'LTC',
}


def normalize_symbol(symbol: str) -> str:
    """Convert cryptocurrency name to standard symbol.
    
    Examples:
        'bitcoin' → 'BTC'
        'ethereum' → 'ETH'
        'BTC' → 'BTC'
    """
    symbol_lower = symbol.lower().strip()
    return CRYPTO_NAME_TO_SYMBOL.get(symbol_lower, symbol.upper().strip())


def format_price(price: float) -> str:
    """Format price by removing trailing zeros."""
    if price >= 1:
        # For prices >= 1, show 2-4 decimals
        return f"{price:,.4f}".rstrip('0').rstrip('.')
    else:
        # For prices < 1, show up to 8 decimals, remove trailing zeros
        return f"{price:.8f}".rstrip('0').rstrip('.')


def get_crypto_price(symbol: str) -> Dict[str, Any]:
    """Get current real-time cryptocurrency price from Binance exchange.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'ADA'). 
                Just provide the base currency, USDT will be added automatically.
                Case insensitive - 'btc', 'BTC', 'Bitcoin' all work.
    
    Returns:
        Dictionary containing:
        - success: True if price retrieved successfully
        - symbol: Trading pair used (e.g., 'BTCUSDT')
        - price: Current price in USDT (numeric)
        - currency: Always 'USDT'
        - message: Human-readable price message
    """
    try:
        # Normalize symbol: convert names like 'bitcoin' to 'BTC'
        symbol = normalize_symbol(symbol)
        
        # If user only provides base currency (e.g., 'BTC'), add 'USDT'
        if not symbol.endswith('USDT'):
            trading_pair = f"{symbol}USDT"
        else:
            trading_pair = symbol
        
        logger.info(f"Fetching price for {trading_pair}...")
        
        # Make request to Binance API
        params = {'symbol': trading_pair}
        response = requests.get(BINANCE_API_URL, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            price_str = format_price(price)
            
            logger.info(f"Price for {trading_pair}: ${price_str}")
            
            return {
                'success': True,
                'symbol': trading_pair,
                'price': price,
                'currency': 'USDT',
                'message': f'Current price of {trading_pair} is ${price_str}'
            }
        else:
            # Handle error responses
            error_msg = f"Error fetching price for {trading_pair}: HTTP {response.status_code}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'symbol': trading_pair,
                'error': error_msg,
                'message': f'Failed to get price for {trading_pair}. Please check if the symbol is correct.'
            }
            
    except requests.exceptions.RequestException as e:
        # Handle network/connection errors
        error_msg = f"Network error while fetching {symbol}: {str(e)}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'symbol': symbol,
            'error': error_msg,
            'message': 'Network error occurred. Please try again later.'
        }
    except Exception as e:
        # Handle any other unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'symbol': symbol,
            'error': error_msg,
            'message': 'An unexpected error occurred. Please try again.'
        }


def get_multiple_prices(symbols: str) -> Dict[str, Any]:
    """Get prices for multiple cryptocurrencies at once from Binance.
    
    Args:
        symbols: Comma-separated list of cryptocurrency symbols.
                 Examples: 'BTC,ETH,ADA', 'bitcoin,ethereum,cardano'
                 Case insensitive, spaces are trimmed automatically.
    
    Returns:
        Dictionary containing:
        - success: True if all prices retrieved successfully
        - prices: Object mapping symbols to their prices (e.g., {'BTCUSDT': '50000'})
        - errors: List of error messages if any symbol failed
        - count: Number of successful price retrievals
    """
    try:
        # Split and clean symbol list
        symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]
        
        if not symbol_list:
            return {
                'success': False,
                'error': 'No symbols provided',
                'message': 'Please provide at least one cryptocurrency symbol'
            }
        
        logger.info(f"Fetching prices for {len(symbol_list)} cryptocurrencies...")
        
        prices = {}
        errors = []
        
        # Fetch price for each symbol
        for symbol in symbol_list:
            result = get_crypto_price(symbol)
            
            if result['success']:
                prices[result['symbol']] = format_price(result['price'])
            else:
                errors.append(f"{symbol}: {result.get('error', 'Unknown error')}")
        
        # Prepare response
        if prices:
            success = len(errors) == 0
            message = f"Successfully retrieved {len(prices)} price(s)"
            if errors:
                message += f", {len(errors)} failed"
            
            return {
                'success': success,
                'prices': prices,
                'errors': errors if errors else None,
                'count': len(prices),
                'message': message
            }
        else:
            return {
                'success': False,
                'errors': errors,
                'message': 'Failed to retrieve any prices'
            }
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'error': error_msg,
            'message': 'An unexpected error occurred while processing multiple symbols'
        }
