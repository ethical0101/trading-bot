# Binance Futures Testnet Trading Bot

A production-quality CLI trading bot for the **Binance USDT-M Futures Testnet**.  
Supports **MARKET**, **LIMIT**, and **STOP_LIMIT** orders with clean structured output, full logging, and robust error handling.

---

## Features

- Place **MARKET** orders (instant execution at best available price)
- Place **LIMIT** orders (execute at a specific price or better)
- Place **STOP_LIMIT** orders (trigger a limit order when the market hits a stop price)
- **Interactive prompt mode** — guided entry without memorising flags
- Structured console output — request summary + API response + final status
- Full logging to `trading_bot.log` (DEBUG) and console (INFO)
- `.env`-based credential management — no secrets in source code

---

## Project Structure

```
trading_bot/
│
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Binance API wrapper (UMFutures + testnet config)
│   ├── orders.py            # Order placement logic + OrderResult dataclass
│   ├── validators.py        # Per-field and cross-field CLI validation
│   └── logging_config.py   # File + console logging setup
│
├── cli.py                   # CLI entry point (argparse, output formatting)
├── requirements.txt         # Python dependencies
├── .env.example             # Credential template
└── README.md
```

---

## Prerequisites

- Python 3.9+
- A free account on [Binance Futures Testnet](https://testnet.binancefuture.com)

---

## Setup

### 1. Clone / download the project

```bash
git clone <repo-url>
cd trading_bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Testnet credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your Testnet API key and secret:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **How to get Testnet credentials**  
> 1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)  
> 2. Log in with your GitHub account  
> 3. Navigate to **API Management** and generate a key pair  

---

## Usage

### Flag-based mode

**Market order**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit order**
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 60000
```

**Stop-Limit order**
```bash
python cli.py --symbol ETHUSDT --side SELL --type STOP_LIMIT \
    --quantity 0.1 --price 2900 --stop-price 2950
```

**Sell market order**
```bash
python cli.py --symbol SOLUSDT --side SELL --type MARKET --quantity 1
```

### Interactive mode

Run without flags and the bot will prompt you for each field:

```bash
python cli.py --interactive
# or
python cli.py -i
```

### Log verbosity

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --log-level DEBUG
```

---

## CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--symbol` | Yes (flag mode) | Trading pair, e.g. `BTCUSDT` (auto-uppercased) |
| `--side` | Yes (flag mode) | `BUY` or `SELL` |
| `--type` | Yes (flag mode) | `MARKET`, `LIMIT`, or `STOP_LIMIT` |
| `--quantity` | Yes (flag mode) | Float > 0 |
| `--price` | LIMIT / STOP_LIMIT | Limit execution price |
| `--stop-price` | STOP_LIMIT only | Trigger price for stop-limit |
| `--interactive` / `-i` | No | Launch guided prompt mode |
| `--log-level` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` (default: `INFO`) |

---

## Output Example

```
  ╔══════════════════════════════════════════╗
  ║   Binance Futures Testnet Trading Bot    ║
  ╚══════════════════════════════════════════╝

  ── Request Summary ──────────────────────────
  ──────────────────────────────────────────
  Symbol           BTCUSDT
  Side             BUY
  Order Type       LIMIT
  Quantity         0.01
  Limit Price      60000.0
  ──────────────────────────────────────────

  ── Order Response ───────────────────────────
  ──────────────────────────────────────────
  Order ID         3492875423
  Status           NEW
  Executed Qty     0
  ──────────────────────────────────────────

  ✔  SUCCESS — Order placed successfully.
```

---

## Logging

All activity is written to `trading_bot.log` in the project root.

| Level | Content |
|---|---|
| `DEBUG` | Full API request payloads, raw responses, connection details |
| `INFO` | Order dispatched, order response summary |
| `ERROR` | API errors, network failures, validation failures |

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `--price` for LIMIT | Validation error before any API call |
| Missing `--price` / `--stop-price` for STOP_LIMIT | Validation error before any API call |
| Invalid symbol / side / type | argparse error with clear message |
| Quantity ≤ 0 | argparse error with clear message |
| Missing `.env` credentials | Clear error message pointing to `.env.example` |
| Binance API error (e.g. insufficient margin) | Error code + message printed and logged |
| Network failure / timeout | Exception caught, logged, printed |

---

## Security Notes

- **Never commit `.env`** — it is listed in `.gitignore` by convention.
- These credentials are for the **Testnet only** — they have no value on mainnet.
- API keys are read from environment variables, never hardcoded.
