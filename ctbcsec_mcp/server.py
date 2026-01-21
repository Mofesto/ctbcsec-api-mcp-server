"""
CTS Trading API MCP Server

FastMCP server providing tools for CTBC Securities CTS Trading API.
Supports stock and futures/options trading operations.
"""

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Handle imports for both module and standalone execution
try:
    from .models import (
        AccountInfo,
        ConnectionStatus,
        InitResponse,
        LoginResponse,
        OrderResponse,
        QueryResult,
        TradeType,
        OrderType,
        BuySell,
        PriceType,
        OrderCondition,
        ProductType,
    )
    from .wrapper import TradeAppWrapper
except ImportError:
    from ctbcsec_mcp.models import (
        AccountInfo,
        ConnectionStatus,
        InitResponse,
        LoginResponse,
        OrderResponse,
        QueryResult,
        TradeType,
        OrderType,
        BuySell,
        PriceType,
        OrderCondition,
        ProductType,
    )
    from ctbcsec_mcp.wrapper import TradeAppWrapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("ctbcsec-trading-api")

# Global trading app wrapper instance
trade_wrapper: Optional[TradeAppWrapper] = None


def _initialize_wrapper():
    """Initialize the trading wrapper if not already done."""
    global trade_wrapper
    if trade_wrapper is None:
        trade_wrapper = TradeAppWrapper()
        try:
            trade_wrapper.create_com_object()
            logger.info("COM object initialized")
        except Exception as e:
            logger.error(f"Failed to initialize COM object: {e}")
            logger.warning("Server will continue but trading operations will fail until COM object is available")


# ============================================================================
# Resources
# ============================================================================

@mcp.resource("config://appsetting")
def get_config_resource() -> str:
    """Get current server configuration from appsetting.json if it exists."""
    config_path = Path("appsetting.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return json.dumps(config, indent=2)
    else:
        return json.dumps({
            "note": "Configuration file not found",
            "expected_path": str(config_path.absolute()),
            "template": {
                "TradeDas": "apsit.ectest.ctbcsec.com/tradedas"
            }
        }, indent=2)


@mcp.resource("status://connection")
def get_status_resource() -> str:
    """Get current connection and authentication status."""
    if trade_wrapper:
        status = trade_wrapper.get_status()
        return status.model_dump_json(indent=2)
    else:
        return json.dumps({
            "error": "Trading wrapper not initialized"
        }, indent=2)


# ============================================================================
# Authentication & Connection Tools
# ============================================================================

@mcp.tool()
def initialize(trade_das_url: str) -> InitResponse:
    """
    Initialize the CTS Trading API with server configuration.
    
    Args:
        trade_das_url: Trading DAS server endpoint (e.g., "apsit.ectest.ctbcsec.com/tradedas")
    
    Returns:
        Initialization result with success status and error details
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return InitResponse(
            success=False,
            error_code=-1,
            error_message="Trading wrapper not initialized"
        )
    
    try:
        result, err_code, err_msg = trade_wrapper.init(trade_das_url)
        
        return InitResponse(
            success=(result == 1),
            error_code=err_code,
            error_message=err_msg if result != 1 else "Initialization successful"
        )
    except Exception as e:
        logger.error(f"Initialize error: {e}")
        return InitResponse(
            success=False,
            error_code=-1,
            error_message=str(e)
        )


@mcp.tool()
def set_lot_size(lot_size_data: str) -> OrderResponse:
    """
    Set lot size data for specific stocks.
    
    Args:
        lot_size_data: Lot size configuration (e.g., "0050=1000|0028=1000")
    
    Returns:
        Operation result
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    try:
        trade_wrapper.set_lot_size_data(lot_size_data)
        return OrderResponse(success=True, message=f"Lot size data set: {lot_size_data}")
    except Exception as e:
        logger.error(f"Set lot size error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def login(user_id: str, password: str) -> LoginResponse:
    """
    Authenticate user with the trading system.
    
    Args:
        user_id: User account ID
        password: User password
    
    Returns:
        Login result with account information
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return LoginResponse(
            success=False,
            error_code=-1,
            error_message="Trading wrapper not initialized"
        )
    
    try:
        result, err_code, err_msg = trade_wrapper.login(user_id, password)
        
        if result == 1:
            # Get accounts
            accounts = trade_wrapper.get_accounts()
            return LoginResponse(
                success=True,
                error_code=0,
                error_message="Login successful",
                accounts=accounts
            )
        else:
            return LoginResponse(
                success=False,
                error_code=err_code,
                error_message=err_msg
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return LoginResponse(
            success=False,
            error_code=-1,
            error_message=str(e)
        )


@mcp.tool()
def connect() -> OrderResponse:
    """
    Connect to the trading server.
    
    Returns:
        Connection status
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    try:
        result = trade_wrapper.connect()
        if result != 0:
            return OrderResponse(success=True, message="Connected to trading server")
        else:
            return OrderResponse(success=False, message="Connection failed")
    except Exception as e:
        logger.error(f"Connect error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def disconnect() -> OrderResponse:
    """
    Disconnect from the trading server.
    
    Returns:
        Status confirmation
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    try:
        trade_wrapper.disconnect()
        return OrderResponse(success=True, message="Disconnected from trading server")
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def logout(user_id: str) -> OrderResponse:
    """
    Logout from the trading system.
    
    Args:
        user_id: User account ID
    
    Returns:
        Logout confirmation
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    try:
        trade_wrapper.logout(user_id)
        return OrderResponse(success=True, message="Logged out successfully")
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def get_accounts() -> list[AccountInfo]:
    """
    Retrieve all available trading accounts.
    
    Returns:
        List of account information objects
    """
    _initialize_wrapper()
    if not trade_wrapper:
        raise RuntimeError("Trading wrapper not initialized")
    
    try:
        accounts = trade_wrapper.get_accounts()
        return accounts
    except Exception as e:
        logger.error(f"Get accounts error: {e}")
        raise


@mcp.tool()
def get_connection_status() -> ConnectionStatus:
    """
    Get current connection and authentication status.
    
    Returns:
        Current connection status
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return ConnectionStatus()
    
    return trade_wrapper.get_status()


# ============================================================================
# Stock Trading Tools
# ============================================================================

@mcp.tool()
def stock_new_order(
    account_id: str,
    stock_id: str,
    quantity: str,
    price: str,
    buy_sell: BuySell,
    trade_date: Optional[str] = None,
    trade_type: TradeType = TradeType.REGULAR,
    order_type: OrderType = OrderType.CASH,
    price_type: PriceType = PriceType.LIMIT,
    condition: OrderCondition = OrderCondition.ROD,
    broker: str = "",
    pay_type: int = 0
) -> OrderResponse:
    """
    Place a new stock order.
    
    Args:
        account_id: Account ID
        stock_id: Stock symbol (e.g., "2330")
        quantity: Number of shares
        price: Order price ("0" for market orders)
        buy_sell: Buy (1) or Sell (2)
        trade_date: Trading date in YYYYMMDD format (defaults to today)
        trade_type: Trade type (default: REGULAR)
        order_type: Order type (default: CASH)
        price_type: Price type (default: LIMIT)
        condition: Order condition (default: ROD)
        broker: Broker code (default: empty)
        pay_type: Payment type (default: 0)
    
    Returns:
        Order confirmation or error message
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    # Default to today if no trade date provided
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.stock_new_order(
            account_id, trade_date, int(trade_type), int(order_type),
            int(buy_sell), stock_id, quantity, int(price_type), price,
            broker, pay_type, int(condition)
        )
        
        if not result:
            return OrderResponse(
                success=True,
                message=f"Stock order placed: {stock_id} x {quantity} @ {price}"
            )
        else:
            return OrderResponse(success=False, message=result)
            
    except Exception as e:
        logger.error(f"Stock new order error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def stock_modify_order(
    account_id: str,
    order_id: str,
    order_number: str,
    stock_id: str,
    buy_sell: BuySell,
    current_quantity: int,
    matched_quantity: int,
    new_price: str,
    trade_date: Optional[str] = None,
    new_quantity: int = 0,
    trade_type: TradeType = TradeType.REGULAR,
    order_type: OrderType = OrderType.CASH,
    price_type: PriceType = PriceType.LIMIT,
    condition: OrderCondition = OrderCondition.ROD,
    modify_type: int = 2,  # Default to price modification
    pre_order: int = 0
) -> OrderResponse:
    """
    Modify an existing stock order.
    
    Args:
        account_id: Account ID
        order_id: Original order ID
        order_number: Order number
        stock_id: Stock symbol
        buy_sell: Buy (1) or Sell (2)
        current_quantity: Current remaining quantity
        matched_quantity: Matched quantity
        new_price: New price
        trade_date: Trading date (defaults to today)
        new_quantity: New quantity (0 to keep unchanged)
        trade_type: Trade type
        order_type: Order type
        price_type: Price type
        condition: Order condition
        modify_type: Modification type (0=Quantity, 2=Price)
        pre_order: Pre-order flag
    
    Returns:
        Modification result
    """
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.stock_modify_order(
            account_id, trade_date, int(trade_type), int(order_type),
            order_id, order_number, stock_id, int(buy_sell),
            new_quantity, current_quantity, matched_quantity, pre_order,
            modify_type, new_price, int(price_type), int(condition)
        )
        
        if not result:
            return OrderResponse(success=True, message=f"Order {order_id} modified successfully")
        else:
            return OrderResponse(success=False, message=result)
            
    except Exception as e:
        logger.error(f"Stock modify order error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def stock_cancel_order(
    account_id: str,
    order_id: str,
    order_number: str,
    stock_id: str,
    buy_sell: BuySell,
    quantity: int,
    current_quantity: int,
    matched_quantity: int,
    price: str,
    trade_date: Optional[str] = None,
    trade_type: TradeType = TradeType.REGULAR,
    order_type: OrderType = OrderType.CASH,
    price_type: PriceType = PriceType.LIMIT,
    condition: OrderCondition = OrderCondition.ROD,
    pre_order: int = 0
) -> OrderResponse:
    """
    Cancel an existing stock order.
    
    Args:
        account_id: Account ID
        order_id: Original order ID
        order_number: Order number
        stock_id: Stock symbol
        buy_sell: Buy (1) or Sell (2)
        quantity: Order quantity
        current_quantity: Current remaining quantity
        matched_quantity: Matched quantity
        price: Order price
        trade_date: Trading date (defaults to today)
        trade_type: Trade type
        order_type: Order type
        price_type: Price type
        condition: Order condition
        pre_order: Pre-order flag
    
    Returns:
        Cancellation confirmation
    """
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.stock_cancel_order(
            account_id, trade_date, int(trade_type), int(order_type),
            order_id, order_number, stock_id, int(buy_sell),
            quantity, current_quantity, matched_quantity, pre_order,
            price, int(price_type), int(condition)
        )
        
        if not result:
            return OrderResponse(success=True, message=f"Order {order_id} cancelled successfully")
        else:
            return OrderResponse(success=False, message=result)
            
    except Exception as e:
        logger.error(f"Stock cancel order error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def stock_query_order(account_id: str, force_query: bool = True) -> QueryResult:
    """
    Query stock orders.
    
    Args:
        account_id: Account ID
        force_query: True to force refresh from server, False to use cache
    
    Returns:
        List of current orders
    """
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    try:
        result = trade_wrapper.stock_query_order(account_id, 1 if force_query else 0)
        
        # Wait for response from event queue
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(
                success=True,
                message="Query completed",
                data=data,
                event_id=event_id
            )
        else:
            return QueryResult(
                success=True,
                message="Query submitted (no response received within timeout)",
                data=result if result else "Query initiated"
            )
            
    except Exception as e:
        logger.error(f"Stock query order error: {e}")
        return QueryResult(success=False, message=str(e))


@mcp.tool()
def stock_query_match(account_id: str, force_query: bool = True) -> QueryResult:
    """
    Query stock trade matches.
    
    Args:
        account_id: Account ID
        force_query: True to force refresh from server, False to use cache
    
    Returns:
        List of matched trades
    """
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    try:
        result = trade_wrapper.stock_query_match(account_id, 1 if force_query else 0)
        
        # Wait for response
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(success=True, message="Query completed", data=data, event_id=event_id)
        else:
            return QueryResult(success=True, message="Query submitted", data=result if result else "Query initiated")
            
    except Exception as e:
        logger.error(f"Stock query match error: {e}")
        return QueryResult(success=False, message=str(e))


@mcp.tool()
def stock_query_position(
    account_id: str,
    trade_date: Optional[str] = None,
    force_query: bool = True
) -> QueryResult:
    """
    Query stock positions.
    
    Args:
        account_id: Account ID
        trade_date: Trading date in YYYYMMDD format (defaults to today)
        force_query: True to force refresh from server, False to use cache
    
    Returns:
        Current positions with P&L data
    """
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.stock_query_position(account_id, trade_date, 1 if force_query else 0)
        
        # Wait for response
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(success=True, message="Query completed", data=data, event_id=event_id)
        else:
            return QueryResult(success=True, message="Query submitted", data=result if result else "Query initiated")
            
    except Exception as e:
        logger.error(f"Stock query position error: {e}")
        return QueryResult(success=False, message=str(e))


# ============================================================================
# Futures/Options Trading Tools
# ============================================================================

@mcp.tool()
def futopt_new_order(
    account_id: str,
    contract_id: str,
    quantity: int,
    price: str,
    buy_sell: BuySell,
    product_type: ProductType = ProductType.FUTURES,
    trade_date: Optional[str] = None,
    price_type: PriceType = PriceType.LIMIT,
    offset: int = 0,
    condition: OrderCondition = OrderCondition.ROD,
    contract_id2: str = "",
    buy_sell2: int = 0,
    pre_order: int = 0
) -> OrderResponse:
    """
    Place a new futures or options order.
    
    Args:
        account_id: Account ID
        contract_id: Contract ID (e.g., "TXFJ4")
        quantity: Number of contracts
        price: Order price ("0" for market orders)
        buy_sell: Buy (1) or Sell (2)
        product_type: Product type (0=Futures, 1=Options)
        trade_date: Trading date (defaults to today)
        price_type: Price type (default: LIMIT)
        offset: Offset flag (0=Open, 1=Close)
        condition: Order condition (default: ROD)
        contract_id2: Second leg contract ID for complex orders
        buy_sell2: Second leg buy/sell
        pre_order: Pre-order flag
    
    Returns:
        Order confirmation
    """
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.futopt_new_order(
            account_id, trade_date, int(product_type),
            contract_id, int(buy_sell), int(price_type), price, quantity,
            offset, int(condition), contract_id2, buy_sell2, pre_order
        )
        
        if not result:
            return OrderResponse(success=True, message=f"FutOpt order placed: {contract_id} x {quantity}")
        else:
            return OrderResponse(success=False, message=result)
            
    except Exception as e:
        logger.error(f"FutOpt new order error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def futopt_modify_order(
    account_id: str,
    order_id: str,
    order_number: str,
    contract_id: str,
    new_quantity: int,
    current_quantity: int,
    matched_quantity: int,
    new_price: str,
    product_type: ProductType = ProductType.FUTURES,
    trade_date: Optional[str] = None,
    modify_type: int = 2,
    price_type: PriceType = PriceType.LIMIT,
    condition: OrderCondition = OrderCondition.ROD,
    contract_id2: str = "",
    pre_order: int = 0
) -> OrderResponse:
    """
    Modify an existing futures/options order.
    
    Args:
        account_id: Account ID
        order_id: Original order ID
        order_number: Order number
        contract_id: Contract ID
        new_quantity: New quantity
        current_quantity: Current remaining quantity
        matched_quantity: Matched quantity
        new_price: New price
        product_type: Product type
        trade_date: Trading date (defaults to today)
        modify_type: Modification type
        price_type: Price type
        condition: Order condition
        contract_id2: Second leg contract ID
        pre_order: Pre-order flag
    
    Returns:
        Modification result
    """
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.futopt_modify_order(
            account_id, modify_type, trade_date, order_id, order_number,
            new_quantity, int(product_type), current_quantity, matched_quantity,
            pre_order, int(price_type), new_price, int(condition),
            contract_id, contract_id2
        )
        
        if not result:
            return OrderResponse(success=True, message=f"FutOpt order {order_id} modified")
        else:
            return OrderResponse(success=False, message=result)
            
    except Exception as e:
        logger.error(f"FutOpt modify order error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def futopt_cancel_order(
    account_id: str,
    order_id: str,
    order_number: str,
    contract_id: str,
    quantity: int,
    current_quantity: int,
    matched_quantity: int,
    product_type: ProductType = ProductType.FUTURES,
    trade_date: Optional[str] = None,
    contract_id2: str = "",
    pre_order: int = 0
) -> OrderResponse:
    """
    Cancel an existing futures/options order.
    
    Args:
        account_id: Account ID
        order_id: Original order ID
        order_number: Order number
        contract_id: Contract ID
        quantity: Order quantity
        current_quantity: Current remaining quantity
        matched_quantity: Matched quantity
        product_type: Product type
        trade_date: Trading date (defaults to today)
        contract_id2: Second leg contract ID
        pre_order: Pre-order flag
    
    Returns:
        Cancellation confirmation
    """
    if not trade_wrapper:
        return OrderResponse(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.futopt_cancel_order(
            account_id, trade_date, order_id, order_number, quantity,
            int(product_type), current_quantity, matched_quantity,
            pre_order, contract_id, contract_id2
        )
        
        if not result:
            return OrderResponse(success=True, message=f"FutOpt order {order_id} cancelled")
        else:
            return OrderResponse(success=False, message=result)
            
    except Exception as e:
        logger.error(f"FutOpt cancel order error: {e}")
        return OrderResponse(success=False, message=str(e))


@mcp.tool()
def futopt_query_order(
    account_id: str,
    product_type: ProductType = ProductType.FUTURES,
    force_query: bool = True
) -> QueryResult:
    """
    Query futures/options orders.
    
    Args:
        account_id: Account ID
        product_type: Product type (0=Futures, 1=Options)
        force_query: True to force refresh, False to use cache
    
    Returns:
        List of orders
    """
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    try:
        result = trade_wrapper.futopt_query_order(account_id, int(product_type), 1 if force_query else 0)
        
        # Wait for response
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(success=True, message="Query completed", data=data, event_id=event_id)
        else:
            return QueryResult(success=True, message="Query submitted", data=result if result else "Query initiated")
            
    except Exception as e:
        logger.error(f"FutOpt query order error: {e}")
        return QueryResult(success=False, message=str(e))


@mcp.tool()
def futopt_query_match(account_id: str, force_query: bool = True) -> QueryResult:
    """
    Query futures/options trade matches.
    
    Args:
        account_id: Account ID
        force_query: True to force refresh, False to use cache
    
    Returns:
        List of matched trades
    """
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    try:
        result = trade_wrapper.futopt_query_match(account_id, 1 if force_query else 0)
        
        # Wait for response
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(success=True, message="Query completed", data=data, event_id=event_id)
        else:
            return QueryResult(success=True, message="Query submitted", data=result if result else "Query initiated")
            
    except Exception as e:
        logger.error(f"FutOpt query match error: {e}")
        return QueryResult(success=False, message=str(e))


@mcp.tool()
def futopt_query_oi(
    account_id: str,
    trade_date: Optional[str] = None,
    force_query: bool = True
) -> QueryResult:
    """
    Query futures/options open interest.
    
    Args:
        account_id: Account ID
        trade_date: Trading date (defaults to today)
        force_query: True to force refresh, False to use cache
    
    Returns:
        Open interest positions
    """
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        result = trade_wrapper.futopt_query_oi(account_id, trade_date, 1 if force_query else 0)
        
        # Wait for response
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(success=True, message="Query completed", data=data, event_id=event_id)
        else:
            return QueryResult(success=True, message="Query submitted", data=result if result else "Query initiated")
            
    except Exception as e:
        logger.error(f"FutOpt query OI error: {e}")
        return QueryResult(success=False, message=str(e))


@mcp.tool()
def futopt_query_equity(
    account_id: str,
    trade_date: Optional[str] = None
) -> QueryResult:
    """
    Query futures/options account equity.
    
    Args:
        account_id: Account ID
        trade_date: Trading date (empty string for current, defaults to today)
    
    Returns:
        Account equity details
    """
    _initialize_wrapper()
    if not trade_wrapper:
        return QueryResult(success=False, message="Trading wrapper not initialized")
    
    if trade_date is None:
        trade_date = ""  # Empty string means current
    
    try:
        result = trade_wrapper.futopt_query_equity(account_id, trade_date)
        
        # Wait for response
        event_id, data = trade_wrapper.wait_for_response(timeout=5.0)
        
        if event_id is not None:
            return QueryResult(success=True, message="Query completed", data=data, event_id=event_id)
        else:
            return QueryResult(success=True, message="Query submitted", data=result if result else "Query initiated")
            
    except Exception as e:
        logger.error(f"FutOpt query equity error: {e}")
        return QueryResult(success=False, message=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the MCP server."""
    import sys
    
    logger.info("Starting CTS Trading API MCP Server...")
    logger.info(f"Python version: {sys.version}")
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
