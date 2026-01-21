# CTS Trading API MCP Server

A Model Context Protocol (MCP) server providing comprehensive access to CTBC Securities CTS Trading API. Enables LLMs like Claude to interact with the trading platform for stock, futures, and options trading operations.

## Features

- **Stock Trading**: Place, modify, and cancel stock orders
- **Futures/Options Trading**: Full support for derivatives trading
- **Account Management**: Query accounts, positions, orders, and matches
- **Type-Safe**: Comprehensive Pydantic models for all operations
- **Event-Driven**: Async response handling for query operations
- **MCP Resources**: Access to configuration and connection status

## Requirements

- **Operating System**: Windows (COM object dependency)
- **Python**: 3.10 or higher
- **CTS Trading API**: Must be installed and registered on the system
- **Dependencies**: 
  - `mcp >= 1.1.0`
  - `pywin32 >= 306`
  - `pydantic >= 2.0`

## Installation

1. **Clone or download the repository**

2. **Install CTS Trading API** (from CTBC Securities)
   - Ensure the `DJTRADEOBJLibCTS.TradeApp` COM object is registered

3. **Install Python dependencies**
   ```bash
   # Using uv (recommended)
   uv pip install -e .
   
   # Or using pip
   pip install -e .
   ```

4. **Configure the server**
   
   Edit `appsetting.json` with your trading server endpoint:
   ```json
   {
     "TradeDas": "your.trading.server.com/tradedas"
   }
   ```

## Usage

### Testing with MCP Inspector

Test the server using the MCP development tools:

```bash
uv run mcp dev d:\ctbcsec-api-mcp-server\ctbcsec_mcp\server.py
```

This launches the MCP Inspector where you can:
- View all available tools
- Test tool schemas
- Execute tools interactively
- Monitor responses

### Integration with Claude Desktop

Install the server to Claude Desktop:

```bash
uv run mcp install d:\ctbcsec-api-mcp-server\ctbcsec_mcp\server.py
```

Or manually add to Claude Desktop configuration (`%APPDATA%\Claude\claude_desktop_config.json`):

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

## Available Tools

### Authentication & Connection

- **`initialize`**: Initialize the CTS Trading API with server configuration
- **`login`**: Authenticate user with trading system
- **`connect`**: Connect to the trading server
- **`disconnect`**: Disconnect from trading server
- **`logout`**: Logout from trading system
- **`get_accounts`**: Retrieve all available trading accounts
- **`get_connection_status`**: Get current connection status
- **`set_lot_size`**: Set lot size data for specific stocks

### Stock Trading

- **`stock_new_order`**: Place a new stock order
- **`stock_modify_order`**: Modify an existing stock order
- **`stock_cancel_order`**: Cancel an existing stock order
- **`stock_query_order`**: Query stock orders
- **`stock_query_match`**: Query stock trade matches
- **`stock_query_position`**: Query stock positions

### Futures/Options Trading

- **`futopt_new_order`**: Place a new futures/options order
- **`futopt_modify_order`**: Modify an existing futures/options order
- **`futopt_cancel_order`**: Cancel an existing futures/options order
- **`futopt_query_order`**: Query futures/options orders
- **`futopt_query_match`**: Query futures/options matches
- **`futopt_query_oi`**: Query futures/options open interest
- **`futopt_query_equity`**: Query futures/options account equity

## Resources

- **`config://appsetting`**: Current server configuration
- **`status://connection`**: Current connection and authentication status

## Example Usage Flow

```python
# 1. Initialize the trading API
initialize(trade_das_url="apsit.ectest.ctbcsec.com/tradedas")

# 2. Login
login(user_id="your_user_id", password="your_password")

# 3. Connect to trading server
connect()

# 4. Get available accounts
accounts = get_accounts()

# 5. Place a stock order
stock_new_order(
    account_id="1234567",
    stock_id="2330",
    quantity="1000",
    price="500",
    buy_sell=BuySell.BUY,
    price_type=PriceType.LIMIT
)

# 6. Query positions
stock_query_position(account_id="1234567")

# 7. Cleanup
disconnect()
logout(user_id="your_user_id")
```

## Enumerations

### TradeType (Stock)
- `REGULAR = 0`: Regular trading
- `AFTER_HOURS_ODD_LOT = 1`: After-hours odd lot
- `AFTER_HOURS = 2`: After-hours
- `EMERGING = 5`: Emerging stock
- `INTRADAY_ODD_LOT = 7`: Intraday odd lot

### OrderType (Stock)
- `CASH = 0`: Cash order
- `MARGIN = 1`: Margin trading
- `SHORT = 2`: Short selling
- `DAY_TRADING_SELL_FIRST = 16`: Day trading sell first

### BuySell
- `BUY = 1`: Buy order
- `SELL = 2`: Sell order

### PriceType
- `LIMIT = 0`: Limit price
- `LIMIT_UP = 1`: Limit up
- `LIMIT_DOWN = 2`: Limit down
- `FLAT = 3`: Flat
- `MARKET = 4`: Market price

### OrderCondition
- `ROD = 0`: Rest of Day
- `IOC = 1`: Immediate or Cancel
- `FOK = 2`: Fill or Kill

### ProductType (Futures/Options)
- `FUTURES = 0`: Futures
- `OPTIONS = 1`: Options
- `COMPLEX_OPTIONS = 2`: Complex options
- `COMPLEX_FUTURES = 3`: Complex futures

## Architecture

### Components

- **`server.py`**: FastMCP server with tool definitions and lifespan management
- **`models.py`**: Pydantic models for type-safe structured data
- **`wrapper.py`**: COM object wrapper with event handling and thread safety
- **`__init__.py`**: Package initialization

### Data Flow

1. MCP tool receives request with typed parameters
2. Server validates input using Pydantic models
3. Wrapper executes COM object method with thread safety
4. Event handler queues async responses
5. Structured response returned to LLM

### Thread Safety

The wrapper uses locks to ensure thread-safe access to the COM object, which is critical for concurrent operations.

### Event Handling

Query operations use an event-driven architecture:
- Responses arrive via `OnDataResponse` callback
- Events are queued for async processing
- Tools wait for responses with configurable timeout

## Troubleshooting

### COM Object Not Found

**Error**: "Failed to create COM object"

**Solution**: Ensure CTS Trading API is installed and the COM object is registered. Run the CTS Trading client once to verify installation.

### Connection Failures

**Error**: "Not connected to trading server"

**Solution**: 
1. Verify `appsetting.json` has correct server URL
2. Call `initialize()` before `login()`
3. Call `login()` before `connect()`
4. Check network connectivity

### Query Timeout

**Note**: Query operations may timeout if the server is slow to respond. The default timeout is 5 seconds. This is normal for some operations.

### Permission Errors

Ensure you have proper trading permissions and account authorization from CTBC Securities.

## Development

### Running Automated Tests

The project includes a comprehensive suite of automated tests using `pytest` and `mock`.

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run all tests
pytest
```

The tests cover:
- **Models**: Validation and serialization of all data structures.
- **Wrapper**: Logic for COM object interaction (using mocks).
- **Server**: Tool registration and high-level logic.

### Manual Testing with Scripts

### Logging

The server uses Python's logging module. Set log level via environment variable:

```bash
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"
uv run ctbcsec-mcp

# Windows CMD
set LOG_LEVEL=DEBUG
uv run ctbcsec-mcp
```

## Security Considerations

- **Credentials**: Never commit credentials to version control
- **Production Use**: Use appropriate authentication and authorization
- **Network Security**: Ensure secure connection to trading server
- **Access Control**: Restrict access to the MCP server appropriately

## License

This MCP server is provided for reference and development purposes. Please refer to your CTBC Securities API license agreement for terms of use.

## Support

For technical support and API questions, contact CTBC Securities technical support team.

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [CTS API Guidebook](./CTS-API-GUIDEBOOK.md)

---

**Version**: 0.1.0  
**Last Updated**: January 21, 2026
