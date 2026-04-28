# 📊 Stock Monitor & Portfolio Analysis Platform

A comprehensive financial analytics platform that enables users to monitor stocks, analyze portfolios, and gain AI-driven insights. Designed for both beginners and intermediate investors, this tool combines quantitative finance metrics with intelligent assistance.

---

## 🚀 Features

### 📌 Watchlist & Stock Analysis

* Add multiple stocks to a personalized watchlist
* Analyze performance across custom time intervals
* Key metrics:

  * Total Return (%)
  * Annual Return (%)
  * Volatility (%)
  * Sharpe Ratio
  * Maximum Drawdown (%)
  * Start Price / End Price
  * Number of Days

---

### 📈 Visual Analytics

* Stock price trend visualization (line charts)
* Total return comparison across assets
* Risk vs Return analysis
* Asset correlation matrix

---

### 🤖 AI-Powered Insights

* AI-generated insights for:

  * Individual stocks
  * Entire watchlist
* Integrated AI chatbot for beginner-friendly financial queries
* Powered by LLaMA model via Groq API

---

### 💼 Portfolio Management

* Create and manage a portfolio by allocating capital to assets
* Real-time tracking using market data
* Displays:

  * Shares
  * Buy Price
  * Current Price
  * Invested Value
  * Current Value
  * Gain / Loss
  * Gain / Loss (%)

---

### 📊 Market Regime Detection

Analyzes overall market conditions using SPY benchmark:

* Indicators used:

  * 50-Day Moving Average
  * 200-Day Moving Average
  * Volatility
  * RSI
  * Period Return

* Provides:

  * Bull / Bear classification
  * Market regime score
  * Historical regime visualization
  * Market signals:

    * Golden Cross
    * Volatility alerts
    * RSI signals
    * Price vs moving averages

---

### ⚖️ Portfolio Optimization

* Optimization based on Sharpe Ratio
* Comparison of:

  * Equal weight portfolio
  * Optimal weight portfolio
* Efficient Frontier visualization
* Risk-based portfolios:

  * Conservative
  * Moderate
  * Aggressive

---

## 🛠️ Tech Stack

* Python
* Flask (Backend)
* HTML / CSS / JS (Frontend)
* yFinance (Market Data)
* NumPy / Pandas (Data Processing)
* Matplotlib / Plotly (Visualization)
* Groq API (LLaMA for AI insights)

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/stock-monitor.git
cd stock-monitor
```

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Setup Groq API Key (IMPORTANT)

* Go to Groq Console: https://console.groq.com
* Generate your API key

Set it as an environment variable:

**Windows:**

```bash
set GROQ_API_KEY=your_api_key_here
```

**Mac/Linux:**

```bash
export GROQ_API_KEY=your_api_key_here
```

---

### 5. Run the application

```bash
python app.py
```

---

### 6. Open in browser

```
http://127.0.0.1:5000
```
---

## 💡 Note

This platform is for educational and analytical purposes only and does not constitute financial advice.
