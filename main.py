"""
Main HTTP Server for Multiple MCP Servers
Manages and routes requests to different MCP servers
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
from contextlib import asynccontextmanager

# Import core components
from core.registry import ServerRegistry

# Import available servers
from servers.crypto_price import CryptoPriceServer
from servers.sun_docs import SunDocsServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPMultiServer')

# Global registry
registry = ServerRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("=" * 60)
    logger.info("🚀 MCP Multi-Server Starting")
    logger.info("=" * 60)
    
    # Register all available servers
    crypto_server = CryptoPriceServer()
    registry.register(crypto_server)
    
    sun_docs_server = SunDocsServer()
    registry.register(sun_docs_server)
    
    logger.info(f"📦 Registered {len(registry.list_servers())} server(s)")
    for server_info in registry.list_servers():
        logger.info(f"   - {server_info['name']} v{server_info['version']}")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(title="MCP Multi-Server", lifespan=lifespan)

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
    """Root endpoint"""
    return {
        "service": "MCP Multi-Server",
        "status": "running",
        "servers": registry.list_servers(),
        "protocol": "MCP over HTTP"
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
            server_info = registry.get_combined_server_info()
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": server_info
                }
            }
            
        elif method == "notifications/initialized":
            # Notification - no response needed
            logger.info("✓ Client initialized")
            return {"jsonrpc": "2.0", "result": None}
            
        elif method == "tools/list":
            # Return list of all available tools from all servers
            all_tools = registry.get_all_tools()
            
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": all_tools
                }
            }
            
        elif method == "tools/call":
            # Call tool
            tool_name = message["params"]["name"]
            arguments = message["params"].get("arguments", {})
            
            logger.info(f"🔧 Calling tool: {tool_name} with args: {arguments}")
            
            try:
                # Call tool through registry
                result = await registry.call_tool(tool_name, arguments)
                
                logger.info(f"✓ Tool {tool_name} executed successfully")
                
                # Format response
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
        
        # Return response - let FastAPI handle JSON encoding
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "servers": registry.list_servers()
    }


@app.get("/servers")
async def list_servers():
    """List all registered servers"""
    return {
        "servers": registry.list_servers()
    }


def main():
    """Main entry point"""
    host = "0.0.0.0"
    port = 8766
    
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
