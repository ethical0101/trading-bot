"""
trading_bot.bot — Core library package.

Public re-exports for convenience:
    BinanceFuturesClient, BinanceClientError  (client.py)
    OrderManager, OrderResult                 (orders.py)
    setup_logging, get_logger                 (logging_config.py)
"""

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import get_logger, setup_logging
from bot.orders import OrderManager, OrderResult

__all__ = [
    "BinanceFuturesClient",
    "BinanceClientError",
    "get_logger",
    "setup_logging",
    "OrderManager",
    "OrderResult",
]
