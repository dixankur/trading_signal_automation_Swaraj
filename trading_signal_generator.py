"""
Trading Signal Generator - Core logic for generating trading signals.
 
Author: Ankur Dixit
Date: 2025-10-19
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
from typing import Dict, List, Optional
import requests
import pyotp

# Import configuration
from config import (
    TRADING_CONFIG, OPTION_CHAIN_CONFIG, SCORING_WEIGHTS,
    ALERT_CONFIG, TIME_CONFIG, FILE_PATHS, BROKER_CONFIG, TELEGRAM_CONFIG, DATA_SOURCES, KITE_CONNECT
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingSignalGenerator:
    """Generates trading signals based on the specified scoring system."""

    def __init__(self):
        self.market_data = {}
        self.option_chain_data = {}
        self.setup_directories()
        self.session: Optional[requests.Session] = None
        self.enctoken: Optional[str] = None
        self.base_url: str = BROKER_CONFIG.get('base_url', 'https://kite.zerodha.com')
        self.instruments_df: Optional[pd.DataFrame] = None
        self.kite_api_key: str = KITE_CONNECT.get('api_key', '')
        self.kite_access_token: str = KITE_CONNECT.get('access_token', '')
        
    def setup_directories(self):
        """Create necessary directories."""
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

    def _ensure_session(self):
        """Ensure we have a logged-in Zerodha web session and enctoken."""
        if self.session and self.enctoken:
            return
        username = BROKER_CONFIG.get('username')
        password = BROKER_CONFIG.get('password')
        totp_secret = BROKER_CONFIG.get('totp_secret')
        if not (username and password and totp_secret):
            raise RuntimeError("Missing Zerodha credentials in environment (.env): ZERODHA_USERNAME/PASSWORD/TOTP")
        s = requests.Session()
        try:
            login_url = f"{self.base_url}/api/login"
            twofa_url = f"{self.base_url}/api/twofa"
            s.get(self.base_url, timeout=10)
            res = s.post(login_url, data={"user_id": username, "password": password}, timeout=15)
            res.raise_for_status()
            data = res.json().get('data') or {}
            request_id = data.get('request_id')
            if not request_id:
                raise RuntimeError("Login failed: request_id not received")
            twofa_payload = {
                "user_id": username,
                "request_id": request_id,
                "twofa_value": pyotp.TOTP(totp_secret).now(),
            }
            res2 = s.post(twofa_url, data=twofa_payload, timeout=15)
            res2.raise_for_status()
            enc = res2.cookies.get("enctoken")
            if not enc:
                raise RuntimeError("Login failed: enctoken not received")
            # Set auth header for subsequent requests
            s.headers.update({"authorization": f"enctoken {enc}"})
            self.session = s
            self.enctoken = enc
        except Exception as e:
            raise RuntimeError(f"Zerodha web session login failed: {e}")

    def _load_instruments(self):
        """Load instruments CSV once and cache it for symbol -> token/exchange mapping."""
        if self.instruments_df is not None:
            return
        url = DATA_SOURCES.get('instruments_csv')
        try:
            df = pd.read_csv(url)
            # Normalize columns
            if 'tradingsymbol' not in df.columns and 'tradingsymbol' in df.columns:
                pass
            self.instruments_df = df
        except Exception as e:
            logger.warning(f"Failed to load instruments CSV: {e}")
            self.instruments_df = pd.DataFrame()

    def _resolve_exchange_and_token(self, symbol: str) -> Dict:
        """Try to resolve exchange and instrument_token for a symbol using instruments CSV."""
        self._load_instruments()
        exchange = 'NSE'
        token = None
        if self.instruments_df is not None and not self.instruments_df.empty:
            # Match exact tradingsymbol first
            rows = self.instruments_df[self.instruments_df['tradingsymbol'] == symbol]
            if rows.empty:
                # Some lists might use 'name' for equities
                rows = self.instruments_df[(self.instruments_df.get('name', pd.Series([])) == symbol) & (self.instruments_df['exchange'] == 'NSE')]
            if not rows.empty:
                # Prefer non-expiry (equity) or nearest expiry
                row = rows.sort_values(by=['expiry'], ascending=True, na_position='last').iloc[0] if 'expiry' in rows.columns else rows.iloc[0]
                exchange = row.get('exchange', 'NSE')
                token = row.get('instrument_token')
        # Basic mapping for known indices if not found
        index_symbols = {'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'NIFTYNXT50'}
        if symbol in index_symbols:
            exchange = 'NSE'
        return {'exchange': exchange, 'instrument_token': token}

    def _kite_headers(self) -> Optional[Dict[str, str]]:
        if not (self.kite_api_key and self.kite_access_token):
            return None
        return {
            'X-Kite-Version': '3',
            'Authorization': f'token {self.kite_api_key}:{self.kite_access_token}',
        }

    def _fetch_historical(self, instrument_token: int, interval: str = 'minute', lookback_minutes: int = 300) -> Optional[pd.DataFrame]:
        """Fetch historical candles via Kite REST if credentials available."""
        headers = self._kite_headers()
        if headers is None:
            return None
        try:
            to_ts = datetime.utcnow()
            from_ts = to_ts - timedelta(minutes=lookback_minutes)
            url = f"https://api.kite.trade/instruments/historical/{int(instrument_token)}/{interval}"
            params = {
                'from': from_ts.strftime('%Y-%m-%d %H:%M:%S'),
                'to': to_ts.strftime('%Y-%m-%d %H:%M:%S'),
            }
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json().get('data', {}).get('candles', [])
            if not data:
                return None
            df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            logger.warning(f"Historical fetch failed for token {instrument_token}: {e}")
            return None

    def fetch_market_data(self, symbol: str) -> Dict:
        """Fetch market data for given symbol."""
        # Ensure session
        self._ensure_session()
        tz = pytz.timezone(TIME_CONFIG['timezone'])
        # Resolve exchange via instruments map if possible
        resolved = self._resolve_exchange_and_token(symbol)
        exchange = resolved['exchange'] or 'NSE'
        instrument_token = resolved['instrument_token']
        price = 0.0
        try:
            # Zerodha web LTP endpoint
            url = f"{self.base_url}/oms/quote/ltp?i={exchange}:{symbol}"
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            payload = r.json().get('data') or {}
            # Try to read last_price from known keys
            key = f"{exchange}:{symbol}"
            item = payload.get(key) or {}
            price = float(item.get('last_price') or item.get('last_traded_price') or 0.0)
        except Exception as e:
            logger.warning(f"Failed to fetch LTP for {symbol}: {e}")
        # Try historical for VWAP/EMA200 via Kite REST
        vwap = None
        ema200 = None
        if instrument_token is not None:
            hist = self._fetch_historical(instrument_token, interval='minute', lookback_minutes=600)
            if hist is not None and not hist.empty:
                try:
                    # VWAP over last 50 candles
                    tail = hist.tail(50)
                    vol_sum = tail['volume'].sum()
                    if vol_sum > 0:
                        vwap = float((tail['close'] * tail['volume']).sum() / vol_sum)
                    # EMA-200 over close
                    ema_series = hist['close'].ewm(span=200, adjust=False).mean()
                    ema200 = float(ema_series.iloc[-1])
                except Exception:
                    pass
        # Fallbacks if unavailable
        if vwap is None:
            vwap = float(price) if price else 0.0
        if ema200 is None:
            ema200 = float(price) if price else 0.0
        return {
            'symbol': symbol,
            'timestamp': datetime.now(tz),
            'price': float(price),
            'volume': 0,
            'vwap': vwap,
            'ema_200': ema200,
            'exchange': exchange,
        }
    
    def calculate_scores(self, symbol: str) -> Dict:
        """Calculate scores for all factors."""
        scores = {
            'option_oi_dynamics': 0,
            'pcr_max_pain': 0,
            'gamma_dealer_flow': 0,
            'price_action': 0,
            'total_score': 0,
            'timestamp': datetime.now(pytz.timezone(TIME_CONFIG['timezone']))
        }
        
        # Get market data
        market_data = self.fetch_market_data(symbol)
        
        # 1. Option OI Dynamics (35 points)
        # TODO: Implement actual OI change calculation
        pe_oi_increase = False
        ce_oi_decrease = False
        
        if pe_oi_increase:
            scores['option_oi_dynamics'] += SCORING_WEIGHTS['option_oi_dynamics']['pe_oi_increase']
        if ce_oi_decrease:
            scores['option_oi_dynamics'] += SCORING_WEIGHTS['option_oi_dynamics']['ce_oi_decrease']
        
        # 2. PCR & Max Pain (15 points)
        pcr_rising = False
        if pcr_rising:
            scores['pcr_max_pain'] += SCORING_WEIGHTS['pcr_max_pain']['pcr_rising']
        
        # 3. Price Action (15 points)
        if market_data['price'] > market_data['vwap']:
            scores['price_action'] += SCORING_WEIGHTS['price_action']['above_vwap']
        if market_data['price'] > market_data['ema_200']:
            scores['price_action'] += SCORING_WEIGHTS['price_action']['above_200ema']
        
        # Calculate total score
        scores['total_score'] = sum([scores[k] for k in scores if k != 'timestamp'])
        
        return scores
    
    def generate_signal(self, symbol: str) -> Dict:
        """Generate trading signal for given symbol."""
        scores = self.calculate_scores(symbol)
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now(pytz.timezone(TIME_CONFIG['timezone'])),
            'action': 'BUY' if scores['total_score'] >= ALERT_CONFIG['min_confidence_score'] else 'HOLD',
            'confidence_score': scores['total_score'],
            'scores': scores
        }
        
        # Log the signal
        self.log_signal(signal)
        
        return signal
    
    def log_signal(self, signal: Dict):
        """Log the generated signal."""
        log_entry = {
            'timestamp': signal['timestamp'].isoformat(),
            'symbol': signal['symbol'],
            'action': signal['action'],
            'confidence_score': signal['confidence_score']
        }
        
        # Log to console
        logger.info(f"Signal: {log_entry}")
        
        # Save to Excel
        df = pd.DataFrame([log_entry])
        file_path = os.path.join('data', 'trade_signals.xlsx')
        
        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_excel(file_path, index=False)

        # Telegram notification (optional)
        try:
            if TELEGRAM_CONFIG.get('enabled') and TELEGRAM_CONFIG.get('bot_token') and TELEGRAM_CONFIG.get('chat_id'):
                msg = f"Signal: {signal['symbol']} | {signal['action']} | score={signal['confidence_score']} | {signal['timestamp'].strftime('%H:%M:%S')}"
                bot = TELEGRAM_CONFIG['bot_token']
                chat_id = TELEGRAM_CONFIG['chat_id']
                url = f"https://api.telegram.org/bot{bot}/sendMessage"
                requests.post(url, params={'chat_id': chat_id, 'text': msg}, timeout=5)
        except Exception:
            pass

def main():
    """Main function to run the trading signal generator."""
    logger.info("Starting Trading Signal Generator")
    
    # Initialize signal generator
    tsg = TradingSignalGenerator()
    
    # Example: Generate signals for all symbols in watchlist
    for symbol in TRADING_CONFIG['watchlist']:
        try:
            signal = tsg.generate_signal(symbol)
            logger.info(f"Generated {signal['action']} signal for {symbol} with confidence {signal['confidence_score']}")
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")

if __name__ == "__main__":
    main()
