# Runbook (Windows): Setup and Run after GitHub Clone

Follow these steps exactly after downloading/cloning the repository from GitHub.
All commands are for Windows PowerShell, executed from the project folder.

Repo: https://github.com/dixankur/trading_signal_automation_Swaraj

---

## 1) Download or clone the repository

- Option A: Clone with Git
```powershell
git clone https://github.com/dixankur/trading_signal_automation_Swaraj.git
cd trading_signal_automation_Swaraj
```

- Option B: Download ZIP
  - Download ZIP from GitHub → Extract → Right-click inside the extracted folder → Open in Terminal.

---

## 2) Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 3) Create your local .env (NOT in Git)

- Copy the example and fill your secrets:
```powershell
Copy-Item .env.example .env
```
- Open `.env` in a text editor and set values (examples):
```
# Zerodha web login
ZERODHA_BASE_URL=https://kite.zerodha.com
ZERODHA_USERNAME=<your_user>
ZERODHA_PASSWORD=<your_pass>
ZERODHA_TOTP=<your_totp_secret>

# Telegram (optional)
TELEGRAM_NOTIFY=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Kite Connect (optional; enables true VWAP/EMA-200)
KITE_API_KEY=
KITE_ACCESS_TOKEN=
```
Notes:
- `.env` is required for Zerodha login. Without it the app cannot fetch LTP.
- Kite Connect keys are optional but required for historical VWAP/EMA-200.

---

## 4) Run the Streamlit app

```powershell
.\.venv\Scripts\streamlit.exe run streamlit_app.py
```

- Browser will open at http://localhost:8501
- In the sidebar:
  - Select symbols from the watchlist
  - Set “Min Confidence Score for BUY” threshold
  - Optionally enable “Auto Refresh” and choose interval
- Main table shows: timestamp, symbol, exchange, price, vwap, ema_200, action, confidence_score
- History reads from `data/trade_signals.xlsx` (auto-created on first signal)

---

## 5) Troubleshooting

- Stop the app: press Ctrl + C in the terminal.
- Port busy (8501):
```powershell
netstat -ano | findstr :8501
# Note the PID and then:
taskkill /PID <PID> /F
```
- TOTP/login failures:
  - Check `.env` values; TOTP must be current.
  - Retry running the app.
- Historical data (VWAP/EMA-200) missing:
  - Provide `KITE_API_KEY` and `KITE_ACCESS_TOKEN` in `.env`.
- Indices or symbols not showing price:
  - Share symbol list with maintainer; exchange routing may need an update.

---

## 6) Optional: Enable Telegram alerts

- In `.env`:
```
TELEGRAM_NOTIFY=true
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_CHAT_ID=<your_chat_id>
```
- The app will send a message each time a signal is generated.

---

## 7) Update/Upgrade

- Pull latest code:
```powershell
git pull
```
- Reinstall dependencies when `requirements.txt` changes:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 8) Quick recap

1. Clone or download the repo.
2. Create venv and install requirements.
3. Copy `.env.example` to `.env` and fill credentials.
4. Run `streamlit_app.py`.
5. Use the UI to generate and view signals.
