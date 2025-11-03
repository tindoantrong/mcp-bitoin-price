# crypto_price.py
"""
MCP Server for Cryptocurrency Price Information

This MCP server provides real-time cryptocurrency price data from Binance exchange.
It can answer questions like:
- "giá bitcoin?" / "what is bitcoin price?"
- "giá ethereum hiện tại?" / "current ethereum price?"
- "bao nhiêu tiền 1 BTC?" / "how much is 1 BTC?"
- "cho tôi giá của BTC, ETH và ADA" / "show me prices of BTC, ETH and ADA"

The server automatically converts cryptocurrency names to symbols:
- 'bitcoin' → 'BTC'
- 'ethereum' → 'ETH'
- 'cardano' → 'ADA'

Tools available:
1. get_crypto_price(symbol) - Get price for a single cryptocurrency
2. get_multiple_prices(symbols) - Get prices for multiple cryptocurrencies

All prices are returned in USDT (Tether USD).
"""
from mcp.server.fastmcp import FastMCP
import sys
import logging
import requests
from typing import Optional

logger = logging.getLogger('CryptoPrice')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("CryptoPrice")

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

@mcp.tool()
def get_crypto_price(symbol: str) -> dict:
    """Get current real-time cryptocurrency price from Binance exchange.
    
    Use this tool when user asks about cryptocurrency prices, such as:
    - "giá bitcoin?" / "bitcoin price?" → use symbol='BTC'
    - "giá ethereum?" / "ethereum price?" → use symbol='ETH'
    - "giá ada?" / "cardano price?" → use symbol='ADA'
    - "bao nhiêu tiền 1 bitcoin?" → use symbol='BTC'
    - "giá hiện tại của BTC?" → use symbol='BTC'
    
    Common cryptocurrency symbols:
    - Bitcoin: BTC
    - Ethereum: ETH
    - Binance Coin: BNB
    - Cardano: ADA
    - Ripple: XRP
    - Solana: SOL
    - Dogecoin: DOGE
    - Polkadot: DOT
    
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
    
    Examples:
        get_crypto_price('BTC') → Bitcoin price in USDT
        get_crypto_price('ethereum') → Ethereum price in USDT
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
                "success": True,
                "symbol": trading_pair,
                "price": price,
                "currency": "USDT",
                "message": f"Current price of {trading_pair} is ${price_str}"
            }
        
        elif response.status_code == 400:
            # Invalid symbol
            logger.warning(f"Invalid symbol: {trading_pair}")
            return {
                "success": False,
                "error": "Invalid symbol",
                "message": f"Symbol '{trading_pair}' not found on Binance. Please check the symbol name."
            }
        
        else:
            logger.error(f"Binance API error: {response.status_code}")
            return {
                "success": False,
                "error": "API error",
                "message": f"Failed to fetch price. Status code: {response.status_code}"
            }
    
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return {
            "success": False,
            "error": "Timeout",
            "message": "Request to Binance API timed out. Please try again."
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return {
            "success": False,
            "error": "Network error",
            "message": f"Failed to connect to Binance API: {str(e)}"
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": "Unknown error",
            "message": f"An unexpected error occurred: {str(e)}"
        }

@mcp.tool()
def get_multiple_prices(symbols: str) -> dict:
    """Get prices for multiple cryptocurrencies at once from Binance.
    
    Use this tool when user asks for multiple prices in one request, such as:
    - "giá bitcoin và ethereum?" → symbols='BTC,ETH'
    - "cho tôi giá của BTC, ETH và ADA" → symbols='BTC,ETH,ADA'
    - "bitcoin, ethereum, cardano bao nhiêu?" → symbols='BTC,ETH,ADA'
    - "list prices of top 5 coins" → symbols='BTC,ETH,BNB,ADA,XRP'
    
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
    
    Examples:
        get_multiple_prices('BTC,ETH') → Prices for Bitcoin and Ethereum
        get_multiple_prices('bitcoin, ethereum, ada') → Prices for 3 coins
    """
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        results = {}
        errors = []
        
        for symbol in symbol_list:
            result = get_crypto_price(symbol)
            
            if result['success']:
                # Store formatted price string instead of raw float
                formatted_price = format_price(result['price'])
                results[result['symbol']] = formatted_price
            else:
                errors.append(f"{symbol}: {result['message']}")
        
        return {
            "success": len(errors) == 0,
            "prices": results,
            "errors": errors if errors else None,
            "count": len(results)
        }
    
    except Exception as e:
        logger.error(f"Error in get_multiple_prices: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch multiple prices"
        }

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")

