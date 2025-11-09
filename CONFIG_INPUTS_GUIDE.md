# Configuration Inputs Guide (Exact locations to customize)

This document lists exactly where you should provide your inputs so the Trading Signal Generator works with your real environment and preferences. Each item names the file and line number(s), and explains what to change.

Note: Line numbers reflect the current repository state you shared.

---

## 1) API and data source settings
- **File**: `config.py`, **line 12**
  - `API_CONFIG['base_url'] = 'https://api.example.com'`
  - Replace with your actual market data API base URL.

- (Optional) **File**: `config.py`, **lines 13–14**
  - `API_CONFIG['timeout']`, `API_CONFIG['retry_attempts']`
  - Adjust based on your API reliability and latency.

- **File**: `trading_signal_generator.py`, **lines 38–47** (`TradingSignalGenerator.fetch_market_data()`)
  - Currently returns placeholder zeros.
  - Implement real API calls here using `API_CONFIG` to fetch live price, volume, VWAP, EMA-200, etc.
  - Example inputs needed: API key, symbol mapping, endpoint path, query params.

---

## 2) Trading universe and frequency
- **File**: `config.py`, **lines 16–24** (`TRADING_CONFIG`)
  - `watchlist`: Add/remove tickers you want to track.
  - `update_interval`: Set seconds between refreshes (used by UI for auto-refresh).
  - `max_trades_per_day`: Governance limit for downstream automation (if added).

- **File**: `trading_signal_generator.py`, **lines 134–140** (`main()` loop)
  - Uses `TRADING_CONFIG['watchlist']` to iterate symbols when running the script directly.

---

## 3) Option chain and model thresholds
- **File**: `config.py`, **lines 27–32** (`OPTION_CHAIN_CONFIG`)
  - `strikes_to_consider`, `oi_change_threshold`, `pcr_threshold`, `iv_stable_threshold`
  - Tune to your strategy and data characteristics.

- **File**: `config.py`, **lines 35–60** (`SCORING_WEIGHTS`)
  - Weights for each factor contributing to the total score.
  - Adjust to calibrate the scoring model to your beliefs/backtests.

---

## 4) Alerting and decision threshold
- **File**: `config.py`, **lines 69–74** (`ALERT_CONFIG`)
  - `min_confidence_score`: Minimum total score to mark action as BUY in backend logic.
  - `alert_methods`: e.g., `['console', 'email']`
  - `email_recipient`: Replace `your.email@example.com` with your real email if you add email sending.

- **File**: `streamlit_app.py`
  - The UI uses its own slider threshold for BUY/HOLD without mutating `config.py`. Use the sidebar slider at runtime if you prefer not to edit files.

---

## 5) Timezone and market hours
- **File**: `config.py`, **lines 83–88** (`TIME_CONFIG`)
  - `timezone`: Replace if your region differs (e.g., `Asia/Kolkata`).
  - `market_open`, `market_close`: Optional use in future scheduling/filters.

---

## 6) File paths and logging
- **File**: `config.py`, **lines 62–67** (`FILE_PATHS`)
  - `trade_log`, `backtest_data`, `logs`: Adjust storage locations if needed.

- **File**: `trading_signal_generator.py`, **lines 118–125** (`log_signal()`)
  - Excel log path is hardcoded to `data/trade_signals.xlsx`.
  - If you want a single source of truth via `config.py`, update this to use `FILE_PATHS['trade_log']` (currently `data/trade_log.xlsx`) or change `FILE_PATHS['trade_log']` to match `data/trade_signals.xlsx`.

- **File**: `config.py`, **lines 90–96** (`LOGGING_CONFIG`)
  - Adjust log level/format/rotation as per your operations needs.

---

## 7) Streamlit UI controls (no code change required)
- **File**: `streamlit_app.py`
  - Modify UI defaults if desired:
    - Default selected symbols use the first items of `TRADING_CONFIG['watchlist']`.
    - Auto-refresh interval defaults to `TRADING_CONFIG['update_interval']`.
    - BUY/HOLD threshold controlled by the sidebar slider.

---

## 8) Places you will most likely edit first
1. `config.py:12` → Set `API_CONFIG['base_url']` to your real data API.
2. `trading_signal_generator.py:38–47` → Implement `fetch_market_data()` using your API (auth headers, params, response parsing).
3. `config.py:16–24` → Update `TRADING_CONFIG['watchlist']` and `update_interval`.
4. `config.py:69–74` → Set `ALERT_CONFIG['min_confidence_score']` and your `email_recipient` if using email.
5. Reconcile trade log path:
   - Either change `trading_signal_generator.py:119` to use `FILE_PATHS['trade_log']`, or
   - Change `config.py:64` to `data/trade_signals.xlsx`.

---

## 9) After making changes
- Reinstall dependencies only if you add new packages.
- Run the UI:
  ```powershell
  .\.venv\Scripts\streamlit.exe run streamlit_app.py
  ```
- Use the UI slider to experiment with thresholds before changing config constants.

---

## Questions / Next steps
If you share your target market data API (docs or sample response), I can implement `fetch_market_data()` for you and align symbol mapping, auth, and error handling.
