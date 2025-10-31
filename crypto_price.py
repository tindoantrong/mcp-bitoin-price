# crypto_price.py
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
    """Get current cryptocurrency price from Binance.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC', 'ETH', 'ADA'). 
                Will automatically append 'USDT' to create the pair.
                Examples: 'BTC' → 'BTCUSDT', 'ADA' → 'ADAUSDT'
    
    Returns:
        Dictionary with price information or error message.
    """
    try:
        # Normalize symbol: uppercase and add USDT if not present
        symbol = symbol.upper().strip()
        
        # If user only provides base currency (e.g., 'ADA'), add 'USDT'
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
    """Get prices for multiple cryptocurrencies at once.
    
    Args:
        symbols: Comma-separated list of symbols (e.g., 'BTC,ETH,ADA,BNB')
    
    Returns:
        Dictionary with prices for all requested symbols.
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

