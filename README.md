# Crypto Price MCP Server

MCP Server để lấy giá cryptocurrency từ Binance API, tích hợp với GitHub Copilot.

## 🚀 Tính năng

- ✅ Lấy giá crypto real-time từ Binance
- ✅ Hỗ trợ nhiều loại transport: stdio, WebSocket, HTTP
- ✅ Tích hợp với GitHub Copilot
- ✅ Auto-retry và error handling

## 📦 Cài đặt

```bash
pip install -r requirements.txt
```

## 🔧 Cách sử dụng

### 1. Sử dụng với GitHub Copilot (RECOMMENDED)

#### Cấu hình stdio (Đơn giản nhất):

Thêm vào file cấu hình MCP của GitHub Copilot:

**Windows**: `%APPDATA%\Code\User\globalStorage\github.copilot-chat\mcpServers.json`

**macOS**: `~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/mcpServers.json`

**Linux**: `~/.config/Code/User/globalStorage/github.copilot-chat/mcpServers.json`

Nội dung:
```json
{
  "mcpServers": {
    "crypto-price": {
      "type": "stdio",
      "command": "python",
      "args": ["F:\\wampp\\www\\mcp-bitoin-price\\crypto_price.py"]
    }
  }
}
```

**Lưu ý**: Thay đường dẫn bằng đường dẫn tuyệt đối đến file `crypto_price.py` trên máy bạn.

#### Sau đó:
1. Restart VS Code
2. Mở GitHub Copilot Chat
3. Server sẽ tự động khởi động khi cần

### 2. Sử dụng HTTP Server (Nếu stdio không hoạt động)

#### Chạy server:
```bash
python mcp_http_server.py
```

Server chạy tại: `http://127.0.0.1:8765`

#### Cấu hình cho GitHub Copilot:
```json
{
  "mcpServers": {
    "crypto-price": {
      "type": "streamablehttp",
      "url": "http://127.0.0.1:8765"
    }
  }
}
```

### 3. Sử dụng WebSocket Server

#### Chạy server:
```bash
python mcp_websocket.py
```

Server chạy tại: `ws://localhost:8766`

### 4. Sử dụng với mcp_pipe (Remote WebSocket)

#### Set environment variable:
```bash
# Windows (PowerShell)
$env:MCP_ENDPOINT = "ws://your-server.com:8766"

# Linux/Mac
export MCP_ENDPOINT="ws://your-server.com:8766"
```

#### Chạy:
```bash
python mcp_pipe.py
```

## 📝 Tools có sẵn

### 1. `get_crypto_price`

Lấy giá của một cryptocurrency.

**Parameters:**
- `symbol` (string): Mã cryptocurrency (e.g., 'BTC', 'ETH', 'ADA')

**Example:**
```
Get price of BTC
Get current price of Ethereum
What is the price of Cardano?
```

### 2. `get_multiple_prices`

Lấy giá của nhiều cryptocurrencies cùng lúc.

**Parameters:**
- `symbols` (string): Danh sách mã currencies cách nhau bởi dấu phẩy

**Example:**
```
Get prices of BTC, ETH, ADA, BNB
Show me Bitcoin, Ethereum and Cardano prices
```

## 🧪 Test thử

### Test trực tiếp với curl:

```bash
# Test HTTP server
curl -X POST http://127.0.0.1:8765 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

### Test với GitHub Copilot:

Sau khi cấu hình xong, mở GitHub Copilot Chat và thử:
- "What is the current price of Bitcoin?"
- "Get me the prices of BTC, ETH, and ADA"
- "Show me Cardano price"

## 🔍 Troubleshooting

### Lỗi 405 Method Not Allowed
→ Sử dụng stdio transport thay vì HTTP/SSE

### Server không khởi động
→ Kiểm tra Python đã được cài đặt: `python --version`
→ Kiểm tra dependencies: `pip install -r requirements.txt`

### GitHub Copilot không nhận diện tools
1. Kiểm tra đường dẫn file trong config
2. Restart VS Code
3. Kiểm tra log của GitHub Copilot
4. Thử chạy trực tiếp: `python crypto_price.py`

### Port đã được sử dụng
→ Thay đổi port trong file server (default: 8765, 8766)

## 📂 Cấu trúc Project

```
mcp-bitcoin-price/
├── crypto_price.py          # MCP server chính (stdio)
├── mcp_http_server.py       # HTTP/Streamable transport
├── mcp_websocket.py         # WebSocket broker
├── mcp_pipe.py              # Remote WebSocket client
├── mcp_server.py            # FastAPI server (SSE)
├── requirements.txt         # Python dependencies
├── copilot_config_stdio.json       # Config mẫu (stdio)
├── copilot_config_example.json     # Config mẫu (HTTP)
└── README.md
```

## 🛠️ Development

### Xem logs:
Server sẽ output logs ra stderr. Quan sát để debug.

### Thêm tools mới:
Edit `crypto_price.py` và thêm decorator `@mcp.tool()`:

```python
@mcp.tool()
def your_new_tool(param: str) -> dict:
    """Tool description"""
    # Your code here
    return {"result": "data"}
```

## 📄 License

MIT

## 🤝 Contributing

Pull requests are welcome!

