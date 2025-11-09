"""
Streamlit UI for the Trading Signal Generator

Author: Ankur Dixit
Date: 2025-11-01
"""

import os
from datetime import datetime
from typing import List, Dict

import pandas as pd
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config import TRADING_CONFIG, ALERT_CONFIG, TIME_CONFIG
from trading_signal_generator import TradingSignalGenerator


# ---------- Helpers ----------

def load_trade_log(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        try:
            return pd.read_excel(path)
        except Exception:
            # Fallback if Excel engine or file has an issue
            return pd.DataFrame()
    return pd.DataFrame()


def generate_signals(tsg: TradingSignalGenerator, symbols: List[str]) -> pd.DataFrame:
    rows: List[Dict] = []
    for sym in symbols:
        try:
            sig = tsg.generate_signal(sym)
            rows.append({
                "timestamp": sig["timestamp"],
                "symbol": sig["symbol"],
                "action": sig["action"],
                "confidence_score": sig["confidence_score"],
            })
        except Exception as e:
            rows.append({
                "timestamp": datetime.now(pytz.timezone(TIME_CONFIG["timezone"])),
                "symbol": sym,
                "action": f"ERROR: {e}",
                "confidence_score": None,
            })
    df = pd.DataFrame(rows)
    if not df.empty and "timestamp" in df.columns:
        df = df.sort_values("timestamp", ascending=False)
    return df


# ---------- Streamlit UI ----------

st.set_page_config(page_title="Trading Signal Generator", page_icon="📈", layout="wide")

st.title("📈 Trading Signal Generator")

col_a, col_b = st.columns([2, 1])
with col_a:
    st.markdown("Use this UI to generate and view trading signals based on your configured scoring system in `config.py`.")
with col_b:
    tz = pytz.timezone(TIME_CONFIG["timezone"]) if TIME_CONFIG.get("timezone") else pytz.UTC
    st.metric("Current Time", datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"))

with st.sidebar:
    st.header("Controls")
    default_watchlist = TRADING_CONFIG.get("watchlist", [])
    selected_symbols = st.multiselect(
        "Select Symbols",
        options=default_watchlist,
        default=default_watchlist[:5] if len(default_watchlist) > 0 else [],
        help="Symbols come from TRADING_CONFIG['watchlist']"
    )

    min_conf_default = ALERT_CONFIG.get("min_confidence_score", 60)
    min_conf = st.slider("Min Confidence Score for BUY", 0, 100, int(min_conf_default), step=1,
                         help="Signals with total score >= this threshold will be marked as BUY")

    update_interval = st.slider("Auto-refresh Interval (seconds)", 5, 300, int(TRADING_CONFIG.get("update_interval", 60)))

    auto_refresh = st.toggle("Auto Refresh", value=False, help="If enabled, the app will refresh at the set interval.")

    st.divider()
    st.caption("Data files are written to `data/`. Recent signals are read from `data/trade_signals.xlsx`.")

# Allow runtime override of threshold without mutating module-level config
ALERT_CONFIG_RUNTIME = dict(ALERT_CONFIG)
ALERT_CONFIG_RUNTIME["min_confidence_score"] = int(min_conf)

# Patch TradingSignalGenerator use of ALERT_CONFIG by monkey-patching module import if necessary
# Here we rely on generate_signal using ALERT_CONFIG dict at import time. To keep things simple,
# we'll pass through as-is and let the threshold be used during action decision.

# Create generator
if "_tsg" not in st.session_state:
    st.session_state["_tsg"] = TradingSignalGenerator()

tsg: TradingSignalGenerator = st.session_state["_tsg"]

# Action buttons
left, right = st.columns([1, 3])
run_clicked = False
with left:
    run_clicked = st.button("Generate Signals Now", type="primary")

if auto_refresh:
    # Auto-refresh the app at the selected interval (milliseconds)
    st_autorefresh(interval=int(update_interval * 1000), key="auto_refresh")

# Core content
if not selected_symbols:
    st.info("Please select at least one symbol from the sidebar.")
    st.stop()

# Generate if requested
signals_df = pd.DataFrame()
if run_clicked or auto_refresh:
    # Temporary override: adjust the generator's BUY threshold decision by wrapping generate_signal
    # We'll compute scores and decide action locally to honor min_conf slider without modifying backend.
    rows = []
    tz = pytz.timezone(TIME_CONFIG["timezone"])
    for sym in selected_symbols:
        # Get market data with price/VWAP/EMA200/exchange
        md = tsg.fetch_market_data(sym)
        scores = tsg.calculate_scores(sym)
        action = "BUY" if scores.get("total_score", 0) >= ALERT_CONFIG_RUNTIME["min_confidence_score"] else "HOLD"
        sig = {
            "symbol": sym,
            "timestamp": datetime.now(tz),
            "action": action,
            "confidence_score": scores.get("total_score", 0),
            "scores": scores,
        }
        # Log via existing logger/excel writer for consistent history
        try:
            tsg.log_signal(sig)
        except Exception:
            pass
        rows.append({
            "timestamp": sig["timestamp"],
            "symbol": sig["symbol"],
            "exchange": md.get("exchange"),
            "price": md.get("price"),
            "vwap": md.get("vwap"),
            "ema_200": md.get("ema_200"),
            "action": sig["action"],
            "confidence_score": sig["confidence_score"],
        })
    signals_df = pd.DataFrame(rows).sort_values("timestamp", ascending=False)

# Layout: current run and recent history
c1, c2 = st.columns([3, 2])
with c1:
    st.subheader("Current Run Signals")
    if signals_df.empty:
        st.caption("Click 'Generate Signals Now' to produce signals.")
    else:
        st.dataframe(signals_df, width='stretch')
        # Download
        csv = signals_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Current Signals as CSV", data=csv, file_name="signals.csv", mime="text/csv")

with c2:
    st.subheader("Recent Signals (from Excel log)")
    trade_log_path = os.path.join("data", "trade_signals.xlsx")
    history_df = load_trade_log(trade_log_path)
    if history_df.empty:
        st.caption("No history yet. Generate signals to create the log.")
    else:
        # Show last 50 by timestamp if available
        if "timestamp" in history_df.columns:
            # Ensure timestamp is datetime
            try:
                history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
            except Exception:
                pass
            history_df = history_df.sort_values("timestamp", ascending=False).head(50)
        st.dataframe(history_df, width='stretch', height=400)

st.divider()
with st.expander("Advanced Details"):
    st.write("Configured Watchlist:", TRADING_CONFIG.get("watchlist", []))
    st.write("Scoring threshold (current session):", ALERT_CONFIG_RUNTIME["min_confidence_score"])
    st.write("Timezone:", TIME_CONFIG.get("timezone"))
