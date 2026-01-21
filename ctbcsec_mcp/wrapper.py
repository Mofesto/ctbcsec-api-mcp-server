"""
COM Object wrapper for CTS Trading API.

This module wraps the Windows COM object and provides a cleaner Python interface
with proper error handling and response parsing.
"""

import logging
import queue
import sys
import threading
from typing import Any, Optional, Tuple

# Only import win32com on Windows platforms
if sys.platform == 'win32':
    import win32com.client
else:
    # Provide stub for non-Windows platforms
    win32com = None

from .models import AccountInfo, AccountType, ConnectionStatus

logger = logging.getLogger(__name__)


class TradeAppWrapper:
    """
    Wrapper for DJTRADEOBJLibCTS.TradeApp COM object.
    
    Manages the COM object lifecycle, event handling, and response queuing.
    """
    
    def __init__(self):
        self.trade_app: Optional[Any] = None
        self.response_queue: queue.Queue = queue.Queue()
        self.status = ConnectionStatus()
        self._lock = threading.Lock()
        
    def create_com_object(self):
        """Create and initialize the COM object with event handler."""
        if sys.platform != 'win32':
            raise RuntimeError(
                "CTS Trading API COM object is only available on Windows. "
                "This platform does not support the trading functionality."
            )
        
        try:
            # Create COM object with event handler
            self.trade_app = win32com.client.DispatchWithEvents(
                "DJTRADEOBJLibCTS.TradeApp",
                EventHandler
            )
            # Set the response queue in the event handler
            self.trade_app.response_queue = self.response_queue
            logger.info("COM object created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create COM object: {e}")
            raise RuntimeError(f"Failed to create COM object. Ensure CTS Trading API is installed: {e}")
    
    def init(self, trade_das_url: str) -> Tuple[int, int, str]:
        """
        Initialize the trading application.
        
        Args:
            trade_das_url: Trading DAS server endpoint
            
        Returns:
            Tuple of (result, error_code, error_message)
        """
        if not self.trade_app:
            raise RuntimeError("COM object not created. Call create_com_object() first.")
        
        try:
            with self._lock:
                result, err_code, err_msg = self.trade_app.Init(trade_das_url)
                
                if result == 1:
                    self.status.initialized = True
                    self.status.trade_das_url = trade_das_url
                    # Set echo type
                    self.trade_app.SetEchoType(1, 1)
                    logger.info("Trading app initialized successfully")
                else:
                    logger.error(f"Initialization failed: {err_msg}")
                
                return (result, err_code, err_msg)
        except Exception as e:
            logger.error(f"Init error: {e}")
            return (0, -1, str(e))
    
    def set_lot_size_data(self, lot_size_string: str):
        """
        Set lot size data for specific stocks.
        
        Args:
            lot_size_string: Lot size configuration (e.g., "0050=1000|0028=1000")
        """
        if not self.trade_app:
            raise RuntimeError("COM object not initialized")
        
        try:
            self.trade_app.SetLotSizeData(lot_size_string)
            logger.info(f"Lot size data set: {lot_size_string}")
        except Exception as e:
            logger.error(f"Failed to set lot size data: {e}")
            raise
    
    def login(self, user_id: str, password: str) -> Tuple[int, int, str]:
        """
        Login to the trading system.
        
        Args:
            user_id: User account ID
            password: User password
            
        Returns:
            Tuple of (result, error_code, error_message)
        """
        if not self.trade_app or not self.status.initialized:
            raise RuntimeError("Trading app not initialized. Call init() first.")
        
        try:
            with self._lock:
                result, err_code, err_msg = self.trade_app.Login(user_id, password)
                
                if result == 1:
                    self.status.logged_in = True
                    self.status.user_id = user_id
                    self.status.account_count = self.trade_app.GetAccountCount()
                    logger.info(f"Login successful for user {user_id}")
                else:
                    logger.error(f"Login failed: {err_msg}")
                
                return (result, err_code, err_msg)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return (0, -1, str(e))
    
    def connect(self) -> int:
        """
        Connect to the trading server.
        
        Returns:
            Non-zero on success, 0 on failure
        """
        if not self.trade_app or not self.status.logged_in:
            raise RuntimeError("Not logged in. Call login() first.")
        
        try:
            with self._lock:
                result = self.trade_app.Connect()
                
                if result != 0:
                    self.status.connected = True
                    logger.info("Connected to trading server")
                else:
                    logger.error("Connection failed")
                
                return result
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return 0
    
    def disconnect(self):
        """Disconnect from the trading server."""
        if not self.trade_app:
            return
        
        try:
            with self._lock:
                self.trade_app.Disconnect()
                self.status.connected = False
                logger.info("Disconnected from trading server")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    def logout(self, user_id: str):
        """
        Logout from the trading system.
        
        Args:
            user_id: User account ID
        """
        if not self.trade_app:
            return
        
        try:
            with self._lock:
                self.trade_app.Logout(user_id)
                self.status.logged_in = False
                self.status.user_id = None
                logger.info(f"Logged out user {user_id}")
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def fini(self):
        """Finalize and clean up the trading application."""
        if not self.trade_app:
            return
        
        try:
            with self._lock:
                self.trade_app.Fini()
                self.status = ConnectionStatus()
                logger.info("Trading app finalized")
        except Exception as e:
            logger.error(f"Fini error: {e}")
    
    def get_accounts(self) -> list[AccountInfo]:
        """
        Get all available trading accounts.
        
        Returns:
            List of AccountInfo objects
        """
        if not self.trade_app or not self.status.logged_in:
            raise RuntimeError("Not logged in")
        
        accounts = []
        try:
            count = self.trade_app.GetAccountCount()
            
            for i in range(count):
                account_data = self.trade_app.GetAccount(i)
                account_data = account_data.strip('<>')
                
                # Parse account data
                fields = {}
                for field in account_data.split("|"):
                    if "=" in field:
                        key, value = field.split("=", 1)
                        fields[key] = value
                
                # Create AccountInfo object
                account = AccountInfo(
                    account_id=fields.get("AccID", ""),
                    account_name=fields.get("AccName", ""),
                    user_id=fields.get("UID", ""),
                    account_type=AccountType(int(fields.get("AccType", "1"))),
                    raw_data=account_data
                )
                accounts.append(account)
            
            logger.info(f"Retrieved {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            raise
    
    def get_status(self) -> ConnectionStatus:
        """Get current connection status."""
        return self.status.model_copy()
    
    # Stock trading methods
    def stock_new_order(self, account_id: str, trade_date: str, tt: int, ot: int, 
                       bs: int, stock_id: str, qty: str, pt: int, price: str,
                       broker: str, pay_type: int, cond: int) -> str:
        """Place a new stock order."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.Stock_NewOrder(
                account_id, trade_date, tt, ot, bs, stock_id,
                qty, pt, price, broker, pay_type, cond
            )
            logger.info(f"Stock order placed: {stock_id} x {qty}")
            return result if result else ""
        except Exception as e:
            logger.error(f"Stock order error: {e}")
            raise
    
    def stock_modify_order(self, account_id: str, trade_date: str, tt: int, ot: int,
                          oid: str, order_number: str, stock_id: str, bs: int,
                          qty: int, q_current: int, q_match: int, pre_order: int,
                          modify_type: int, price: str, pt: int, cond: int) -> str:
        """Modify an existing stock order."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.Stock_ModifyOrder(
                account_id, trade_date, tt, ot, oid, order_number, stock_id,
                bs, qty, q_current, q_match, pre_order, modify_type, price, pt, cond
            )
            logger.info(f"Stock order modified: {oid}")
            return result if result else ""
        except Exception as e:
            logger.error(f"Stock modify error: {e}")
            raise
    
    def stock_cancel_order(self, account_id: str, trade_date: str, tt: int, ot: int,
                          oid: str, order_number: str, stock_id: str, bs: int,
                          qty: int, q_current: int, q_match: int, pre_order: int,
                          price: str, pt: int, cond: int) -> str:
        """Cancel an existing stock order."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.Stock_CancelOrder(
                account_id, trade_date, tt, ot, oid, order_number, stock_id,
                bs, qty, q_current, q_match, pre_order, price, pt, cond
            )
            logger.info(f"Stock order cancelled: {oid}")
            return result if result else ""
        except Exception as e:
            logger.error(f"Stock cancel error: {e}")
            raise
    
    def stock_query_order(self, account_id: str, force_query: int) -> str:
        """Query stock orders."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.Stock_QueryOrder(account_id, force_query)
            logger.info(f"Stock orders queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"Stock query order error: {e}")
            raise
    
    def stock_query_match(self, account_id: str, force_query: int) -> str:
        """Query stock matches."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.Stock_QueryMatch(account_id, force_query)
            logger.info(f"Stock matches queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"Stock query match error: {e}")
            raise
    
    def stock_query_position(self, account_id: str, trade_date: str, force_query: int) -> str:
        """Query stock positions."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.Stock_QueryPosition(account_id, trade_date, force_query)
            logger.info(f"Stock positions queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"Stock query position error: {e}")
            raise
    
    # Futures/Options trading methods
    def futopt_new_order(self, account_id: str, trade_date: str, tt: int,
                        trade_id1: str, bs1: int, pt: int, price: str, qty: int,
                        offset: int, cond: int, trade_id2: str, bs2: int, pre_order: int) -> str:
        """Place a new futures/options order."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_NewOrder(
                account_id, trade_date, tt, trade_id1, bs1, pt, price,
                qty, offset, cond, trade_id2, bs2, pre_order
            )
            logger.info(f"FutOpt order placed: {trade_id1} x {qty}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt order error: {e}")
            raise
    
    def futopt_modify_order(self, account_id: str, modify_type: int, trade_date: str,
                           oid: str, order_no: str, qty: int, tt: int, q_current: int,
                           q_match: int, pre_order: int, new_pt: int, new_price: str,
                           new_cond: int, trade_id1: str, trade_id2: str) -> str:
        """Modify an existing futures/options order."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_ModifyOrder(
                account_id, modify_type, trade_date, oid, order_no, qty, tt,
                q_current, q_match, pre_order, new_pt, new_price, new_cond,
                trade_id1, trade_id2
            )
            logger.info(f"FutOpt order modified: {oid}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt modify error: {e}")
            raise
    
    def futopt_cancel_order(self, account_id: str, trade_date: str, oid: str,
                           order_no: str, qty: int, tt: int, q_current: int,
                           q_match: int, pre_order: int, trade_id1: str, trade_id2: str) -> str:
        """Cancel an existing futures/options order."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_CancelOrder(
                account_id, trade_date, oid, order_no, qty, tt,
                q_current, q_match, pre_order, trade_id1, trade_id2
            )
            logger.info(f"FutOpt order cancelled: {oid}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt cancel error: {e}")
            raise
    
    def futopt_query_order(self, account_id: str, tt: int, force_query: int) -> str:
        """Query futures/options orders."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_QueryOrder(account_id, tt, force_query)
            logger.info(f"FutOpt orders queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt query order error: {e}")
            raise
    
    def futopt_query_match(self, account_id: str, force_query: int) -> str:
        """Query futures/options matches."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_QueryMatch(account_id, force_query)
            logger.info(f"FutOpt matches queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt query match error: {e}")
            raise
    
    def futopt_query_oi(self, account_id: str, trade_date: str, force_query: int) -> str:
        """Query futures/options open interest."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_QueryOI(account_id, trade_date, force_query)
            logger.info(f"FutOpt OI queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt query OI error: {e}")
            raise
    
    def futopt_query_equity(self, account_id: str, trade_date: str) -> str:
        """Query futures/options account equity."""
        if not self.trade_app or not self.status.connected:
            raise RuntimeError("Not connected to trading server")
        
        try:
            result = self.trade_app.FutOpt_QueryEquity(account_id, trade_date)
            logger.info(f"FutOpt equity queried for account {account_id}")
            return result if result else ""
        except Exception as e:
            logger.error(f"FutOpt query equity error: {e}")
            raise
    
    def wait_for_response(self, timeout: float = 5.0) -> Tuple[Optional[int], Optional[str]]:
        """
        Wait for a response from the event queue.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Tuple of (event_id, response_data) or (None, None) on timeout
        """
        try:
            event_id, data = self.response_queue.get(timeout=timeout)
            return (event_id, data)
        except queue.Empty:
            return (None, None)


class EventHandler:
    """Event handler for COM object callbacks."""
    
    def __init__(self):
        self.response_queue = None
    
    def OnDataResponse(self, event_id: int, response_data: str):
        """
        Handle data response events from the COM object.
        
        Args:
            event_id: Event type ID
            response_data: Response data string
        """
        logger.debug(f"Event {event_id}: {response_data[:100]}...")
        
        if self.response_queue:
            self.response_queue.put((event_id, response_data))
