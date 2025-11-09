"""
Configuration settings for the Trading Signal Automation System.

This file contains all the configuration parameters and constants used throughout the application.

Author: Ankur Dixit
Date: 2025-10-19
"""

import os
from dotenv import load_dotenv
load_dotenv()

# API Configuration
API_CONFIG = {
    'base_url': 'https://kite.zerodha.com',  # Zerodha base URL from EMA script
    'timeout': 10,  # API request timeout in seconds
    'retry_attempts': 3,  # Number of retry attempts for API calls
}

# Broker (Zerodha) configuration via environment variables
BROKER_CONFIG = {
    'base_url': os.getenv('ZERODHA_BASE_URL', 'https://kite.zerodha.com'),
    'username': os.getenv('ZERODHA_USERNAME', ''),
    'password': os.getenv('ZERODHA_PASSWORD', ''),
    'totp_secret': os.getenv('ZERODHA_TOTP', ''),
}

# Optional: Kite Connect API (preferred for historical data)
KITE_CONNECT = {
    'api_key': os.getenv('KITE_API_KEY', ''),
    'access_token': os.getenv('KITE_ACCESS_TOKEN', ''),
}

# Telegram notification configuration
TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    'enabled': os.getenv('TELEGRAM_NOTIFY', 'false').lower() in ('1', 'true', 'yes'),
}
TRADING_CONFIG = {
    'watchlist': [
        'NIFTY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'INFY',
        'HINDUNILVR', 'TATASTEEL', 'BHARTIARTL', 'BAJFINANCE', 'KOTAKBANK'
        # Add more stocks as needed (up to 50+)
    ],
    'update_interval': 60,  # Data update interval in seconds
    'max_trades_per_day': 5,  # Maximum number of trades per day
}

# Option Chain Parameters
OPTION_CHAIN_CONFIG = {
    'strikes_to_consider': 5,  # Number of strikes to consider (ATM ±2 = 5 strikes)
    'oi_change_threshold': 0.05,  # 5% OI change threshold
    'pcr_threshold': 1.2,  # PCR threshold for signal
    'iv_stable_threshold': 0.1,  # 10% IV change threshold
}

# Scoring Weights (as per requirements)
SCORING_WEIGHTS = {
    'option_oi_dynamics': {
        'pe_oi_increase': 18,
        'ce_oi_decrease': 12,
        'futures_long_buildup': 5,
    },
    'pcr_max_pain': {
        'pcr_rising': 8,
        'max_pain_upward': 7,
    },
    'gamma_dealer_flow': {
        'positive_gex': 10,
        'negative_gex_iv_stable': 10,
    },
    'price_action': {
        'above_vwap': 10,
        'above_200ema': 5,
    },
    'volatility_greeks': {
        'ce_iv_stable': 4,
        'call_delta_strong': 3,
    },
    'volume_confirmation': {
        'volume_spike': 8,
    },
}

# File Paths
FILE_PATHS = {
    'trade_log': 'data/trade_log.xlsx',
    'backtest_data': 'data/backtest/',
    'logs': 'logs/automation.log',
}

# External data sources
DATA_SOURCES = {
    'instruments_csv': os.getenv('INSTRUMENTS_CSV_URL', 'https://api.kite.trade/instruments'),
}

# Alert Configuration
ALERT_CONFIG = {
    'min_confidence_score': 60,  # Minimum score to trigger a trade alert
    'alert_methods': ['console', 'email'],  # Options: 'console', 'email', 'sms', 'webhook'
    'email_recipient': 'your.email@example.com',
}

# Backtesting Configuration
BACKTEST_CONFIG = {
    'initial_capital': 100000,  # Initial capital in INR
    'risk_per_trade': 0.02,  # Risk 2% of capital per trade
    'commission_rate': 0.0003,  # 0.03% commission per trade
}

# Time Configuration
TIME_CONFIG = {
    'market_open': '09:15',
    'market_close': '15:30',
    'timezone': 'Asia/Kolkata',
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_size_mb': 10,  # Maximum log file size in MB
    'backup_count': 5,  # Number of backup log files to keep
}

# Add any additional configuration parameters below
# ...
