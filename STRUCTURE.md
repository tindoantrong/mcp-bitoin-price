# Cấu trúc Project - MCP Multi-Server

## 📁 Cấu trúc thư mục

```
mcp-bitoin-price/
├── core/                      # Core framework
│   ├── __init__.py
│   ├── base_server.py        # Base class cho tất cả MCP servers
│   └── registry.py           # Server registry để quản lý nhiều servers
│
├── servers/                   # Các MCP servers
│   ├── __init__.py
│   └── crypto_price/         # Crypto Price Server
│       ├── __init__.py
│       ├── server.py         # Server implementation
│       └── tools.py          # Tool functions
│
├── config/                    # Configuration files
│
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## 🏗️ Kiến trúc

### 1. Core Framework (`core/`)

#### `base_server.py` - Base Server Class
Abstract base class định nghĩa interface cho tất cả MCP servers:

```python
from core.base_server import BaseMCPServer

class YourServer(BaseMCPServer):
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        pass
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Execute a tool"""
        pass
```

**Methods cần implement:**
- `get_tools()` - Trả về danh sách tools available
- `call_tool()` - Execute tool với arguments

**Utility methods có sẵn:**
- `get_server_info()` - Server name và version
- `get_capabilities()` - Server capabilities
- `format_tool_response()` - Format response theo MCP protocol

#### `registry.py` - Server Registry
Quản lý nhiều servers và routing requests:

```python
registry = ServerRegistry()
registry.register(YourServer())

# Get all tools from all servers
all_tools = registry.get_all_tools()

# Call tool (auto-routing)
result = await registry.call_tool("tool_name", {"arg": "value"})
```

### 2. Servers (`servers/`)

Mỗi server là một module riêng biệt:

```
servers/
└── your_server/
    ├── __init__.py       # Export server class
    ├── server.py         # Server implementation
    └── tools.py          # Tool functions
```

**Example: Crypto Price Server**
```python
# servers/crypto_price/server.py
from core.base_server import BaseMCPServer
from .tools import get_crypto_price

class CryptoPriceServer(BaseMCPServer):
    def __init__(self):
        super().__init__(name="CryptoPrice", version="1.0.0")
    
    def get_tools(self):
        return [
            {
                "name": "get_crypto_price",
                "description": "Get cryptocurrency price",
                "inputSchema": {...}
            }
        ]
    
    async def call_tool(self, tool_name, arguments):
        if tool_name == "get_crypto_price":
            return get_crypto_price(**arguments)
```

### 3. Main Entry Point (`main.py`)

FastAPI application với MCP protocol support:

```python
from core.registry import ServerRegistry
from servers.crypto_price import CryptoPriceServer

registry = ServerRegistry()

# Register servers
registry.register(CryptoPriceServer())
registry.register(YourNewServer())

# FastAPI app handles MCP protocol
# POST /sse - MCP JSON-RPC endpoint
# GET /servers - List all servers
# GET /health - Health check
```

## 🚀 Cách thêm Server mới

### Bước 1: Tạo thư mục server

```bash
mkdir servers/your_server
```

### Bước 2: Tạo `tools.py` với các functions

```python
# servers/your_server/tools.py
def your_tool(param1: str, param2: int) -> dict:
    """Your tool implementation"""
    return {
        "success": True,
        "result": "Your result"
    }
```

### Bước 3: Tạo `server.py` với server class

```python
# servers/your_server/server.py
from core.base_server import BaseMCPServer
from .tools import your_tool

class YourServer(BaseMCPServer):
    def __init__(self):
        super().__init__(name="YourServer", version="1.0.0")
    
    def get_tools(self):
        return [
            {
                "name": "your_tool",
                "description": "Description of your tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Parameter 1"
                        },
                        "param2": {
                            "type": "integer",
                            "description": "Parameter 2"
                        }
                    },
                    "required": ["param1", "param2"]
                }
            }
        ]
    
    async def call_tool(self, tool_name, arguments):
        if tool_name == "your_tool":
            return your_tool(**arguments)
        raise ValueError(f"Unknown tool: {tool_name}")
```

### Bước 4: Export trong `__init__.py`

```python
# servers/your_server/__init__.py
from .server import YourServer

__all__ = ['YourServer']
```

### Bước 5: Register trong `main.py`

```python
# main.py
from servers.your_server import YourServer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...
    
    # Add your server
    your_server = YourServer()
    registry.register(your_server)
    
    yield
```

## 🧪 Testing

### Khởi động server:
```bash
python main.py
```

### Test với curl:
```bash
# List all tools
curl -X POST http://localhost:8766/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool
curl -X POST http://localhost:8766/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_crypto_price",
      "arguments": {
        "symbol": "BTC"
      }
    }
  }'
```

## 📝 MCP Protocol Support

Server hỗ trợ các MCP methods:

1. **initialize** - Initialize connection
2. **notifications/initialized** - Client ready notification
3. **tools/list** - List all available tools
4. **tools/call** - Execute a tool

## 🔧 Configuration

Cấu hình server trong `mcp.json` (VS Code):

```json
{
    "servers": {
        "your_server": {
            "type": "fetch",
            "url": "http://localhost:8766/sse"
        }
    }
}
```

## 🎯 Best Practices

1. **Mỗi server nên có scope rõ ràng** (ví dụ: crypto prices, weather, etc.)
2. **Tools nên pure functions** - dễ test và maintain
3. **Error handling đầy đủ** - trả về proper error messages
4. **Logging chi tiết** - để debug dễ dàng
5. **Type hints** - để code dễ đọc và IDE support tốt

## 📚 Examples

### Example 1: Weather Server
```python
# servers/weather/tools.py
def get_weather(city: str) -> dict:
    # Implementation
    pass

# servers/weather/server.py
class WeatherServer(BaseMCPServer):
    def __init__(self):
        super().__init__(name="Weather", version="1.0.0")
    # ... implementation
```

### Example 2: Database Query Server
```python
# servers/database/tools.py
def query_database(sql: str) -> dict:
    # Implementation
    pass

# servers/database/server.py
class DatabaseServer(BaseMCPServer):
    def __init__(self):
        super().__init__(name="Database", version="1.0.0")
    # ... implementation
```

## 🐛 Troubleshooting

### Server không start được
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8766 không bị chiếm

### Tool không được list
- Verify server được register trong `main.py`
- Check `get_tools()` return đúng format
- Check logs để xem errors

### Tool execution lỗi
- Check tool function signature
- Verify arguments match inputSchema
- Check logs để xem detailed error

## 🚦 Deployment

### Development
```bash
python main.py
```

### Production (với gunicorn)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8766
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```
