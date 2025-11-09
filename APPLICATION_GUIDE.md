<!--
 Author: Ankur Dixit
 Date: 2025-10-19
 -->
# Trading Signal Automation – Application Guide

This document explains how the app works, what you can change, and how to run it. It is written for non-developers in simple, step-by-step language.

- Project folder: `c:/Users/Ankur/Downloads/Projects/trading_signal_automation/`
- Main files:
  - `trading_signal_generator.py` – runs the app and generates signals
  - `config.py` – settings you can change (watchlist, thresholds, paths, etc.)

---

## 1) How the app works (simple flow)

1. **Start the app**
   - You run `trading_signal_generator.py`.
   - The app creates folders `data/` and `logs/` if they don’t exist.

2. **Read your settings**
   - The app loads all your settings from `config.py`.

3. **Go through each stock/symbol**
   - The app looks at every symbol listed in `TRADING_CONFIG['watchlist']` from `config.py`.

4. **Get market data (placeholder now)**
   - The app calls `fetch_market_data(symbol)` in `trading_signal_generator.py`.
   - Right now it returns dummy values (price, volume, etc.). You can connect this to a real API later (see section 4).

5. **Calculate a score**
   - The app calculates different parts of a score (price action, OI dynamics, PCR/Max Pain, etc.) using the weights in `SCORING_WEIGHTS` from `config.py`.
   - The parts are added up to a `total_score`.

6. **Make a decision**
   - If `total_score` is greater than or equal to `ALERT_CONFIG['min_confidence_score']`, action = `BUY`; otherwise, action = `HOLD`.

7. **Save results**
   - The app prints the result to the screen.
   - It also adds a new row to `data/trade_signals.xlsx` with the symbol, time, action, and score.

---

## 2) Things you can change (user settings)

All settings are in: `config.py`.

- **API settings** – `API_CONFIG`
  - `base_url`: Put your data provider base URL here when you connect to a real API.
  - `timeout`, `retry_attempts`: Network settings.

- **Trading parameters** – `TRADING_CONFIG`
  - `watchlist`: The list of symbols you want to process. Example: `['NIFTY', 'RELIANCE', ...]`
  - `update_interval`: If you add a scheduler later, this will be the seconds between runs.
  - `max_trades_per_day`: A cap to control how many trades per day (for future logic).

- **Option chain parameters** – `OPTION_CHAIN_CONFIG`
  - `strikes_to_consider`: How many strikes around ATM to consider.
  - `oi_change_threshold`: Minimum OI change to count.
  - `pcr_threshold`: PCR level you consider meaningful.
  - `iv_stable_threshold`: How much IV can change to be considered stable.

- **Scoring weights** – `SCORING_WEIGHTS`
  - These numbers decide how important each factor is.
  - Example keys: `option_oi_dynamics`, `pcr_max_pain`, `gamma_dealer_flow`, `price_action`, `volatility_greeks`, `volume_confirmation`.
  - Increase a weight to make that factor more important in the final score.

- **Alert settings** – `ALERT_CONFIG`
  - `min_confidence_score`: Minimum score to trigger `BUY`. Increase it to be stricter.
  - `alert_methods`: Currently `['console', 'email']` (email is a placeholder; add logic later).
  - `email_recipient`: Where to send emails if you add email logic.

- **File paths** – `FILE_PATHS`
  - `trade_log`, `backtest_data`, `logs`: Update these if you want different locations.

- **Backtesting settings** – `BACKTEST_CONFIG`
  - `initial_capital`, `risk_per_trade`, `commission_rate`.

- **Time settings** – `TIME_CONFIG`
  - `market_open`, `market_close`, `timezone` (used for timestamps).

- **Logging settings** – `LOGGING_CONFIG`
  - `level`, `format`, `max_size_mb`, `backup_count` (log rotation can be wired later). Currently basic logging to console is used.

---

## 3) Where the logic lives (for later improvements)

- File: `trading_signal_generator.py`
  - Function: `TradingSignalGenerator.fetch_market_data(symbol)`
    - Purpose: Get live market data for `price`, `volume`, `vwap`, `ema_200`.
    - Current state: Returns placeholder values. Replace with real API calls using `API_CONFIG` from `config.py`.

  - Function: `TradingSignalGenerator.calculate_scores(symbol)`
    - Purpose: Calculate the sub-scores and combine them to `total_score`.
    - Current state: Some parts are placeholders. Use your real data for OI dynamics, PCR/Max Pain, etc., and then apply weights from `SCORING_WEIGHTS`.

  - Function: `TradingSignalGenerator.generate_signal(symbol)`
    - Purpose: Build the final signal (`BUY` or `HOLD`) based on `total_score` and `ALERT_CONFIG['min_confidence_score']`.

  - Function: `TradingSignalGenerator.log_signal(signal)`
    - Purpose: Print the signal and save it to Excel at `data/trade_signals.xlsx`.

- File: `config.py`
  - Purpose: Central place for all settings you can change without touching code logic.

---

## 4) How to implement real data (optional next step)

1. Pick a data provider (for example, your broker API or a market data API).
2. Put the base URL in `API_CONFIG['base_url']` in `config.py`.
3. In `trading_signal_generator.py`, update `fetch_market_data(symbol)`
   - Make a request to your API.
   - Parse the response to fill: `price`, `volume`, `vwap`, `ema_200`.
4. If you need authentication (API keys), store the key safely (environment variable) and read it in your function. Do not hardcode secrets in files.
5. Test one symbol first, then expand to the full watchlist.

---

## 5) How to run the app

1. Install Python packages (run in a terminal):
   ```bash
   pip install pandas numpy pytz openpyxl
   ```
2. Run the program:
   ```bash
   python trading_signal_generator.py
   ```
3. Check results:
   - See output messages in the terminal.
   - Open the file: `data/trade_signals.xlsx`.

If you get an error about Excel writing, ensure `openpyxl` is installed (included above) and the `data/` folder exists (the app creates it automatically).

---

## 6) Recommended actions (next steps)

- **Connect real data**: Implement `fetch_market_data()` with your API.
- **Fill in OI/PCR logic**: Update `calculate_scores()` to use real OI/PCR/Max Pain and other factors.
- **Tune thresholds and weights**: Adjust `ALERT_CONFIG['min_confidence_score']` and `SCORING_WEIGHTS` to match your strategy.
- **Optional alerts**: Add email/SMS/Webhook sending inside `log_signal()` or a new alert function based on `ALERT_CONFIG['alert_methods']`.
- **Documentation**: Keep `config.py` comments updated as you refine the strategy.

---

## 7) Quick reference (what to change and where)

- Symbols list: `config.py` → `TRADING_CONFIG['watchlist']`
- Buy threshold: `config.py` → `ALERT_CONFIG['min_confidence_score']`
- Scoring importance: `config.py` → `SCORING_WEIGHTS`
- Market data source: `trading_signal_generator.py` → `fetch_market_data()`
- Output file path: `config.py` → `FILE_PATHS['trade_log']` (note: the generator currently writes `data/trade_signals.xlsx` directly)
- Timezone: `config.py` → `TIME_CONFIG['timezone']`

---

If you need this guide updated as the app grows, ask for an update and we will keep it simple and clear.
