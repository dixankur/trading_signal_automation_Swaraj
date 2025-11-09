# Credentials and API Setup

This guide shows how to transfer credentials and endpoints from `Project2_EMA921_v4.py` into this project's secure configuration.

Important: Do NOT paste secrets into code. Use `.env` for secrets. Keep `.env` out of version control.

---

## 1) Values to copy from EMA script

From `Project2_EMA921_v4.py` (line numbers may vary slightly):

- Users block (lines ~28–31):
  - `username`, `password`, `totp` for Zerodha login
- Zerodha base URLs (lines ~116–119):
  - `base_url = "https://kite.zerodha.com"`
  - `login_url`, `totp_url` derived from base
- Telegram (lines ~34–37):
  - `TelegramBotCredential` (bot token)
  - `ReceiverTelegramID` (chat ID)
  - `Telegram_Notification` (True/False)

Do not commit these raw values. Place them in `.env` as shown below.

---

## 2) Fill .env using .env.example

Create a new file `.env` in `trading_signal_automation/` by copying `.env.example` and fill values:

```
ZERODHA_BASE_URL=https://kite.zerodha.com
ZERODHA_USERNAME=AZ4855
ZERODHA_PASSWORD=<your_password>
ZERODHA_TOTP=<your_totp_secret>

TELEGRAM_NOTIFY=true
TELEGRAM_BOT_TOKEN=<8031...gno>
TELEGRAM_CHAT_ID=<-1002420364359>

INSTRUMENTS_CSV_URL=https://api.kite.trade/instruments
```

Keep `.env` private. Do not commit.

---

## 3) Where these are used in code

- `config.py`:
  - `BROKER_CONFIG` uses `ZERODHA_*` for login
  - `TELEGRAM_CONFIG` uses `TELEGRAM_*`
  - `DATA_SOURCES['instruments_csv']` defaults to Kite instruments list
  - `API_CONFIG['base_url']` set to `https://kite.zerodha.com`

- `trading_signal_generator.py` (to be implemented):
  - `fetch_market_data(symbol)` should read from `BROKER_CONFIG`/`API_CONFIG` and call the real endpoint.

---

## 4) Next coding steps (I can implement)

- Implement `fetch_market_data()` to retrieve price/volume/VWAP/EMA from Zerodha source (or alternate you provide).
- Optionally add Telegram notifications using `TELEGRAM_CONFIG`.
- Align Excel log path with `FILE_PATHS['trade_log']` for consistency.

---

## 5) Security reminders

- Never hardcode usernames/passwords/TOTP in code.
- Keep `.env` local only; rotate tokens if exposed.
- Limit bot token permissions and chat IDs as needed.
