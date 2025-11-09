<!--
 Author: Ankur Dixit
 Date: 2025-10-19
 -->
# Trading Signal Automation System

This is a simple trading signal automation system that generates buy/sell signals based on the provided scoring system using option chain data and technical indicators.

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package installer)

## Installation

1. **Clone the repository** or download the files to your local machine.

2. **Create a virtual environment (recommended):**
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install the required packages:**
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Open `config.py` and update the following settings:
   - Add your stock symbols to the `watchlist` in `TRADING_CONFIG`
   - Update API credentials if you have any (currently using placeholder data)
   - Adjust scoring weights if needed in `SCORING_WEIGHTS`
   - Set your preferred alert methods in `ALERT_CONFIG`

## Running the System

1. **Run the signal generator:**
   ```
   python trading_signal_generator.py
   ```

2. The system will:
   - Fetch market data for all symbols in the watchlist
   - Calculate scores based on the defined parameters
   - Generate buy/sell signals
   - Save the signals to an Excel file in the `data` directory
   - Display logs in the console

## Understanding the Output

- **Console Output:** Real-time logging of signals and system status
- **Excel File (`data/trade_signals.xlsx`):** Historical record of all generated signals
  - Timestamp: When the signal was generated
  - Symbol: Stock/Index symbol
  - Action: BUY or HOLD
  - Confidence Score: 0-100 score indicating signal strength

## Customization

1. **Adding More Indicators:**
   - Modify the `calculate_scores` method in `trading_signal_generator.py`
   - Add new scoring parameters in `config.py` under `SCORING_WEIGHTS`

2. **Changing Alert Thresholds:**
   - Adjust `min_confidence_score` in `ALERT_CONFIG` to change when signals are triggered
   - Modify weights in `SCORING_WEIGHTS` to emphasize different factors

## Backtesting

To backtest the strategy:

1. Create a new Python script (e.g., `backtest.py`)
2. Import the `TradingSignalGenerator` class
3. Feed historical data and evaluate signal performance
4. Analyze the results and adjust the strategy as needed




