"""
Binance Futures Testnet API client wrapper.

Wraps python-binance's UMFutures client and provides safe, logged
API call helpers used by the order layer.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from bot.logging_config import get_logger

# Load .env early so os.getenv picks up the values
load_dotenv()

logger = get_logger("client")

# ── Testnet base URL ───────────────────────────────────────────────────────────
FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the Binance client cannot be initialised or a call fails."""


class BinanceFuturesClient:
    """
    Thin wrapper around python-binance's UMFutures (USDT-M) client.

    Reads credentials from environment variables:
        BINANCE_API_KEY
        BINANCE_API_SECRET

    Configures the client to target the Testnet endpoint automatically.
    """

    def __init__(self) -> None:
        self._api_key: str = self._require_env("BINANCE_API_KEY")
        self._api_secret: str = self._require_env("BINANCE_API_SECRET")
        self._client = self._build_client()

    # ── Public interface ───────────────────────────────────────────────────────

    def new_order(self, **params: Any) -> Dict[str, Any]:
        """
        Place a new futures order.

        Args:
            **params: Keyword arguments forwarded directly to the Binance
                      new_order endpoint (symbol, side, type, quantity, …).

        Returns:
            Raw API response as a dict.

        Raises:
            BinanceClientError: On any API or network error.
        """
        logger.info("Placing order | payload=%s", params)
        try:
            response: Dict[str, Any] = self._client.new_order(**params)
            logger.info("Order response | %s", response)
            return response
        except Exception as exc:
            logger.error("Order placement failed | error=%s", exc, exc_info=True)
            raise BinanceClientError(str(exc)) from exc

    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Fetch exchange info (useful for symbol validation & precision rules).

        Returns:
            Raw exchange info dict from Binance.

        Raises:
            BinanceClientError: On any API or network error.
        """
        logger.debug("Fetching exchange info")
        try:
            info = self._client.exchange_info()
            logger.debug("Exchange info fetched successfully")
            return info
        except Exception as exc:
            logger.error("Failed to fetch exchange info | error=%s", exc)
            raise BinanceClientError(str(exc)) from exc

    def ping(self) -> bool:
        """
        Check connectivity to the testnet.

        Returns:
            True if the server is reachable, False otherwise.
        """
        try:
            self._client.ping()
            logger.debug("Testnet ping successful")
            return True
        except Exception as exc:
            logger.warning("Testnet ping failed | error=%s", exc)
            return False

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_client(self):
        """
        Instantiate and return the UMFutures client pointed at Testnet.

        Returns:
            binance.um_futures.UMFutures instance.

        Raises:
            BinanceClientError: If the library is missing or init fails.
        """
        try:
            from binance.um_futures import UMFutures  # type: ignore

            client = UMFutures(
                key=self._api_key,
                secret=self._api_secret,
                base_url=FUTURES_TESTNET_BASE_URL,
            )
            logger.info(
                "BinanceFuturesClient initialised | base_url=%s",
                FUTURES_TESTNET_BASE_URL,
            )
            return client
        except ImportError as exc:
            raise BinanceClientError(
                "python-binance is not installed. Run: pip install python-binance"
            ) from exc
        except Exception as exc:
            raise BinanceClientError(
                f"Failed to initialise Binance client: {exc}"
            ) from exc

    @staticmethod
    def _require_env(key: str) -> str:
        """
        Read a required environment variable.

        Args:
            key: Name of the environment variable.

        Returns:
            The variable's value.

        Raises:
            BinanceClientError: If the variable is missing or blank.
        """
        value = os.getenv(key, "").strip()
        if not value:
            raise BinanceClientError(
                f"Missing required environment variable: {key}. "
                "Copy .env.example to .env and fill in your Testnet credentials."
            )
        return value
