import pytest

from ctbcsec_mcp.models import BuySell, OrderCondition, OrderType, PriceType, TradeType
from ctbcsec_mcp.wrapper import TradeAppWrapper


def test_wrapper_init(trade_wrapper_mocked, mock_com_object):
    """Test wrapper initialization."""
    result, err_code, err_msg = trade_wrapper_mocked.init("test_url")
    
    assert result == 1
    assert err_code == 0
    assert trade_wrapper_mocked.status.initialized is True
    assert trade_wrapper_mocked.status.trade_das_url == "test_url"
    mock_com_object.Init.assert_called_once_with("test_url")
    mock_com_object.SetEchoType.assert_called_once_with(1, 1)

def test_wrapper_login(trade_wrapper_mocked, mock_com_object):
    """Test wrapper login and account retrieval."""
    trade_wrapper_mocked.init("test_url")
    result, err_code, err_msg = trade_wrapper_mocked.login("user", "pass")
    
    assert result == 1
    assert trade_wrapper_mocked.status.logged_in is True
    assert trade_wrapper_mocked.status.user_id == "user"
    assert trade_wrapper_mocked.status.account_count == 1
    mock_com_object.Login.assert_called_once_with("user", "pass")
    mock_com_object.GetAccountCount.assert_called()

def test_wrapper_get_accounts(trade_wrapper_mocked, mock_com_object):
    """Test parsing account data."""
    trade_wrapper_mocked.init("test_url")
    trade_wrapper_mocked.login("user", "pass")
    accounts = trade_wrapper_mocked.get_accounts()
    
    assert len(accounts) == 1
    assert accounts[0].account_id == "123"
    assert accounts[0].account_name == "TestAccount"
    assert accounts[0].user_id == "User1"
    assert accounts[0].account_type == 1

def test_wrapper_stock_new_order(trade_wrapper_mocked, mock_com_object):
    """Test stock order placement."""
    trade_wrapper_mocked.init("test_url")
    trade_wrapper_mocked.login("user", "pass")
    trade_wrapper_mocked.connect()
    
    mock_com_object.Stock_NewOrder.return_value = "" # Empty string means success
    
    result = trade_wrapper_mocked.stock_new_order(
        "ACC123", "20260121", 0, 0, 1, "2330", "1000", 0, "500", "", 0, 0
    )
    
    assert result == ""
    mock_com_object.Stock_NewOrder.assert_called_once()

def test_wrapper_wait_for_response(trade_wrapper_mocked):
    """Test response queue mechanism."""
    # Put a mock response in the queue
    trade_wrapper_mocked.response_queue.put((10, "test_data"))
    
    event_id, data = trade_wrapper_mocked.wait_for_response(timeout=0.1)
    
    assert event_id == 10
    assert data == "test_data"

def test_wrapper_wait_for_response_timeout(trade_wrapper_mocked):
    """Test response queue timeout."""
    event_id, data = trade_wrapper_mocked.wait_for_response(timeout=0.1)
    assert event_id is None
    assert data is None
