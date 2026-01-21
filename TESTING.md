# Local Testing Guide

This guide explains how to test the CTS Trading API MCP server locally.

## Prerequisites

✅ **Already Installed:**
- Python 3.10+
- Project dependencies (`uv pip install -e .`)

⚠️ **For Full Testing:**
- CTS Trading API COM object (from CTBC Securities)
- Valid trading credentials
- Access to trading server

## Testing Methods

### 1. 🔍 MCP Inspector (Recommended - Interactive UI)

**The MCP Inspector is currently running!**

**Access:** Open your browser to:
```
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<token>
```

**Features:**
- ✅ Visual interface for all tools
- ✅ Test tools with custom parameters
- ✅ See request/response in real-time
- ✅ Validate tool schemas
- ✅ No coding required

**How to Use:**

1. **View Tools:**
   - All 20+ tools are listed in the left sidebar
   - Click any tool to see its schema

2. **Test a Tool:**
   - Click `get_connection_status` → Execute
   - Click `initialize` → Enter `trade_das_url` → Execute
   - View response in the output panel

3. **Test Authentication Flow:**
   ```
   1. initialize → with your server URL
   2. login → with credentials
   3. connect
   4. get_accounts → see your accounts
   ```

**Start/Restart Inspector:**
```bash
uv run mcp dev ctbcsec_mcp\server.py
```

---

### 2. 🐍 Direct Python Testing (No COM Object Needed)

**Test models and enums without the COM object:**

```bash
# Run the test script
python tests\test_local.py
```

**What it tests:**
- ✅ Pydantic model creation
- ✅ Enum values
- ✅ Model serialization
- ✅ Server module imports
- ✅ Wrapper creation (will fail without COM object)

**Create Your Own Test:**

```python
# test_my_functions.py
from ctbcsec_mcp.models import OrderRequest, BuySell, PriceType

# Test creating an order request
order = OrderRequest(
    account_id="123456",
    trade_date="20260121",
    stock_id="2330",        # TSMC
    quantity="1000",
    price="500",
    buy_sell=BuySell.BUY
)

print(order.model_dump_json(indent=2))
```

---

### 3. 🧪 Python REPL Testing

**Quick interactive testing:**

```bash
# Start Python REPL
python

# Then in the REPL:
>>> from ctbcsec_mcp.models import *
>>> from ctbcsec_mcp.server import *

# Test enums
>>> BuySell.BUY
<BuySell.BUY: 1>

>>> PriceType.MARKET
<PriceType.MARKET: 4>

# Create a model
>>> order = OrderRequest(
...     account_id="123",
...     trade_date="20260121", 
...     stock_id="2330",
...     quantity="1000",
...     price="500",
...     buy_sell=BuySell.BUY
... )
>>> print(order.model_dump_json(indent=2))
```

---

### 4. 🖥️ With COM Object (Full Functionality)

**If you have CTS Trading API installed:**

```python
# test_with_com.py
from ctbcsec_mcp.wrapper import TradeAppWrapper

# Create wrapper
wrapper = TradeAppWrapper()
wrapper.create_com_object()

# Initialize
result, err_code, err_msg = wrapper.init("apsit.ectest.ctbcsec.com/tradedas")
print(f"Init result: {result}, Message: {err_msg}")

# Login
result, err_code, err_msg = wrapper.login("your_user_id", "your_password")
print(f"Login result: {result}, Message: {err_msg}")

# Connect
result = wrapper.connect()
print(f"Connect result: {result}")

# Get accounts
accounts = wrapper.get_accounts()
for account in accounts:
    print(f"Account: {account.account_id}, Type: {account.account_type}")

# Query positions
result = wrapper.stock_query_position("your_account_id", "20260121", 1)
print(f"Query result: {result}")
```

---

### 5. 🤖 Claude Desktop Integration

**Test with real Claude:**

1. **Install to Claude Desktop:**
   ```bash
   uv run mcp install ctbcsec_mcp\server.py
   ```

2. **Or manually edit** `%APPDATA%\Claude\claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "ctbcsec-trading": {
         "command": "uv",
         "args": [
           "--directory",
           "d:\\ctbcsec-api-mcp-server",
           "run",
           "ctbcsec-mcp"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Test in Claude:**
   ```
   You: Check the connection status of the CTS trading API
   
   You: Initialize the trading API with server "apsit.ectest.ctbcsec.com/tradedas"
   
   You: Get my trading accounts
   ```

---

## Test Scenarios

### ✅ Scenario 1: Model Validation

**Goal:** Verify all Pydantic models work correctly

```bash
python tests\test_local.py
```

**Expected:** All model tests pass, enums display correctly

---

### ✅ Scenario 2: Tool Schema Validation

**Goal:** Ensure all tools have correct schemas

1. Run MCP Inspector: `uv run mcp dev ctbcsec_mcp\server.py`
2. Open in browser
3. Click through each tool
4. Verify parameter types and descriptions

---

### ✅ Scenario 3: Authentication Flow (with COM)

**Goal:** Test complete login sequence

Using MCP Inspector or Python:

1. `initialize(trade_das_url="...")`
2. `login(user_id="...", password="...")`
3. `connect()`
4. `get_accounts()`
5. Verify accounts returned

---

### ✅ Scenario 4: Order Placement (Paper Trading)

**Goal:** Test order creation

**In MCP Inspector:**

1. Select `stock_new_order`
2. Fill parameters:
   - `account_id`: Your account
   - `stock_id`: "2330"
   - `quantity`: "1000"
   - `price`: "500"
   - `buy_sell`: 1 (BUY)
   - `price_type`: 0 (LIMIT)
3. Execute
4. Check response

---

### ✅ Scenario 5: Query Operations

**Goal:** Test position/order queries

**Tools to test:**
- `stock_query_position`
- `stock_query_order`
- `stock_query_match`
- `futopt_query_oi`
- `futopt_query_equity`

---

## Troubleshooting

### ❌ "COM object not found"

**Error:** `類別未登錄` (Class not registered)

**Solution:** 
- Install CTS Trading API from CTBC Securities
- Run the API client once to register COM object
- Or test only models/enums (doesn't need COM)

---

### ❌ MCP Inspector won't start

**Solution:**
```bash
# Kill existing process
# Ctrl+C in the terminal

# Restart
uv run mcp dev ctbcsec_mcp\server.py
```

---

### ❌ Import errors

**Solution:**
```bash
# Reinstall package
uv pip install -e .

# Or use absolute imports
python -c "from ctbcsec_mcp.models import *; print('OK')"
```

---

## Quick Command Reference

```bash
# Run local Python tests
python tests\test_local.py

# Start MCP Inspector
uv run mcp dev ctbcsec_mcp\server.py

# Install to Claude Desktop
uv run mcp install ctbcsec_mcp\server.py

# Python REPL for quick tests
python
>>> from ctbcsec_mcp.models import *

# Check server can import
uv run python -c "from ctbcsec_mcp.server import mcp; print(mcp.name)"
```

---

## What Works Without COM Object

✅ **Available:**
- All Pydantic models
- All enums (TradeType, BuySell, PriceType, etc.)
- Model serialization/validation
- Server import and tool registration
- MCP Inspector (shows tools but can't execute)

❌ **Requires COM:**
- Actual API calls (init, login, connect)
- Order placement
- Query operations
- Account retrieval

---

## Next Steps

1. ✅ **Run** `python tests\test_local.py` to verify models
2. ✅ **Use** MCP Inspector (already running!) to test tool schemas
3. 📋 **Install** CTS Trading API to test full functionality
4. 🤖 **Integrate** with Claude Desktop for AI-powered trading

---

**Current Status:** ✅ Models tested successfully! MCP Inspector is running.
