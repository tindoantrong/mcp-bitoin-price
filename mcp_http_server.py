"""
MCP HTTP Server cho GitHub Copilot - Version 2
Import trực tiếp MCP server thay vì dùng subprocess
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
from contextlib import asynccontextmanager

# Import MCP server
from crypto_price import mcp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCP_HTTP_V2')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("=" * 60)
    logger.info("🚀 MCP HTTP Server V2 Starting")
    logger.info("=" * 60)
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Crypto Price MCP Server V2", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Crypto Price MCP Server V2",
        "status": "running",
        "protocol": "MCP over HTTP (direct import)"
    }

@app.post("/sse")
async def handle_sse_request(request: Request):
    """SSE endpoint for MCP (GitHub Copilot compatibility)"""
    try:
        # Parse JSON-RPC request
        body = await request.body()
        message = json.loads(body.decode('utf-8'))
        
        method = message.get('method', 'unknown')
        msg_id = message.get('id')
        
        logger.info(f"📨 Request: {method} (id={msg_id})")
        logger.debug(f"Full message: {message}")
        
        # Handle different MCP methods
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "CryptoPrice",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "notifications/initialized":
            # Notification - no response needed
            logger.info("✓ Client initialized")
            return {"jsonrpc": "2.0", "result": None}
            
        elif method == "tools/list":
            # Return list of available tools
            tools = [
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
            
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": tools
                }
            }
            
        elif method == "tools/call":
            # Call tool
            tool_name = message["params"]["name"]
            arguments = message["params"].get("arguments", {})
            
            logger.info(f"🔧 Calling tool: {tool_name} with args: {arguments}")
            
            # Import tool functions
            from crypto_price import get_crypto_price, get_multiple_prices
            
            # Map tool names to functions
            tool_map = {
                "get_crypto_price": get_crypto_price,
                "get_multiple_prices": get_multiple_prices
            }
            
            if tool_name in tool_map:
                tool_func = tool_map[tool_name]
                
                try:
                    # Call the tool
                    result = tool_func(**arguments)
                    
                    logger.info(f"✓ Tool {tool_name} executed successfully")
                    
                    # Ensure proper JSON serialization
                    result_text = json.dumps(result, ensure_ascii=False, indent=2)
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result_text
                                }
                            ]
                        }
                    }
                except Exception as e:
                    logger.error(f"Tool execution error: {e}", exc_info=True)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution failed: {str(e)}"
                        }
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
        
        else:
            # Unknown method
            logger.warning(f"Unknown method: {method}")
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        # Return response - let FastAPI handle JSON encoding automatically
        logger.info(f"✓ Sending response for {method}")
        logger.debug(f"Response: {response}")
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}},
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": message.get("id") if 'message' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            },
            status_code=500
        )

@app.get("/health")
async def health():
    return {"status": "healthy"}

def main():
    host = "0.0.0.0"
    port = 8766  # Changed port to avoid conflict
    
    logger.info(f"🌐 Server: http://{host}:{port}")
    logger.info(f"📝 Endpoint: POST http://{host}:{port}/sse")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
