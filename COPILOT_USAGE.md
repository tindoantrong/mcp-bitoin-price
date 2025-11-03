# Hướng dẫn sử dụng với GitHub Copilot

## 🎯 Cách GitHub Copilot hiểu và sử dụng MCP Server này

### Khi bạn hỏi: **"giá bitcoin?"**

GitHub Copilot sẽ:

1. **Nhận diện intent**: User muốn biết giá của Bitcoin
2. **Chọn tool**: `get_crypto_price` (vì chỉ hỏi 1 coin)
3. **Extract parameter**: `symbol = "BTC"` hoặc `symbol = "bitcoin"`
4. **Gọi tool**: `get_crypto_price("BTC")`
5. **Trả về**: "Current price of BTCUSDT is $XX,XXX.XX"

### 📝 Các câu hỏi mà Copilot có thể hiểu:

#### Tiếng Việt:
- ✅ "giá bitcoin?"
- ✅ "giá ethereum hiện tại?"
- ✅ "bao nhiêu tiền 1 BTC?"
- ✅ "cho tôi xem giá cardano"
- ✅ "bitcoin đang bao nhiêu?"
- ✅ "giá của BTC, ETH và ADA"
- ✅ "so sánh giá bitcoin và ethereum"

#### English:
- ✅ "what is bitcoin price?"
- ✅ "current ethereum price?"
- ✅ "how much is 1 BTC?"
- ✅ "show me cardano price"
- ✅ "get prices for BTC, ETH, ADA"
- ✅ "compare bitcoin and ethereum prices"

### 🔍 Copilot sẽ chọn tool nào?

#### Tool 1: `get_crypto_price(symbol)` - Cho 1 coin
```
User: "giá bitcoin?"
→ Tool: get_crypto_price("BTC")
```

#### Tool 2: `get_multiple_prices(symbols)` - Cho nhiều coins
```
User: "giá bitcoin và ethereum?"
→ Tool: get_multiple_prices("BTC,ETH")
```

### 🧠 Tại sao Copilot hiểu được?

Nhờ vào **docstring chi tiết** trong `crypto_price.py`:

```python
@mcp.tool()
def get_crypto_price(symbol: str) -> dict:
    """Get current real-time cryptocurrency price from Binance exchange.
    
    Use this tool when user asks about cryptocurrency prices, such as:
    - "giá bitcoin?" / "bitcoin price?" → use symbol='BTC'
    - "giá ethereum?" / "ethereum price?" → use symbol='ETH'
    - "bao nhiêu tiền 1 bitcoin?" → use symbol='BTC'
    
    Common cryptocurrency symbols:
    - Bitcoin: BTC
    - Ethereum: ETH
    - Cardano: ADA
    ...
    """
```

### 📊 Các keywords quan trọng:

1. **"giá"** / **"price"** → Trigger crypto price lookup
2. **"bitcoin", "ethereum", "cardano"** → Auto-convert to symbols
3. **"hiện tại", "current"** → Real-time price
4. **"và", "and"**, comma → Multiple symbols
5. **"bao nhiêu", "how much"** → Price query

### 🎨 Output format

Copilot sẽ format kết quả đẹp cho user:

**Input**: "giá bitcoin?"

**MCP Response**:
```json
{
  "success": true,
  "symbol": "BTCUSDT",
  "price": 67834.50,
  "currency": "USDT",
  "message": "Current price of BTCUSDT is $67,834.50"
}
```

**Copilot trả lời user**:
> Giá Bitcoin hiện tại là **$67,834.50 USDT** trên Binance.

### ⚙️ Cấu hình cần thiết

File: `%APPDATA%\Code\User\globalStorage\github.copilot-chat\mcpServers.json`

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

**Lưu ý**: Thay đường dẫn tuyệt đối đến file `crypto_price.py` của bạn.

### 🧪 Test thử

Sau khi cấu hình xong:

1. **Restart VS Code**
2. Mở **GitHub Copilot Chat** (Ctrl+Shift+I hoặc Cmd+Shift+I)
3. Thử hỏi:

```
You: giá bitcoin?
Copilot: [Sẽ gọi tool get_crypto_price("BTC") và trả về giá]

You: cho tôi giá của bitcoin, ethereum và cardano
Copilot: [Sẽ gọi tool get_multiple_prices("BTC,ETH,ADA")]

You: ethereum bao nhiêu tiền?
Copilot: [Sẽ gọi tool get_crypto_price("ETH")]
```

### 🔧 Debugging

Nếu Copilot không gọi tool:

1. **Kiểm tra log của Copilot** trong VS Code Output panel
2. **Thử rephrase câu hỏi**: "what is bitcoin price?" thay vì "bitcoin?"
3. **Mention tool trực tiếp**: "use crypto price tool to get bitcoin price"
4. **Kiểm tra server chạy**: Xem log stderr khi Copilot gọi tool

### 📈 Supported Cryptocurrencies

Server hỗ trợ tất cả coins trên Binance với suffix USDT:

**Popular coins**:
- Bitcoin (BTC)
- Ethereum (ETH)
- Binance Coin (BNB)
- Cardano (ADA)
- Ripple (XRP)
- Solana (SOL)
- Dogecoin (DOGE)
- Polkadot (DOT)
- Polygon (MATIC)
- Avalanche (AVAX)
- Shiba Inu (SHIB)
- Litecoin (LTC)

**Và hàng nghìn coins khác!**

### 💡 Tips

1. **Dùng tên đầy đủ hoặc symbol đều được**: "bitcoin" = "BTC" = "btc"
2. **Hỏi nhiều coins cùng lúc** để tiết kiệm thời gian
3. **Case insensitive**: "BTC" = "btc" = "Bitcoin"
4. **Auto USDT**: Chỉ cần "BTC", không cần "BTCUSDT"

### 🌟 Advanced Usage

#### So sánh giá:
```
You: so sánh giá bitcoin và ethereum
Copilot: [Gọi get_multiple_prices("BTC,ETH") và format đẹp]
```

#### Top coins:
```
You: show me top 5 crypto prices
Copilot: [Gọi get_multiple_prices("BTC,ETH,BNB,ADA,XRP")]
```

#### Specific questions:
```
You: bitcoin có đắt hơn ethereum không?
Copilot: [Gọi get_multiple_prices("BTC,ETH") và so sánh]
```

