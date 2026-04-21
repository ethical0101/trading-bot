#!/usr/bin/env python3
"""
cli.py — Binance Futures Testnet Trading Bot CLI
=================================================

Entry point for placing MARKET, LIMIT, and STOP_LIMIT orders via the
command line.  Supports both flag-based and interactive prompt modes.

Usage examples
--------------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 60000

Stop-limit order:
    python cli.py --symbol ETHUSDT --side SELL --type STOP_LIMIT \\
        --quantity 0.1 --price 2900 --stop-price 2950

Interactive mode (no flags needed):
    python cli.py --interactive
"""

import argparse
import sys
from typing import Optional

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logging, get_logger
from bot.orders import OrderManager, OrderResult
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    cross_validate_args,
)

logger = get_logger("cli")

# ── ANSI colours (disabled automatically on non-TTY output) ───────────────────
_IS_TTY = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    """Wrap text in ANSI colour code if stdout is a TTY."""
    return f"\033[{code}m{text}\033[0m" if _IS_TTY else text


GREEN  = "32"
RED    = "31"
CYAN   = "36"
YELLOW = "33"
BOLD   = "1"
DIM    = "2"


# ── Argument parser ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--symbol",
        type=validate_symbol,
        help="Trading pair, e.g. BTCUSDT (uppercase)",
    )
    parser.add_argument(
        "--side",
        type=validate_side,
        help="Order direction: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        type=validate_order_type,
        dest="type",
        help="Order type: MARKET | LIMIT | STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity",
        type=validate_quantity,
        help="Trade quantity (must be > 0)",
    )
    parser.add_argument(
        "--price",
        type=validate_price,
        default=None,
        help="Limit price — required for LIMIT and STOP_LIMIT",
    )
    parser.add_argument(
        "--stop-price",
        type=validate_price,
        default=None,
        dest="stop_price",
        help="Stop trigger price — required for STOP_LIMIT",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=False,
        help="Launch interactive prompt to fill order details",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console log verbosity (default: INFO)",
    )
    return parser


# ── Interactive prompt mode ────────────────────────────────────────────────────

def interactive_prompt() -> argparse.Namespace:
    """
    Guide the user through order entry with interactive prompts.

    Returns:
        argparse.Namespace with validated order parameters.
    """
    _print_banner()
    print(_c("  Interactive Order Entry", BOLD))
    print(_c("  Press Ctrl-C at any time to cancel.\n", DIM))

    def _ask(prompt: str, validator, required: bool = True):
        while True:
            raw = input(f"  {prompt}: ").strip()
            if not required and raw == "":
                return None
            try:
                return validator(raw)
            except argparse.ArgumentTypeError as exc:
                print(_c(f"  ✗ {exc}", RED))

    symbol   = _ask("Symbol (e.g. BTCUSDT)", validate_symbol)
    side     = _ask("Side (BUY/SELL)", validate_side)
    otype    = _ask("Order type (MARKET/LIMIT/STOP_LIMIT)", validate_order_type)
    quantity = _ask("Quantity", validate_quantity)

    price      = None
    stop_price = None

    if otype in ("LIMIT", "STOP_LIMIT"):
        price = _ask("Limit price", validate_price)
    if otype == "STOP_LIMIT":
        stop_price = _ask("Stop trigger price", validate_price)

    print()

    ns = argparse.Namespace(
        symbol=symbol,
        side=side,
        type=otype,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        interactive=True,
        log_level="INFO",
    )
    return ns


# ── Output helpers ─────────────────────────────────────────────────────────────

def _print_banner() -> None:
    """Print the application banner."""
    print()
    print(_c("  ╔══════════════════════════════════════════╗", CYAN))
    print(_c("  ║   Binance Futures Testnet Trading Bot    ║", CYAN))
    print(_c("  ╚══════════════════════════════════════════╝", CYAN))
    print()


def _print_request_summary(args: argparse.Namespace) -> None:
    """
    Print a formatted request summary table.

    Args:
        args: Parsed and validated CLI arguments.
    """
    divider = _c("  " + "─" * 42, DIM)
    print(_c("  ── Request Summary ──────────────────────────", BOLD))
    print(divider)
    print(f"  {'Symbol':<16} {_c(args.symbol, YELLOW)}")
    print(f"  {'Side':<16} {_c(args.side, CYAN)}")
    print(f"  {'Order Type':<16} {args.type}")
    print(f"  {'Quantity':<16} {args.quantity}")

    if args.price is not None:
        print(f"  {'Limit Price':<16} {args.price}")
    if getattr(args, "stop_price", None) is not None:
        print(f"  {'Stop Price':<16} {args.stop_price}")

    print(divider)
    print()


def _print_order_result(result: OrderResult) -> None:
    """
    Print the API response and final status message.

    Args:
        result: Populated OrderResult from the order manager.
    """
    divider = _c("  " + "─" * 42, DIM)

    if result.success:
        print(_c("  ── Order Response ───────────────────────────", BOLD))
        print(divider)
        print(f"  {'Order ID':<16} {result.order_id}")
        print(f"  {'Status':<16} {_c(result.status or 'N/A', GREEN)}")
        print(f"  {'Executed Qty':<16} {result.executed_qty or '0'}")

        avg = result.avg_price
        if avg and float(avg) > 0:
            print(f"  {'Avg Price':<16} {avg}")

        print(divider)
        print()
        print(_c("  ✔  SUCCESS — Order placed successfully.", GREEN + ";" + BOLD))
    else:
        print(_c("  ── Error Details ────────────────────────────", BOLD))
        print(divider)
        print(f"  {_c(result.error or 'Unknown error', RED)}")
        print(divider)
        print()
        print(_c(f"  ✘  FAILED — {result.error}", RED + ";" + BOLD))

    print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    """
    Parse arguments, place the order, and print results.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = build_parser()
    args = parser.parse_args()

    # Bootstrap logging before anything else
    setup_logging(level=args.log_level)

    _print_banner()

    # ── Interactive mode ───────────────────────────────────────────────────────
    if args.interactive:
        try:
            args = interactive_prompt()
        except KeyboardInterrupt:
            print("\n\n  Cancelled by user.\n")
            return 0

    # ── Flag mode: ensure required fields are present ─────────────────────────
    else:
        missing = [
            flag for flag, val in [
                ("--symbol", args.symbol),
                ("--side", args.side),
                ("--type", args.type),
                ("--quantity", args.quantity),
            ]
            if val is None
        ]
        if missing:
            parser.error(
                f"The following arguments are required: {', '.join(missing)}\n"
                "  Tip: use --interactive for guided entry."
            )

    # ── Cross-field validation ─────────────────────────────────────────────────
    cross_validate_args(args)

    # ── Print what we're about to do ──────────────────────────────────────────
    _print_request_summary(args)

    # ── Initialise client ─────────────────────────────────────────────────────
    logger.info(
        "New order request | symbol=%s side=%s type=%s qty=%s",
        args.symbol, args.side, args.type, args.quantity,
    )

    try:
        client = BinanceFuturesClient()
    except BinanceClientError as exc:
        print(_c(f"  ✘  CLIENT ERROR — {exc}\n", RED))
        logger.error("Client init failed | %s", exc)
        return 1

    manager = OrderManager(client)

    # ── Dispatch by order type ─────────────────────────────────────────────────
    order_type: str = args.type

    if order_type == "MARKET":
        result = manager.place_market_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
        )

    elif order_type == "LIMIT":
        result = manager.place_limit_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            price=args.price,
        )

    else:  # STOP_LIMIT
        result = manager.place_stop_limit_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

    # ── Print results ──────────────────────────────────────────────────────────
    _print_order_result(result)

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
