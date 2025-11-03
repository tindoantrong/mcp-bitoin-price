"""
Crypto Price MCP Server Implementation
"""
from typing import Dict, List, Any
import logging
from core.base_server import BaseMCPServer
from .tools import get_crypto_price, get_multiple_prices

logger = logging.getLogger('CryptoPriceServer')


class CryptoPriceServer(BaseMCPServer):
    """MCP Server for cryptocurrency price information"""
    
    def __init__(self):
        super().__init__(name="CryptoPrice", version="1.0.0")
        self.logger.info("Crypto Price Server initialized")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return [
            {
                "name": "get_crypto_price",
                "description": "Get current real-time cryptocurrency price from Binance exchange",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'ADA')"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_multiple_prices",
                "description": "Get prices for multiple cryptocurrencies at once from Binance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "string",
                            "description": "Comma-separated list of cryptocurrency symbols (e.g., 'BTC,ETH,ADA')"
                        }
                    },
                    "required": ["symbols"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        self.logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        if tool_name == "get_crypto_price":
            result = get_crypto_price(**arguments)
        elif tool_name == "get_multiple_prices":
            result = get_multiple_prices(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return result
