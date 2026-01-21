# CTS Trading API Guidebook

## Overview

The CTS Trading API is a COM-based API for trading stocks, futures, and options through the CTBC Securities trading platform. This guidebook provides comprehensive documentation for integrating and using the CTS Trading API in Python applications.

## Table of Contents

- [System Requirements](#system-requirements)
- [Setup and Installation](#setup-and-installation)
- [Architecture Overview](#architecture-overview)
- [Authentication](#authentication)
- [API Reference](#api-reference)
  - [Core Methods](#core-methods)
  - [Stock Trading](#stock-trading)
  - [Futures & Options Trading](#futures--options-trading)
  - [Query Methods](#query-methods)
- [Code Examples](#code-examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## System Requirements

- **Operating System**: Windows (COM object requires Windows)
- **Python Version**: Python 3.10 or higher
- **Required Libraries**:
  - `pywin32` - For COM object interaction
  - `PyQt5` - For GUI applications (optional)

## Setup and Installation

### 1. Install Required Dependencies

```bash
pip install pywin32 PyQt5
```

### 2. Configuration File

Create an `appsetting.json` file with your trading DAS server endpoint:

```json
{
    "TradeDas": "apsit.ectest.ctbcsec.com/tradedas"
}
```

### 3. Initialize the Trade Application

```python
import win32com.client
import json

# Create COM object instance
tradeApp = win32com.client.Dispatch("DJTRADEOBJLibCTS.TradeApp")

# Load configuration
with open('appsetting.json', 'r') as jsonFile:
    config = json.load(jsonFile)

# Initialize the application
(ret, errCode, errMsg) = tradeApp.Init(config["TradeDas"])

if ret != 1:
    print(f"Initialization failed: {errMsg}")
```

---

## Architecture Overview

### COM Object

The CTS Trading API is accessed through a COM object: `DJTRADEOBJLibCTS.TradeApp`

### Event Handler

The API uses an event-driven architecture with callbacks for data responses:

```python
class EventHandler:
    def OnDataResponse(self, eventID, responseData):
        print(f"Event {eventID}: {responseData}")
        return

# Attach event handler
tradeApp = win32com.client.DispatchWithEvents("DJTRADEOBJLibCTS.TradeApp", EventHandler)
```

### Event Types

| Event ID | Description |
|----------|-------------|
| 1 | Connection status change |
| 10 | Query results |
| 100 | General messages |
| 101-103 | Order/Match/Position responses |

---

## Authentication

### Login

```python
def login(user_id, password):
    (result, errCode, errMsg) = tradeApp.Login(user_id, password)
    
    if result == 1:
        print("Login successful")
        return True
    else:
        print(f"Login failed: {errMsg}")
        return False
```

**Parameters:**
- `user_id` (string): User account ID
- `password` (string): User password

**Returns:**
- Tuple: `(result, errorCode, errorMessage)`
  - `result`: 1 for success, 0 for failure
  - `errorCode`: Error code if failed
  - `errorMessage`: Error description if failed

### Connect to Trading Server

```python
def connect():
    result = tradeApp.Connect()
    
    if result != 0:
        print("Connected to trading server")
        return True
    else:
        print("Connection failed")
        return False
```

### Disconnect

```python
def disconnect():
    tradeApp.Disconnect()
    print("Disconnected from trading server")
```

### Logout

```python
def logout(user_id):
    tradeApp.Logout(user_id)
    print("Logged out successfully")
```

### Get Account Information

```python
def get_accounts():
    count = tradeApp.GetAccountCount()
    accounts = []
    
    for i in range(count):
        account_data = tradeApp.GetAccount(i)
        account_data = account_data.strip('<>')
        
        # Parse account data
        fields = account_data.split("|")
        account_info = {}
        for field in fields:
            key, value = field.split("=")
            account_info[key] = value
        
        accounts.append(account_info)
    
    return accounts
```

**Account Data Format:**
- `AccID`: Account ID
- `AccName`: Account name
- `UID`: User ID
- `AccType`: Account type (1=Stock, 2=Futures/Options, 3=International)

---

## API Reference

### Core Methods

#### `Init(tradeDasUrl)`

Initialize the trading application with the DAS server URL.

**Parameters:**
- `tradeDasUrl` (string): Trading DAS server endpoint

**Returns:**
- Tuple: `(result, errorCode, errorMessage)`

#### `SetEchoType(type1, type2)`

Configure echo settings for the application.

**Parameters:**
- `type1` (int): Echo type parameter 1
- `type2` (int): Echo type parameter 2

#### `SetLotSizeData(lotSizeString)`

Set lot size data for specific stocks.

**Parameters:**
- `lotSizeString` (string): Lot size configuration (e.g., "0050=1000|0028=1000")

**Example:**
```python
tradeApp.SetLotSizeData("0050=1000|0028=1000")
```

#### `Fini()`

Finalize and clean up the trading application.

---

### Stock Trading

#### `Stock_NewOrder()`

Place a new stock order.

**Signature:**
```python
Stock_NewOrder(accountID, tradeDate, TT, OT, BS, stockID, qty, PT, price, broker, payType, cond)
```

**Parameters:**

| Parameter | Type | Description | Values |
|-----------|------|-------------|--------|
| `accountID` | string | Account ID | From GetAccount() |
| `tradeDate` | string | Trading date | Format: YYYYMMDD |
| `TT` | int | Trade type | 0=Regular, 1=After-hours odd lot, 2=After-hours, 5=Emerging, 7=Intraday odd lot |
| `OT` | int | Order type | 0=Cash, 1=Margin, 2=Short, 16=Day trading sell first |
| `BS` | int | Buy/Sell | 1=Buy, 2=Sell |
| `stockID` | string | Stock symbol | e.g., "2330" |
| `qty` | string | Quantity | Number of shares |
| `PT` | int | Price type | 0=Limit, 1=Limit up, 2=Limit down, 3=Flat, 4=Market |
| `price` | string | Order price | "0" for market orders |
| `broker` | string | Broker code | Usually empty "" |
| `payType` | int | Payment type | Usually 0 |
| `cond` | int | Order condition | 0=ROD, 1=IOC, 2=FOK |

**Returns:**
- String: Order confirmation message or empty string on success

**Example:**
```python
# Buy 1000 shares of stock 2330 at limit price 500
result = tradeApp.Stock_NewOrder(
    accountID="1234567",
    tradeDate="20260121",
    TT=0,           # Regular trading
    OT=0,           # Cash order
    BS=1,           # Buy
    stockID="2330",
    qty="1000",
    PT=0,           # Limit price
    price="500",
    broker="",
    payType=0,
    cond=0          # ROD
)
```

#### `Stock_ModifyOrder()`

Modify an existing stock order.

**Signature:**
```python
Stock_ModifyOrder(accountID, tradeDate, TT, OT, OID, orderNumber, stockID, BS, qty, qCurrent, qMatch, preOrder, modifyType, price, PT, cond)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `accountID` | string | Account ID |
| `tradeDate` | string | Trading date (YYYYMMDD) |
| `TT` | int | Trade type |
| `OT` | int | Order type |
| `OID` | string | Original order ID |
| `orderNumber` | string | Order number |
| `stockID` | string | Stock symbol |
| `BS` | int | Buy/Sell (1=Buy, 2=Sell) |
| `qty` | int | New quantity (0 to keep unchanged) |
| `qCurrent` | int | Current remaining quantity |
| `qMatch` | int | Matched quantity |
| `preOrder` | int | Pre-order flag (0 or 1) |
| `modifyType` | int | Modification type (0=Quantity, 2=Price) |
| `price` | string | New price |
| `PT` | int | Price type |
| `cond` | int | Order condition |

**Example:**
```python
# Modify order quantity
result = tradeApp.Stock_ModifyOrder(
    accountID="1234567",
    tradeDate="20260121",
    TT=0,
    OT=0,
    OID="A001",
    orderNumber="12345",
    stockID="2330",
    BS=1,
    qty=2000,       # New quantity
    qCurrent=1000,  # Current quantity
    qMatch=0,       # Matched quantity
    preOrder=0,
    modifyType=0,   # Modify quantity
    price="500",
    PT=0,
    cond=0
)
```

#### `Stock_CancelOrder()`

Cancel an existing stock order.

**Signature:**
```python
Stock_CancelOrder(accountID, tradeDate, TT, OT, OID, orderNumber, stockID, BS, qty, qCurrent, qMatch, preOrder, price, PT, cond)
```

**Parameters:** Similar to `Stock_ModifyOrder()`

**Example:**
```python
result = tradeApp.Stock_CancelOrder(
    accountID="1234567",
    tradeDate="20260121",
    TT=0,
    OT=0,
    OID="A001",
    orderNumber="12345",
    stockID="2330",
    BS=1,
    qty=1000,
    qCurrent=1000,
    qMatch=0,
    preOrder=0,
    price="500",
    PT=0,
    cond=0
)
```

#### `Stock_QueryOrder()`

Query stock orders.

**Signature:**
```python
Stock_QueryOrder(accountID, forceQuery)
```

**Parameters:**
- `accountID` (string): Account ID
- `forceQuery` (int): 1 to force refresh, 0 to use cache

**Returns:**
- String: Query result or error message

#### `Stock_QueryMatch()`

Query stock trade matches.

**Signature:**
```python
Stock_QueryMatch(accountID, forceQuery)
```

#### `Stock_QueryPosition()`

Query stock positions.

**Signature:**
```python
Stock_QueryPosition(accountID, tradeDate, forceQuery)
```

**Parameters:**
- `accountID` (string): Account ID
- `tradeDate` (string): Trading date (YYYYMMDD)
- `forceQuery` (int): 1 to force refresh, 0 to use cache

---

### Futures & Options Trading

#### `FutOpt_NewOrder()`

Place a new futures or options order.

**Signature:**
```python
FutOpt_NewOrder(accountID, tradeDate, TT, tradeID1, BS1, PT, price, qty, offset, cond, tradeID2, BS2, preOrder)
```

**Parameters:**

| Parameter | Type | Description | Values |
|-----------|------|-------------|--------|
| `accountID` | string | Account ID | From GetAccount() |
| `tradeDate` | string | Trading date | Format: YYYYMMDD |
| `TT` | int | Product type | 0=Futures, 1=Options, 2=Complex options, 3=Complex futures |
| `tradeID1` | string | Contract ID | e.g., "TXFJ4" |
| `BS1` | int | Buy/Sell | 1=Buy, 2=Sell |
| `PT` | int | Price type | 0=Limit, 4=Market |
| `price` | string | Order price | "0" for market orders |
| `qty` | int | Quantity | Number of contracts |
| `offset` | int | Offset flag | 0=Open position, 1=Close position |
| `cond` | int | Order condition | 0=ROD, 1=IOC, 2=FOK |
| `tradeID2` | string | Second leg contract (for complex orders) | Usually "" |
| `BS2` | int | Second leg Buy/Sell | Usually 0 |
| `preOrder` | int | Pre-order flag | 0 or 1 |

**Example:**
```python
# Buy 1 lot of TX futures at market price
result = tradeApp.FutOpt_NewOrder(
    accountID="1234567",
    tradeDate="20260121",
    TT=0,           # Futures
    tradeID1="TXFJ4",
    BS1=1,          # Buy
    PT=4,           # Market price
    price="0",
    qty=1,
    offset=0,       # Open position
    cond=0,         # ROD
    tradeID2="",
    BS2=0,
    preOrder=0
)
```

#### `FutOpt_ModifyOrder()`

Modify an existing futures/options order.

**Signature:**
```python
FutOpt_ModifyOrder(accountID, type, tradeDate, OID, orderNo, qty, TT, qCurrent, qMatch, preOrder, newPT, newPrice, newCond, tradeID1, tradeID2)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `accountID` | string | Account ID |
| `type` | int | Modification type |
| `tradeDate` | string | Trading date (YYYYMMDD) |
| `OID` | string | Original order ID |
| `orderNo` | string | Order number |
| `qty` | int | New quantity |
| `TT` | int | Product type |
| `qCurrent` | int | Current remaining quantity |
| `qMatch` | int | Matched quantity |
| `preOrder` | int | Pre-order flag |
| `newPT` | int | New price type |
| `newPrice` | string | New price |
| `newCond` | int | New condition |
| `tradeID1` | string | Contract ID |
| `tradeID2` | string | Second leg contract |

#### `FutOpt_CancelOrder()`

Cancel an existing futures/options order.

**Signature:**
```python
FutOpt_CancelOrder(accountID, tradeDate, OID, orderNo, qty, TT, qCurrent, qMatch, preOrder, tradeID1, tradeID2)
```

#### `FutOpt_QueryOrder()`

Query futures/options orders.

**Signature:**
```python
FutOpt_QueryOrder(accountID, TT, forceQuery)
```

**Parameters:**
- `accountID` (string): Account ID
- `TT` (int): Product type (0=Futures, 1=Options)
- `forceQuery` (int): 1 to force refresh, 0 to use cache

#### `FutOpt_QueryMatch()`

Query futures/options trade matches.

**Signature:**
```python
FutOpt_QueryMatch(accountID, forceQuery)
```

#### `FutOpt_QueryOI()`

Query futures/options open interest.

**Signature:**
```python
FutOpt_QueryOI(accountID, tradeDate, forceQuery)
```

#### `FutOpt_QueryEquity()`

Query futures/options account equity.

**Signature:**
```python
FutOpt_QueryEquity(accountID, tradeDate)
```

**Parameters:**
- `accountID` (string): Account ID
- `tradeDate` (string): Trading date (YYYYMMDD) or "" for current

---

## Query Methods

All query methods follow a similar pattern and return results through the `OnDataResponse` event handler.

### Common Parameters

- `accountID`: The trading account ID
- `forceQuery`: 
  - `1` = Force query from server (latest data)
  - `0` = Use cached data if available

### Response Handling

Query results are delivered via the `OnDataResponse` callback with specific event IDs:

```python
def OnDataResponse(self, eventID, responseData):
    if eventID == 10:
        # Query result
        print(f"Query result: {responseData}")
    elif eventID == 100:
        # General message
        print(f"Message: {responseData}")
    elif eventID in [101, 102, 103]:
        # Order/Match/Position updates
        formatted = responseData.replace(">", ">\n")
        print(formatted)
```

---

## Code Examples

### Complete Trading Application

```python
import win32com.client
import json
import datetime

class TradingApp:
    def __init__(self):
        self.tradeApp = None
        self.connected = False
        self.logged_in = False
        
    def initialize(self):
        """Initialize the trading application"""
        # Create COM object with event handler
        self.tradeApp = win32com.client.Dispatch("DJTRADEOBJLibCTS.TradeApp")
        self.tradeApp.OnDataResponse = self.on_data_response
        
        # Load configuration
        with open('appsetting.json', 'r') as f:
            config = json.load(f)
        
        # Initialize
        (ret, errCode, errMsg) = self.tradeApp.Init(config["TradeDas"])
        
        if ret != 1:
            raise Exception(f"Init failed: {errMsg}")
        
        # Configure settings
        self.tradeApp.SetEchoType(1, 1)
        self.tradeApp.SetLotSizeData("0050=1000|0028=1000")
        
        print("Trading app initialized")
        
    def on_data_response(self, eventID, responseData):
        """Handle data responses"""
        if eventID == 1:
            print(f"Connection status changed: {responseData}")
        elif eventID == 10:
            print(f"Query result: {responseData}")
        elif eventID == 100:
            print(f"Message: {responseData}")
        elif eventID in [101, 102, 103]:
            print(f"Order update: {responseData}")
    
    def login(self, user_id, password):
        """Login to trading system"""
        (result, errCode, errMsg) = self.tradeApp.Login(user_id, password)
        
        if result == 1:
            self.logged_in = True
            print("Login successful")
            self.print_accounts()
            return True
        else:
            print(f"Login failed: {errMsg}")
            return False
    
    def connect(self):
        """Connect to trading server"""
        result = self.tradeApp.Connect()
        
        if result != 0:
            self.connected = True
            print("Connected to trading server")
            return True
        else:
            print("Connection failed")
            return False
    
    def print_accounts(self):
        """Print all available accounts"""
        count = self.tradeApp.GetAccountCount()
        print(f"\nFound {count} accounts:")
        
        for i in range(count):
            account_data = self.tradeApp.GetAccount(i)
            print(f"  {account_data}")
    
    def buy_stock(self, account_id, stock_id, qty, price):
        """Buy stock at limit price"""
        today = datetime.date.today().strftime('%Y%m%d')
        
        result = self.tradeApp.Stock_NewOrder(
            account_id,
            today,
            0,          # Regular trading
            0,          # Cash order
            1,          # Buy
            stock_id,
            str(qty),
            0,          # Limit price
            str(price),
            "",         # No broker
            0,          # Default pay type
            0           # ROD
        )
        
        if result:
            print(f"Order error: {result}")
        else:
            print(f"Buy order placed: {stock_id} x {qty} @ {price}")
    
    def query_positions(self, account_id):
        """Query current stock positions"""
        today = datetime.date.today().strftime('%Y%m%d')
        
        result = self.tradeApp.Stock_QueryPosition(account_id, today, 1)
        
        if result:
            print(f"Query error: {result}")
    
    def cleanup(self):
        """Cleanup and disconnect"""
        if self.connected:
            self.tradeApp.Disconnect()
        if self.logged_in:
            self.tradeApp.Logout("")
        self.tradeApp.Fini()
        print("Cleanup complete")

# Usage example
if __name__ == "__main__":
    app = TradingApp()
    
    try:
        # Initialize
        app.initialize()
        
        # Login
        app.login("your_user_id", "your_password")
        
        # Connect
        app.connect()
        
        # Place an order
        app.buy_stock("1234567", "2330", 1000, 500)
        
        # Query positions
        app.query_positions("1234567")
        
        # Keep application running to receive callbacks
        input("Press Enter to exit...")
        
    finally:
        app.cleanup()
```

### Placing Market Orders

```python
def place_market_order(tradeApp, account_id, stock_id, qty, buy_sell):
    """
    Place a market order for stocks
    
    Args:
        tradeApp: TradeApp COM object
        account_id: Account ID string
        stock_id: Stock symbol
        qty: Quantity to trade
        buy_sell: 1 for buy, 2 for sell
    """
    today = datetime.date.today().strftime('%Y%m%d')
    
    result = tradeApp.Stock_NewOrder(
        account_id,
        today,
        0,          # Regular trading
        0,          # Cash order
        buy_sell,   # Buy or Sell
        stock_id,
        str(qty),
        4,          # Market price
        "0",        # Price ignored for market orders
        "",
        0,
        0           # ROD
    )
    
    return result
```

### Query All Orders

```python
def query_all_orders(tradeApp, stock_account, futures_account):
    """Query orders for both stock and futures accounts"""
    
    print("Querying stock orders...")
    result = tradeApp.Stock_QueryOrder(stock_account, 1)
    if result:
        print(f"Stock query error: {result}")
    
    print("Querying futures orders...")
    result = tradeApp.FutOpt_QueryOrder(futures_account, 0, 1)
    if result:
        print(f"Futures query error: {result}")
```

---

## Error Handling

### Common Error Patterns

1. **Initialization Errors**
   - Invalid DAS URL
   - Network connectivity issues
   - COM object registration issues

2. **Authentication Errors**
   - Invalid credentials
   - Account not authorized
   - Session expired

3. **Order Errors**
   - Invalid stock/contract ID
   - Insufficient buying power
   - Market closed
   - Invalid price or quantity

### Error Handling Best Practices

```python
def safe_order(tradeApp, account_id, stock_id, qty, price):
    """Place order with comprehensive error handling"""
    
    try:
        # Validate inputs
        if not stock_id or not stock_id.strip():
            raise ValueError("Stock ID cannot be empty")
        
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        # Place order
        today = datetime.date.today().strftime('%Y%m%d')
        
        result = tradeApp.Stock_NewOrder(
            account_id, today, 0, 0, 1,
            stock_id, str(qty), 0, str(price),
            "", 0, 0
        )
        
        if result:
            # API returned error message
            print(f"Order failed: {result}")
            return False
        else:
            print("Order placed successfully")
            return True
            
    except ValueError as ve:
        print(f"Validation error: {ve}")
        return False
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        return False
```

### Handling Async Responses

```python
import threading
import queue

class AsyncTradeApp:
    def __init__(self):
        self.response_queue = queue.Queue()
        self.tradeApp = win32com.client.Dispatch("DJTRADEOBJLibCTS.TradeApp")
        self.tradeApp.OnDataResponse = self.on_data_response
    
    def on_data_response(self, eventID, responseData):
        """Queue responses for async processing"""
        self.response_queue.put((eventID, responseData))
    
    def process_responses(self):
        """Process responses in separate thread"""
        while True:
            try:
                eventID, data = self.response_queue.get(timeout=1)
                self.handle_response(eventID, data)
            except queue.Empty:
                continue
    
    def handle_response(self, eventID, data):
        """Handle different response types"""
        if eventID == 10:
            print(f"Query result: {data}")
        elif eventID == 100:
            print(f"Message: {data}")
        # ... handle other event types
```

---

## Best Practices

### 1. **Always Initialize Properly**

```python
# Good practice
def init_trading_app():
    tradeApp = win32com.client.Dispatch("DJTRADEOBJLibCTS.TradeApp")
    
    with open('appsetting.json', 'r') as f:
        config = json.load(f)
    
    (ret, errCode, errMsg) = tradeApp.Init(config["TradeDas"])
    
    if ret != 1:
        raise Exception(f"Initialization failed: {errMsg}")
    
    tradeApp.SetEchoType(1, 1)
    return tradeApp
```

### 2. **Use Context Managers**

```python
class TradingContext:
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password
        self.tradeApp = None
    
    def __enter__(self):
        self.tradeApp = init_trading_app()
        (result, _, errMsg) = self.tradeApp.Login(self.user_id, self.password)
        
        if result != 1:
            raise Exception(f"Login failed: {errMsg}")
        
        self.tradeApp.Connect()
        return self.tradeApp
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tradeApp:
            self.tradeApp.Disconnect()
            self.tradeApp.Logout(self.user_id)
            self.tradeApp.Fini()

# Usage
with TradingContext("user_id", "password") as app:
    # Place orders, query data, etc.
    app.Stock_QueryPosition("account_id", "20260121", 1)
```

### 3. **Cache Account Information**

```python
class AccountManager:
    def __init__(self, tradeApp):
        self.tradeApp = tradeApp
        self.accounts = {}
        self.load_accounts()
    
    def load_accounts(self):
        """Load and cache all accounts"""
        count = self.tradeApp.GetAccountCount()
        
        for i in range(count):
            account_data = self.tradeApp.GetAccount(i).strip('<>')
            fields = dict(f.split("=") for f in account_data.split("|") if "=" in f)
            
            account_type = fields.get("AccType", "")
            account_id = fields.get("AccID", "")
            
            if account_type == "1":
                self.accounts["stock"] = account_id
            elif account_type == "2":
                self.accounts["futures"] = account_id
    
    def get_stock_account(self):
        return self.accounts.get("stock")
    
    def get_futures_account(self):
        return self.accounts.get("futures")
```

### 4. **Validate Before Trading**

```python
def validate_stock_order(stock_id, qty, price, price_type):
    """Validate order parameters before submission"""
    
    errors = []
    
    # Validate stock ID
    if not stock_id or not stock_id.strip():
        errors.append("Stock ID is required")
    
    # Validate quantity
    if qty <= 0:
        errors.append("Quantity must be positive")
    
    # Validate price for limit orders
    if price_type == 0 and price <= 0:
        errors.append("Price must be positive for limit orders")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return True
```

### 5. **Log All Trading Activity**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)

def logged_order(tradeApp, account_id, stock_id, qty, price):
    """Place order with logging"""
    
    logging.info(f"Placing order: {stock_id} x {qty} @ {price}")
    
    today = datetime.date.today().strftime('%Y%m%d')
    
    result = tradeApp.Stock_NewOrder(
        account_id, today, 0, 0, 1,
        stock_id, str(qty), 0, str(price),
        "", 0, 0
    )
    
    if result:
        logging.error(f"Order failed: {result}")
    else:
        logging.info(f"Order placed successfully")
    
    return result
```

### 6. **Use Proper Cleanup**

```python
def cleanup_trading_app(tradeApp, user_id):
    """Properly cleanup trading application"""
    
    try:
        # Disconnect from trading server
        tradeApp.Disconnect()
        logging.info("Disconnected from trading server")
    except Exception as e:
        logging.error(f"Error during disconnect: {e}")
    
    try:
        # Logout
        tradeApp.Logout(user_id)
        logging.info("Logged out successfully")
    except Exception as e:
        logging.error(f"Error during logout: {e}")
    
    try:
        # Finalize
        tradeApp.Fini()
        logging.info("Trading app finalized")
    except Exception as e:
        logging.error(f"Error during finalization: {e}")
```

---

## Appendix

### Enumeration Values

#### Trade Type (TT) - Stock

| Value | Description |
|-------|-------------|
| 0 | Regular trading |
| 1 | After-hours odd lot |
| 2 | After-hours |
| 5 | Emerging stock |
| 7 | Intraday odd lot |

#### Order Type (OT) - Stock

| Value | Description |
|-------|-------------|
| 0 | Cash |
| 1 | Margin |
| 2 | Short |
| 16 | Day trading sell first |

#### Buy/Sell (BS)

| Value | Description |
|-------|-------------|
| 1 | Buy |
| 2 | Sell |

#### Price Type (PT)

| Value | Description |
|-------|-------------|
| 0 | Limit price |
| 1 | Limit up |
| 2 | Limit down |
| 3 | Flat |
| 4 | Market price |

#### Order Condition (Cond)

| Value | Description |
|-------|-------------|
| 0 | ROD (Rest of Day) |
| 1 | IOC (Immediate or Cancel) |
| 2 | FOK (Fill or Kill) |

#### Product Type (TT) - Futures/Options

| Value | Description |
|-------|-------------|
| 0 | Futures |
| 1 | Options |
| 2 | Complex options |
| 3 | Complex futures |

#### Account Type

| Value | Description |
|-------|-------------|
| 1 | Stock |
| 2 | Futures/Options |
| 3 | International (HK/US) |

---

## Support and Resources

### Contact Information

For technical support and API questions, contact CTBC Securities technical support team.

### Additional Resources

- Python win32com documentation: [pywin32 docs](https://github.com/mhammond/pywin32)
- PyQt5 documentation: [PyQt5 docs](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

---

## License

This guidebook is provided for reference purposes. Please refer to your CTBC Securities API license agreement for terms of use.

---

**Document Version**: 1.0  
**Last Updated**: January 21, 2026  
**Author**: Generated from CTS Trading API Python Reference Implementation
