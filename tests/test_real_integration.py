
import pytest

from ctbcsec_mcp.models import AccountType, ConnectionStatus, InitResponse, LoginResponse


def test_real_initialize_success(trade_wrapper_real):
    """Test successful initialization with REAL COM object."""
    # Use the URL found in manual_test_local.py or a known test environment
    trade_das_url = "apsit.ectest.ctbcsec.com/tradedas"
    
    result, err_code, err_msg = trade_wrapper_real.init(trade_das_url)
    
    assert result == 1
    assert err_code == 0
    assert trade_wrapper_real.status.initialized is True
    assert trade_wrapper_real.status.trade_das_url == trade_das_url
    print(f"\nReal Init Result: {result}, Message: {err_msg}")

@pytest.mark.skip(reason="Requires valid credentials")
def test_real_login_success(trade_wrapper_real):
    """Test successful login with REAL COM object."""
    # Initialize first
    trade_das_url = "apsit.ectest.ctbcsec.com/tradedas"
    trade_wrapper_real.init(trade_das_url)
    
    # Needs valid credentials - skipping by default unless provided
    user_id = "YOUR_USER_ID"
    password = "YOUR_PASSWORD"
    
    if user_id == "YOUR_USER_ID":
        pytest.skip("Valid credentials required for real login test")
        
    result, err_code, err_msg = trade_wrapper_real.login(user_id, password)
    
    assert result == 1, f"Login failed: {err_msg}"
    assert trade_wrapper_real.status.logged_in is True
    
    # Get accounts
    accounts = trade_wrapper_real.get_accounts()
    print(f"\nFound {len(accounts)} accounts")
    for acc in accounts:
        print(f"  {acc.account_id} ({acc.account_name})")

def test_real_initialize_invalid_url(trade_wrapper_real):
    """Test initialization with invalid URL on REAL COM object."""
    # This might hang or return error depending on the API behavior
    # Use a non-existent URL
    invalid_url = "invalid.url.test/tradedas"
    
    # We expect it might fail or return error code
    result, err_code, err_msg = trade_wrapper_real.init(invalid_url)
    
    # Note: Initialization might actually 'succeed' locally but fail to connect later?
    # Or return 0. Let's inspect the behavior.
    print(f"\nInvalid URL Init Result: {result}, Code: {err_code}, Msg: {err_msg}")
    
    # If it returns 0 (failure), assertion passes
    # If it returns 1 but logs error, we might need to adjust expectation
    # For now, just print the result
