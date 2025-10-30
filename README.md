# MCP Bitcoin Price Server

Đơn giản nhất có thể để lấy giá Bitcoin/USDT.

## Cài đặt:
```bash
pip install -r requirements.txt
```

## Chạy:
```bash
export MCP_ENDPOINT="ws://your-websocket-endpoint"
python mcp_pipe.py
```

## Tool:
- `get_bitcoin_price()`: Lấy giá BTC/USDT từ Binance API