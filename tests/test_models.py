from ctbcsec_mcp.models import (
    OrderRequest, 
    BuySell, 
    PriceType, 
    OrderCondition, 
    TradeType, 
    OrderType,
    AccountInfo,
    AccountType
)
import json

def test_order_request_defaults():
    """Test OrderRequest with default values."""
    order = OrderRequest(
        account_id="123456",
        trade_date="20260121",
        stock_id="2330",
        quantity="1000",
        price="500",
        buy_sell=BuySell.BUY
    )
    assert order.trade_type == TradeType.REGULAR
    assert order.order_type == OrderType.CASH
    assert order.price_type == PriceType.LIMIT
    assert order.condition == OrderCondition.ROD
    assert order.broker == ""
    assert order.pay_type == 0

def test_order_request_serialization():
    """Test OrderRequest JSON serialization."""
    order = OrderRequest(
        account_id="123456",
        trade_date="20260121",
        stock_id="2330",
        quantity="1000",
        price="500",
        buy_sell=BuySell.BUY
    )
    json_str = order.model_dump_json()
    data = json.loads(json_str)
    assert data["account_id"] == "123456"
    assert data["buy_sell"] == 1
    assert data["trade_type"] == 0

def test_account_info():
    """Test AccountInfo model."""
    account = AccountInfo(
        account_id="ACC123",
        account_name="Test Account",
        user_id="USER1",
        account_type=AccountType.STOCK,
        raw_data="<AccID=ACC123|...>"
    )
    assert account.account_id == "ACC123"
    assert account.account_type == AccountType.STOCK

def test_enums():
    """Test enum value mapping matches CTS API specs."""
    assert TradeType.REGULAR == 0
    assert TradeType.AFTER_HOURS == 2
    assert OrderType.CASH == 0
    assert OrderType.MARGIN == 1
    assert BuySell.BUY == 1
    assert BuySell.SELL == 2
    assert PriceType.LIMIT == 0
    assert PriceType.MARKET == 4
    assert OrderCondition.ROD == 0
    assert OrderCondition.IOC == 1
    assert OrderCondition.FOK == 2
