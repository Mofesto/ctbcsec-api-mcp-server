from unittest.mock import MagicMock, patch

import pytest

from ctbcsec_mcp.models import BuySell, OrderCondition, OrderType, PriceType, TradeType
from ctbcsec_mcp.server import initialize, login, mcp, stock_new_order


@pytest.fixture
def mock_wrapper(monkeypatch):
    """Fixture to mock the global trade_wrapper in server.py."""
    mock = MagicMock()
    # Replace the global trade_wrapper in server module
    import ctbcsec_mcp.server
    monkeypatch.setattr(ctbcsec_mcp.server, "trade_wrapper", mock)
    return mock

def test_initialize_tool(mock_wrapper):
    """Test initialize tool logic."""
    mock_wrapper.init.return_value = (1, 0, "Success")
    
    response = initialize("test_url")
    
    assert response.success is True
    mock_wrapper.init.assert_called_once_with("test_url")

def test_login_tool(mock_wrapper):
    """Test login tool logic."""
    mock_wrapper.login.return_value = (1, 0, "Success")
    mock_wrapper.get_accounts.return_value = []
    
    response = login("user", "pass")
    
    assert response.success is True
    assert response.error_message == "Login successful"
    mock_wrapper.login.assert_called_once_with("user", "pass")

def test_stock_new_order_tool(mock_wrapper):
    """Test stock_new_order tool logic."""
    mock_wrapper.stock_new_order.return_value = "" # Success
    
    response = stock_new_order(
        account_id="ACC123",
        stock_id="2330",
        quantity="1000",
        price="500",
        buy_sell=BuySell.BUY,
        trade_date="20260121"
    )
    
    assert response.success is True
    assert "Stock order placed" in response.message
    mock_wrapper.stock_new_order.assert_called_once()

async def test_mcp_registration():
    """Verify tools are correctly registered with FastMCP."""
    # FastMCP tools are stored in its internal registry
    # Check if some of our tools are present
    tools = await mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    assert "initialize" in tool_names
    assert "login" in tool_names
    assert "stock_new_order" in tool_names
    assert "get_accounts" in tool_names
