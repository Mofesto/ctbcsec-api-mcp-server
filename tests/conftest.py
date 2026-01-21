import os
import sys
from unittest.mock import MagicMock

import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_com_object():
    """Fixture to provide a mocked COM object."""
    mock = MagicMock()
    # Mock some basic methods
    mock.Init.return_value = (1, 0, "Success")
    mock.Login.return_value = (1, 0, "Success")
    mock.Connect.return_value = 1
    mock.GetAccountCount.return_value = 1
    mock.GetAccount.return_value = "<AccID=123|AccName=TestAccount|UID=User1|AccType=1>"
    return mock

@pytest.fixture
def trade_wrapper_mocked(mock_com_object, monkeypatch):
    """Fixture to provide a TradeAppWrapper with a mocked COM object."""
    import win32com.client

    from ctbcsec_mcp.wrapper import TradeAppWrapper

    # Mock win32com.client.DispatchWithEvents
    monkeypatch.setattr("win32com.client.DispatchWithEvents", lambda progid, handler_class: mock_com_object)
    
    wrapper = TradeAppWrapper()
    wrapper.create_com_object()
    return wrapper

@pytest.fixture
def trade_wrapper_real():
    """Fixture to provide a REAL TradeAppWrapper without mocking."""
    import win32com.client

    from ctbcsec_mcp.wrapper import TradeAppWrapper
    
    wrapper = TradeAppWrapper()
    try:
        wrapper.create_com_object()
    except RuntimeError:
        pytest.skip("CTS Trading API (COM object) not installed or failed to load")
    return wrapper
