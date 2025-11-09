# Trading Signal Automation - User Guide (English + Hindi)

This guide explains, step by step, how to run the app on Windows and what the Streamlit UI does.
यह गाइड विंडोज़ पर ऐप चलाने के स्टेप‑बाय‑स्टेप तरीके और Streamlit UI की सुविधाओं को समझाती है।

---

## Part A: How to run the app (Windows PowerShell)
ऐप कैसे चलाएँ (विंडोज़ पावरशेल)

- **1) Open PowerShell in the project folder**
  Open `c:\Users\Ankur\Downloads\Projects\trading_signal_automation\` in PowerShell.
  प्रोजेक्ट फ़ोल्डर `c:\Users\Ankur\Downloads\Projects\trading_signal_automation\` में PowerShell खोलें।

- **2) Create a virtual environment**
  Creates an isolated Python environment called `.venv`.
  यह `.venv` नाम का अलग Python वातावरण बनाता है।
  
  ```powershell
  python -m venv .venv
  ```

- **3) Upgrade pip (recommended)**
  Ensures latest installer before installing packages.
  पैकेज इंस्टॉल करने से पहले नवीनतम इंस्टॉलर सुनिश्चित करता है।
  
  ```powershell
  .\.venv\Scripts\python.exe -m pip install --upgrade pip
  ```

- **4) Install dependencies**
  Installs all required packages from `requirements.txt`.
  `requirements.txt` से सभी ज़रूरी पैकेज इंस्टॉल करता है।
  
  ```powershell
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

- **5) Start the Streamlit UI**
  Launches the web interface in your browser (default: http://localhost:8501).
  वेब इंटरफ़ेस आपके ब्राउज़र में खुलेगा (डिफ़ॉल्ट: http://localhost:8501)।
  
  ```powershell
  .\.venv\Scripts\streamlit.exe run streamlit_app.py
  ```

- **6) Stop the app**
  Press `Ctrl + C` in the PowerShell window to stop.
  ऐप बंद करने के लिए PowerShell में `Ctrl + C` दबाएँ।

- **Note**
  The current backend `fetch_market_data()` returns placeholder zeros. To see BUY signals for testing, set the "Min Confidence Score for BUY" slider very low (e.g., 0–10).
  वर्तमान बैकएंड `fetch_market_data()` डमी ज़ीरो लौटाता है। टेस्ट के लिए BUY सिग्नल देखने हेतु "Min Confidence Score for BUY" स्लाइडर को बहुत कम (जैसे 0–10) करें।

---

## Part B: What the UI provides (features)
UI क्या प्रदान करता है (सुविधाएँ)

- **Home title and time**
  The top shows the app title and current time using your configured timezone in `config.py` → `TIME_CONFIG['timezone']`.
  ऊपर ऐप का शीर्षक और `config.py` में सेट `TIME_CONFIG['timezone']` के अनुसार वर्तमान समय दिखता है।

- **Sidebar: Select Symbols**
  Choose one or more symbols from `TRADING_CONFIG['watchlist']` to generate signals.
  `TRADING_CONFIG['watchlist']` में से एक या अधिक सिम्बल चुनें ताकि उनके लिए सिग्नल बने।

- **Sidebar: Min Confidence Score for BUY**
  Decide the threshold for marking a signal as BUY using the total score. Higher = stricter, Lower = easier BUY.
  कुल स्कोर के आधार पर BUY तय करने की सीमा सेट करें। अधिक मान = कड़ी शर्त, कम मान = आसान BUY।

- **Sidebar: Auto Refresh and Interval**
  Option to auto refresh the page every N seconds to regenerate signals.
  हर N सेकंड में पेज को ऑटो रिफ्रेश कर सिग्नल दुबारा बनाने का विकल्प।

- **Button: Generate Signals Now**
  Click to immediately calculate scores and actions for the selected symbols.
  क्लिक करने पर चुने गए सिम्बल के लिए तुरंत स्कोर और एक्शन (BUY/HOLD) निकाले जाते हैं।

- **Current Run Signals table**
  Shows the latest signals you just generated with timestamp, symbol, action and confidence score.
  अभी‑अभी बने सिग्नल टाइमस्टैम्प, सिम्बल, एक्शन और कॉन्फिडेंस स्कोर सहित दिखते हैं।

- **Download Current Signals as CSV**
  Download the current run table so you can share or analyze it elsewhere.
  करंट टेबल को CSV के रूप में डाउनलोड करें ताकि साझा या विश्लेषण किया जा सके।

- **Recent Signals (from Excel log)**
  Reads history from `data/trade_signals.xlsx` (created automatically) and shows the last entries.
  इतिहास `data/trade_signals.xlsx` (स्वतः बनती है) से पढ़कर हाल की एंट्री दिखाता है।

- **Advanced Details expander**
  Shows your configured watchlist, the current session threshold, and timezone.
  आपकी सेट की हुई वॉचलिस्ट, मौजूदा सेशन थ्रेशोल्ड और टाइमज़ोन दिखाता है।

---

## How the UI works with the backend
UI बैकएंड के साथ कैसे काम करता है

- **Score calculation**
  The UI calls `TradingSignalGenerator.calculate_scores(symbol)` for each selected symbol.
  UI हर चुने हुए सिम्बल के लिए `TradingSignalGenerator.calculate_scores(symbol)` को कॉल करता है।

- **Action decision**
  The UI decides BUY vs HOLD using the slider threshold without changing your `config.py`.
  UI स्लाइडर थ्रेशोल्ड के आधार पर BUY/HOLD तय करता है, `config.py` बदले बिना।

- **Logging**
  Signals are logged via `TradingSignalGenerator.log_signal()` into `data/trade_signals.xlsx`.
  सिग्नल `TradingSignalGenerator.log_signal()` के माध्यम से `data/trade_signals.xlsx` में सेव होते हैं।

---

## Troubleshooting
समस्या समाधान

- **The page opens but all signals are HOLD**
  Lower the Min Confidence slider because placeholder market data may produce low scores.
  मिन कॉन्फिडेंस स्लाइडर कम करें, क्योंकि प्लेसहोल्डर मार्केट डेटा कम स्कोर दे सकता है।

- **Browser did not open automatically**
  Manually open http://localhost:8501 after starting Streamlit.
  Streamlit शुरू करने के बाद http://localhost:8501 ब्राउज़र में स्वयं खोलें।

- **Package install errors**
  Ensure internet access and retry `pip install`. Share error text if it persists.
  इंटरनेट कनेक्शन जाँचें और `pip install` फिर चलाएँ। त्रुटि बनी रहे तो संदेश साझा करें।

---

## Files to know
जानने योग्य फ़ाइलें

- `streamlit_app.py` – Streamlit UI entry point.
  `streamlit_app.py` – Streamlit UI की मुख्य फ़ाइल।
- `trading_signal_generator.py` – Core logic for scoring and logging.
  `trading_signal_generator.py` – स्कोरिंग और लॉगिंग की मुख्य लॉजिक।
- `config.py` – Watchlist, thresholds, timezone, and other settings.
  `config.py` – वॉचलिस्ट, थ्रेशोल्ड, टाइमज़ोन और अन्य सेटिंग।
- `data/trade_signals.xlsx` – Excel log created automatically.
  `data/trade_signals.xlsx` – स्वतः बनती Excel लॉग फ़ाइल।
