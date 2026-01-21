
from unittest.mock import MagicMock

import pytest

from ctbcsec_mcp.models import AccountInfo, AccountType
from ctbcsec_mcp.server import initialize, login


@pytest.fixture
def mock_wrapper(monkeypatch):
    """Fixture to mock the global trade_wrapper in server.py."""
    mock = MagicMock()
    # Replace the global trade_wrapper in server module
    import ctbcsec_mcp.server
    monkeypatch.setattr(ctbcsec_mcp.server, "trade_wrapper", mock)
    return mock

def test_initialize_success(mock_wrapper):
    """Test successful initialization."""
    mock_wrapper.init.return_value = (1, 0, "Success")
    
    response = initialize("test_url")
    
    assert response.success is True
    assert response.error_code == 0
    assert response.error_message == "Initialization successful"
    mock_wrapper.init.assert_called_once_with("test_url")

def test_initialize_failure(mock_wrapper):
    """Test initialization failure."""
    mock_wrapper.init.return_value = (0, -100, "Connection failed")
    
    response = initialize("bad_url")
    
    assert response.success is False
    assert response.error_code == -100
    assert response.error_message == "Connection failed"
    mock_wrapper.init.assert_called_once_with("bad_url")

def test_initialize_exception(mock_wrapper):
    """Test exception during initialization."""
    mock_wrapper.init.side_effect = Exception("Network error")
    
    response = initialize("test_url")
    
    assert response.success is False
    assert response.error_code == -1
    assert "Network error" in response.error_message

def test_login_success(mock_wrapper):
    """Test successful login with accounts."""
    mock_wrapper.login.return_value = (1, 0, "Success")
    
    # Mock accounts
    acc1 = AccountInfo(
        account_id="123",
        account_name="Test",
        user_id="user",
        account_type=AccountType.STOCK,
        raw_data=""
    )
    mock_wrapper.get_accounts.return_value = [acc1]
    
    response = login("user", "pass")
    
    assert response.success is True
    assert response.error_code == 0
    assert len(response.accounts) == 1
    assert response.accounts[0].account_id == "123"
    mock_wrapper.login.assert_called_once_with("user", "pass")

def test_login_failure(mock_wrapper):
    """Test login failure (wrong password)."""
    mock_wrapper.login.return_value = (0, -500, "Invalid password")
    
    response = login("user", "wrong_pass")
    
    assert response.success is False
    assert response.error_code == -500
    assert response.error_message == "Invalid password"
    # Ensure get_accounts is NOT called
    mock_wrapper.get_accounts.assert_not_called()

def test_login_not_initialized(monkeypatch):
    """Test login when wrapper is not initialized."""
    import ctbcsec_mcp.server

    # Ensure trade_wrapper is None
    monkeypatch.setattr(ctbcsec_mcp.server, "trade_wrapper", None)
    # We also need to mock _initialize_wrapper so it doesn't create a real one
    monkeypatch.setattr(ctbcsec_mcp.server, "_initialize_wrapper", lambda: None)
    
    response = login("user", "pass")
    
    assert response.success is False
    assert response.error_message == "Trading wrapper not initialized"

def test_login_exception(mock_wrapper):
    """Test exception during login."""
    mock_wrapper.login.side_effect = Exception("Login timeout")
    
    response = login("user", "pass")
    
    assert response.success is False
    assert response.error_message == "Login timeout"
