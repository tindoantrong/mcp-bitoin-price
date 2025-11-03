# 🚀 Quick Start Guide - Refactored MCP Multi-Server

## ✅ Đã hoàn thành

Project đã được refactor thành công với kiến trúc mới cho phép dễ dàng mở rộng nhiều servers!

### 🎯 Thay đổi chính

**Trước (Old):**
```
mcp-bitoin-price/
├── crypto_price.py         # Monolithic file
├── mcp_http_server.py      # Tight coupling
└── requirements.txt
```

**Sau (New):**
```
mcp-bitoin-price/
├── core/                    # ✨ Core framework
│   ├── base_server.py      # Abstract base class
│   └── registry.py         # Server manager
├── servers/                 # ✨ Pluggable servers
│   └── crypto_price/       # Modular server
│       ├── server.py       # Server implementation
│       └── tools.py        # Business logic
├── main.py                  # ✨ Unified entry point
└── STRUCTURE.md            # ✨ Documentation
```

## 🚀 Khởi động server mới

```bash
# Cách cũ (deprecated)
python mcp_http_server.py

# Cách mới (recommended)
python main.py
```

Output khi chạy thành công:
```
============================================================
🚀 MCP Multi-Server Starting
============================================================
Crypto Price Server initialized
Registered server: CryptoPrice v1.0.0
📦 Registered 1 server(s)
   - CryptoPrice v1.0.0
🌐 Server: http://0.0.0.0:8766
📝 Endpoint: POST http://0.0.0.0:8766/sse
============================================================
```

## 📝 API Endpoints

### 1. Health Check
```bash
curl http://localhost:8766/health
```

### 2. List Servers
```bash
curl http://localhost:8766/servers
```

### 3. MCP Protocol (SSE)
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

## 🔧 Configuration

Update `mcp.json` trong VS Code:

```json
{
    "servers": {
        "crypto_price": {
            "type": "fetch",
            "url": "http://localhost:8766/sse"
        }
    }
}
```

## ➕ Thêm Server mới

### Ví dụ: Weather Server

#### 1. Tạo structure
```bash
mkdir servers/weather
```

#### 2. Tạo `tools.py`
```python
# servers/weather/tools.py
def get_weather(city: str) -> dict:
    return {
        "city": city,
        "temperature": 25,
        "condition": "Sunny"
    }
```

#### 3. Tạo `server.py`
```python
# servers/weather/server.py
from core.base_server import BaseMCPServer
from .tools import get_weather

class WeatherServer(BaseMCPServer):
    def __init__(self):
        super().__init__(name="Weather", version="1.0.0")
    
    def get_tools(self):
        return [{
            "name": "get_weather",
            "description": "Get weather for a city",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }]
    
    async def call_tool(self, tool_name, arguments):
        if tool_name == "get_weather":
            return get_weather(**arguments)
```

#### 4. Tạo `__init__.py`
```python
# servers/weather/__init__.py
from .server import WeatherServer
__all__ = ['WeatherServer']
```

#### 5. Register trong `main.py`
```python
from servers.weather import WeatherServer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...
    
    # Add weather server
    weather_server = WeatherServer()
    registry.register(weather_server)
    
    yield
```

#### 6. Restart và test
```bash
python main.py
```

Output sẽ hiện:
```
📦 Registered 2 server(s)
   - CryptoPrice v1.0.0
   - Weather v1.0.0
```

## 🎨 Kiến trúc

```
┌─────────────────────────────────────┐
│         GitHub Copilot              │
│         (MCP Client)                │
└────────────┬────────────────────────┘
             │ MCP Protocol (JSON-RPC)
             ▼
┌─────────────────────────────────────┐
│         main.py                     │
│         FastAPI + MCP Handler       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      ServerRegistry                 │
│      (Route to appropriate server)  │
└────────────┬────────────────────────┘
             │
        ┌────┴────┬────────┬─────────┐
        ▼         ▼        ▼         ▼
   ┌─────────┐ ┌──────┐ ┌────────┐ ...
   │ Crypto  │ │Weather│ │Database│
   │ Server  │ │Server │ │ Server │
   └─────────┘ └──────┘ └────────┘
```

## 📚 Files Guide

| File | Purpose |
|------|---------|
| `main.py` | Entry point, FastAPI app, MCP protocol handler |
| `core/base_server.py` | Abstract base class for all servers |
| `core/registry.py` | Server registry and routing |
| `servers/*/server.py` | Server implementation |
| `servers/*/tools.py` | Business logic functions |
| `STRUCTURE.md` | Detailed architecture documentation |

## 🐛 Troubleshooting

### Port already in use
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
killall python
```

### Import errors
```bash
# Make sure you're in the correct directory
cd f:\wampp\www\mcp-bitoin-price

# Verify Python can find modules
python -c "import core, servers"
```

### Server not registered
Check in `main.py` that your server is imported and registered:
```python
from servers.your_server import YourServer
registry.register(YourServer())
```

## 📖 Documentation

- **STRUCTURE.md** - Chi tiết về kiến trúc và cách extend
- **README.md** - Documentation gốc
- **COPILOT_USAGE.md** - Hướng dẫn sử dụng với GitHub Copilot

## ✨ Benefits của kiến trúc mới

1. **Modularity** - Mỗi server độc lập, dễ maintain
2. **Scalability** - Thêm server mới không ảnh hưởng code cũ
3. **Testability** - Test từng server riêng biệt
4. **Reusability** - Share base class và utilities
5. **Clear separation** - Business logic tách khỏi protocol handling

## 🎯 Next Steps

1. ✅ Server đang chạy thành công
2. ✅ Test với GitHub Copilot
3. 🔄 Thêm servers mới theo nhu cầu
4. 🔄 Add more features (authentication, rate limiting, etc.)

## 💡 Tips

- Mỗi server nên có scope rõ ràng (single responsibility)
- Tools nên là pure functions để dễ test
- Luôn validate input trong tools
- Log đầy đủ để debug dễ dàng
- Viết docstring chi tiết cho tools

---

**Happy coding! 🚀**
