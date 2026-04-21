"""
Input validation for CLI arguments.
All validators raise argparse.ArgumentTypeError on failure so argparse
can surface clean, consistent error messages to the user.
"""

import argparse
from typing import Optional


# ── Allowed constants ──────────────────────────────────────────────────────────
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


def validate_symbol(value: str) -> str:
    """
    Ensure the trading symbol is non-empty and uppercase.

    Args:
        value: Raw symbol string from CLI.

    Returns:
        Uppercased symbol string.

    Raises:
        argparse.ArgumentTypeError: If the symbol is blank.
    """
    symbol = value.strip().upper()
    if not symbol:
        raise argparse.ArgumentTypeError("Symbol must not be empty.")
    return symbol


def validate_side(value: str) -> str:
    """
    Ensure side is BUY or SELL.

    Args:
        value: Raw side string from CLI.

    Returns:
        Uppercased side string.

    Raises:
        argparse.ArgumentTypeError: If side is not in VALID_SIDES.
    """
    side = value.strip().upper()
    if side not in VALID_SIDES:
        raise argparse.ArgumentTypeError(
            f"Side must be one of {sorted(VALID_SIDES)}. Got: '{value}'"
        )
    return side


def validate_order_type(value: str) -> str:
    """
    Ensure order type is MARKET, LIMIT, or STOP_LIMIT.

    Args:
        value: Raw order type string from CLI.

    Returns:
        Uppercased order type string.

    Raises:
        argparse.ArgumentTypeError: If type is not in VALID_ORDER_TYPES.
    """
    order_type = value.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise argparse.ArgumentTypeError(
            f"Order type must be one of {sorted(VALID_ORDER_TYPES)}. Got: '{value}'"
        )
    return order_type


def validate_quantity(value: str) -> float:
    """
    Ensure quantity is a positive float.

    Args:
        value: Raw quantity string from CLI.

    Returns:
        Parsed positive float.

    Raises:
        argparse.ArgumentTypeError: If the value is not a valid positive number.
    """
    try:
        qty = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Quantity must be a number. Got: '{value}'"
        )
    if qty <= 0:
        raise argparse.ArgumentTypeError(
            f"Quantity must be greater than 0. Got: {qty}"
        )
    return qty


def validate_price(value: str) -> float:
    """
    Ensure price is a positive float (used for LIMIT / STOP_LIMIT orders).

    Args:
        value: Raw price string from CLI.

    Returns:
        Parsed positive float.

    Raises:
        argparse.ArgumentTypeError: If the value is not a valid positive number.
    """
    try:
        price = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Price must be a number. Got: '{value}'"
        )
    if price <= 0:
        raise argparse.ArgumentTypeError(
            f"Price must be greater than 0. Got: {price}"
        )
    return price


def cross_validate_args(args: argparse.Namespace) -> None:
    """
    Perform cross-field validation that cannot be done per-argument.

    Checks:
      - LIMIT orders require --price
      - STOP_LIMIT orders require both --price and --stop-price

    Args:
        args: Parsed argparse Namespace.

    Raises:
        SystemExit: Prints a user-friendly error message and exits with code 2.
    """
    order_type: str = args.type

    if order_type == "LIMIT" and args.price is None:
        _exit_with_error("--price is required for LIMIT orders.")

    if order_type == "STOP_LIMIT":
        if args.price is None:
            _exit_with_error("--price (limit price) is required for STOP_LIMIT orders.")
        if args.stop_price is None:
            _exit_with_error("--stop-price is required for STOP_LIMIT orders.")


def _exit_with_error(message: str) -> None:
    """Print a formatted error and exit."""
    print(f"\n[ERROR] Validation failed: {message}\n")
    raise SystemExit(2)
