# 📊 StockScope – AI-Driven Investment Learning & Stock Analysis Platform

**StockScope** is an AI-powered financial learning and stock analysis web app designed to help beginners understand the stock market with clarity and confidence. It combines real stock performance analytics with an AI finance assistant that explains concepts in simple language, reducing confusion and empowering smarter investment learning.

---

## 🚀 Features

### 🤖 AI-Driven Finance Assistant  
Integrated with **LLaMA via Groq API**, the chatbot answers finance questions, explains investment concepts, and guides beginners in understanding market terms.

### 📈 Real Stock Performance Analysis  
Fetches historical stock data from **Yahoo Finance** and calculates key performance metrics like:
- Returns  
- Volatility  
- Sharpe Ratio  
- Maximum Drawdown  

### 🧠 Beginner-Friendly Explanations  
Complex financial terms are translated into simple, easy-to-understand explanations using **AI + rule-based fallback**.

### 📊 Interactive Data Visualizations  
Dynamic charts help users visually understand:
- Stock growth  
- Risk levels
- Correlation matrix
- Portfolio diversification  

### ⭐ Watchlist-Based Learning  
Users can add **up to 10 stocks** and compare them across multiple time periods to learn performance differences.

---

## 🛠 Tech Stack

| Category | Technologies Used |
|----------|------------------|
| **Frontend** | HTML, CSS, JavaScript, Bootstrap |
| **Backend** | Python, Flask |
| **Stock Data API** | Yahoo Finance (`yfinance`) |
| **Charts & Visualizations** | Plotly.js |
| **AI Integration** | LLaMA via Groq API |
| **Environment Management** | python-dotenv |

---

## 📌 Purpose

StockScope focuses on **investment learning, not financial advice**. It helps beginners build confidence by understanding how stocks perform, how risk works, and how to interpret financial metrics.

---

- Portfolio allocation simulator  
- Risk profiling quiz for beginners  
- News sentiment analysis integration  
- AI-based stock comparison summaries  

---

## ⚙ Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/riddhiiee/Stock-monitor.git
cd stock-monitor
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Add API Key

Create a `.env` file in the project root and add:

```env
OPENAI_API_KEY=your_groq_api_key_here
```

### 4️⃣ Run the App
```bash
python app.py
```

### 5️⃣ Open in Browser
```
http://localhost:5000
```
---
---

## 🔑 How to Get a Groq API Key

1️⃣ Go to the **Groq website** and **sign up / log in** to your account.  

2️⃣ Navigate to the **Developers** section from the dashboard.  

3️⃣ Find the **API Keys** or **Free API Key** section.  

4️⃣ Click **Create API Key**.  

5️⃣ Copy the generated key and paste it into your `.env` file like this:

```env
OPENAI_API_KEY=your_groq_api_key_here
```

## 🎯 Impact & Benefits

- ✅ Makes stock market learning easier for beginners  
- ✅ Connects financial data with AI explanations  
- ✅ Helps users understand risk before investing  
- ✅ Encourages data-driven decision-making  
- ✅ Acts as a bridge between finance education and technology  

---

## 🔮 Future Scope

- 🌍 Multi-language AI financial assistant  
- 🎙 Voice-enabled investment guidance  
- 📊 Portfolio tracking & alerts  
- 📚 AI-powered personalized learning paths  
- 📱 Mobile app version for wider accessibility  

---

