import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock win32com for non-Windows platforms before any imports
if sys.platform != 'win32':
    sys.modules['win32com'] = MagicMock()
    sys.modules['win32com.client'] = MagicMock()
    sys.modules['pythoncom'] = MagicMock()

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
def trade_wrapper_real(mock_com_object, monkeypatch):
    """Fixture to provide a TradeAppWrapper (mocked on non-Windows platforms)."""
    import win32com.client

    from ctbcsec_mcp.wrapper import TradeAppWrapper
    
    # On Linux, use mock_com_object; on Windows, try to use real COM object
    if sys.platform != 'win32':
        # Linux: Use mocked COM object
        monkeypatch.setattr("win32com.client.DispatchWithEvents", lambda progid, handler_class: mock_com_object)
        wrapper = TradeAppWrapper()
        try:
            wrapper.create_com_object()
            return wrapper
        except Exception:
            pytest.skip("Failed to initialize mocked COM object")
    else:
        # Windows: Try to use real COM object
        wrapper = TradeAppWrapper()
        try:
            wrapper.create_com_object()
            return wrapper
        except RuntimeError:
            pytest.skip("CTS Trading API (COM object) not installed or failed to load")
