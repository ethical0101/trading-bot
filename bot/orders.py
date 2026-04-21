"""
Order placement logic for Binance Futures Testnet.

Supports MARKET, LIMIT, and STOP_LIMIT orders.
Provides a clean, structured result object for CLI rendering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import get_logger

logger = get_logger("orders")


# ── Result data class ──────────────────────────────────────────────────────────

@dataclass
class OrderResult:
    """
    Encapsulates the outcome of an order placement attempt.

    Attributes:
        success:      Whether the order was accepted by the exchange.
        order_id:     Binance-assigned order ID (None on failure).
        status:       Order status string (e.g. NEW, FILLED).
        executed_qty: Quantity that has been filled so far.
        avg_price:    Average fill price (0 for unfilled orders).
        symbol:       Trading pair.
        side:         BUY or SELL.
        order_type:   MARKET / LIMIT / STOP_LIMIT.
        quantity:     Requested quantity.
        price:        Limit price (None for MARKET).
        stop_price:   Stop trigger price (STOP_LIMIT only).
        error:        Human-readable error message on failure.
        raw_response: Full raw API response dict.
    """

    success: bool
    order_id: Optional[int] = None
    status: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    symbol: str = ""
    side: str = ""
    order_type: str = ""
    quantity: float = 0.0
    price: Optional[float] = None
    stop_price: Optional[float] = None
    error: Optional[str] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)


# ── Order builder ──────────────────────────────────────────────────────────────

class OrderManager:
    """
    Constructs and dispatches order requests via BinanceFuturesClient.
    """

    def __init__(self, client: BinanceFuturesClient) -> None:
        self._client = client

    # ── Public order methods ───────────────────────────────────────────────────

    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
    ) -> OrderResult:
        """
        Place a MARKET order.

        Args:
            symbol:   Trading pair (e.g. BTCUSDT).
            side:     BUY or SELL.
            quantity: Quantity to trade.

        Returns:
            Populated OrderResult.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
        }
        return self._execute(params, symbol, side, "MARKET", quantity)

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC",
    ) -> OrderResult:
        """
        Place a LIMIT order.

        Args:
            symbol:        Trading pair.
            side:          BUY or SELL.
            quantity:      Quantity to trade.
            price:         Limit price.
            time_in_force: GTC (default), IOC, or FOK.

        Returns:
            Populated OrderResult.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force,
        }
        return self._execute(params, symbol, side, "LIMIT", quantity, price=price)

    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC",
    ) -> OrderResult:
        """
        Place a STOP_LIMIT order (bonus feature).

        A STOP_LIMIT triggers a LIMIT order once the market reaches
        `stop_price`, placing the LIMIT at `price`.

        Args:
            symbol:        Trading pair.
            side:          BUY or SELL.
            quantity:      Quantity to trade.
            price:         Limit price (executes at this level or better).
            stop_price:    Trigger price (order activates when hit).
            time_in_force: GTC (default).

        Returns:
            Populated OrderResult.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",         # Binance futures uses "STOP" for stop-limit
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price,
            "timeInForce": time_in_force,
        }
        return self._execute(
            params, symbol, side, "STOP_LIMIT", quantity,
            price=price, stop_price=stop_price,
        )

    # ── Private helper ─────────────────────────────────────────────────────────

    def _execute(
        self,
        params: Dict[str, Any],
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> OrderResult:
        """
        Send the order request and map the response to an OrderResult.

        Args:
            params:     Full parameter dict for the API call.
            symbol:     Trading pair.
            side:       BUY or SELL.
            order_type: Human-readable order type label.
            quantity:   Requested quantity.
            price:      Limit price if applicable.
            stop_price: Stop trigger price if applicable.

        Returns:
            Populated OrderResult (success or failure).
        """
        logger.debug(
            "Preparing %s %s order | symbol=%s qty=%s",
            side, order_type, symbol, quantity,
        )

        try:
            response = self._client.new_order(**params)
        except BinanceClientError as exc:
            logger.error("Order failed | %s", exc)
            return OrderResult(
                success=False,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                error=str(exc),
            )

        return OrderResult(
            success=True,
            order_id=response.get("orderId"),
            status=response.get("status"),
            executed_qty=response.get("executedQty"),
            avg_price=response.get("avgPrice"),
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            raw_response=response,
        )
