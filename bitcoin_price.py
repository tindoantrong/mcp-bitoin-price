from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("BitcoinPrice")

@mcp.tool()
def get_bitcoin_price() -> dict:
    """Get current Bitcoin/USDT price from Binance"""
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        data = response.json()
        price = float(data["price"])
        return {"success": True, "price": price, "symbol": "BTC/USDT"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")