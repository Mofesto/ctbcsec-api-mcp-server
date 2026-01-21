"""
Pydantic models for CTS Trading API MCP Server.

These models provide type safety and schema generation for MCP tools.
"""

from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field


class TradeType(IntEnum):
    """Stock trade type"""
    REGULAR = 0
    AFTER_HOURS_ODD_LOT = 1
    AFTER_HOURS = 2
    EMERGING = 5
    INTRADAY_ODD_LOT = 7


class OrderType(IntEnum):
    """Stock order type"""
    CASH = 0
    MARGIN = 1
    SHORT = 2
    DAY_TRADING_SELL_FIRST = 16


class BuySell(IntEnum):
    """Buy or sell direction"""
    BUY = 1
    SELL = 2


class PriceType(IntEnum):
    """Order price type"""
    LIMIT = 0
    LIMIT_UP = 1
    LIMIT_DOWN = 2
    FLAT = 3
    MARKET = 4


class OrderCondition(IntEnum):
    """Order time-in-force condition"""
    ROD = 0  # Rest of Day
    IOC = 1  # Immediate or Cancel
    FOK = 2  # Fill or Kill


class ProductType(IntEnum):
    """Futures/Options product type"""
    FUTURES = 0
    OPTIONS = 1
    COMPLEX_OPTIONS = 2
    COMPLEX_FUTURES = 3


class AccountType(IntEnum):
    """Account type"""
    STOCK = 1
    FUTURES_OPTIONS = 2
    INTERNATIONAL = 3


class AccountInfo(BaseModel):
    """Trading account information"""
    account_id: str = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    user_id: str = Field(..., description="User ID")
    account_type: AccountType = Field(..., description="Account type (1=Stock, 2=Futures/Options, 3=International)")
    raw_data: str = Field(..., description="Raw account data from API")


class ConnectionStatus(BaseModel):
    """Current connection and authentication status"""
    initialized: bool = Field(default=False, description="Whether Init() has been called")
    logged_in: bool = Field(default=False, description="Whether user is logged in")
    connected: bool = Field(default=False, description="Whether connected to trading server")
    user_id: Optional[str] = Field(default=None, description="Current logged-in user ID")
    account_count: int = Field(default=0, description="Number of available accounts")
    trade_das_url: Optional[str] = Field(default=None, description="Trading DAS server URL")


class OrderRequest(BaseModel):
    """Stock order request parameters"""
    account_id: str = Field(..., description="Account ID")
    trade_date: str = Field(..., description="Trading date in YYYYMMDD format")
    trade_type: TradeType = Field(default=TradeType.REGULAR, description="Trade type")
    order_type: OrderType = Field(default=OrderType.CASH, description="Order type")
    buy_sell: BuySell = Field(..., description="Buy or sell")
    stock_id: str = Field(..., description="Stock symbol (e.g., '2330')")
    quantity: str = Field(..., description="Number of shares")
    price_type: PriceType = Field(default=PriceType.LIMIT, description="Price type")
    price: str = Field(..., description="Order price ('0' for market orders)")
    broker: str = Field(default="", description="Broker code (usually empty)")
    pay_type: int = Field(default=0, description="Payment type")
    condition: OrderCondition = Field(default=OrderCondition.ROD, description="Order condition")


class FutOptOrderRequest(BaseModel):
    """Futures/Options order request parameters"""
    account_id: str = Field(..., description="Account ID")
    trade_date: str = Field(..., description="Trading date in YYYYMMDD format")
    product_type: ProductType = Field(..., description="Product type (0=Futures, 1=Options)")
    trade_id1: str = Field(..., description="Contract ID (e.g., 'TXFJ4')")
    buy_sell1: BuySell = Field(..., description="Buy or sell")
    price_type: PriceType = Field(default=PriceType.LIMIT, description="Price type")
    price: str = Field(..., description="Order price ('0' for market orders)")
    quantity: int = Field(..., description="Number of contracts")
    offset: int = Field(default=0, description="Offset flag (0=Open, 1=Close)")
    condition: OrderCondition = Field(default=OrderCondition.ROD, description="Order condition")
    trade_id2: str = Field(default="", description="Second leg contract ID for complex orders")
    buy_sell2: int = Field(default=0, description="Second leg buy/sell")
    pre_order: int = Field(default=0, description="Pre-order flag")


class OrderModifyRequest(BaseModel):
    """Stock order modification request"""
    account_id: str = Field(..., description="Account ID")
    trade_date: str = Field(..., description="Trading date in YYYYMMDD format")
    trade_type: TradeType = Field(..., description="Trade type")
    order_type: OrderType = Field(..., description="Order type")
    order_id: str = Field(..., description="Original order ID")
    order_number: str = Field(..., description="Order number")
    stock_id: str = Field(..., description="Stock symbol")
    buy_sell: BuySell = Field(..., description="Buy or sell")
    new_quantity: int = Field(..., description="New quantity (0 to keep unchanged)")
    current_quantity: int = Field(..., description="Current remaining quantity")
    matched_quantity: int = Field(..., description="Matched quantity")
    pre_order: int = Field(default=0, description="Pre-order flag")
    modify_type: int = Field(..., description="Modification type (0=Quantity, 2=Price)")
    new_price: str = Field(..., description="New price")
    price_type: PriceType = Field(..., description="Price type")
    condition: OrderCondition = Field(..., description="Order condition")


class OrderCancelRequest(BaseModel):
    """Stock order cancellation request"""
    account_id: str = Field(..., description="Account ID")
    trade_date: str = Field(..., description="Trading date in YYYYMMDD format")
    trade_type: TradeType = Field(..., description="Trade type")
    order_type: OrderType = Field(..., description="Order type")
    order_id: str = Field(..., description="Original order ID")
    order_number: str = Field(..., description="Order number")
    stock_id: str = Field(..., description="Stock symbol")
    buy_sell: BuySell = Field(..., description="Buy or sell")
    quantity: int = Field(..., description="Order quantity")
    current_quantity: int = Field(..., description="Current remaining quantity")
    matched_quantity: int = Field(..., description="Matched quantity")
    pre_order: int = Field(default=0, description="Pre-order flag")
    price: str = Field(..., description="Order price")
    price_type: PriceType = Field(..., description="Price type")
    condition: OrderCondition = Field(..., description="Order condition")


class OrderResponse(BaseModel):
    """Order operation response"""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(default="", description="Response message or error description")
    order_id: Optional[str] = Field(default=None, description="Order ID if successful")


class QueryResult(BaseModel):
    """Query operation response"""
    success: bool = Field(..., description="Whether the query succeeded")
    message: str = Field(default="", description="Response message or error description")
    data: Optional[str] = Field(default=None, description="Query result data")
    event_id: Optional[int] = Field(default=None, description="Event ID from response")


class InitResponse(BaseModel):
    """Initialization response"""
    success: bool = Field(..., description="Whether initialization succeeded")
    error_code: int = Field(default=0, description="Error code")
    error_message: str = Field(default="", description="Error message if failed")


class LoginResponse(BaseModel):
    """Login response"""
    success: bool = Field(..., description="Whether login succeeded")
    error_code: int = Field(default=0, description="Error code")
    error_message: str = Field(default="", description="Error message if failed")
    accounts: list[AccountInfo] = Field(default_factory=list, description="List of available accounts")
