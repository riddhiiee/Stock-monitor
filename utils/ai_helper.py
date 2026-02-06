import os
from dotenv import load_dotenv
from utils.data_fetcher import DataFetcher

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

try:
    from groq import Groq
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Groq not installed, using rule-based fallback")


class AIHelper:
    def __init__(self, data_fetcher: DataFetcher):
        self.data_fetcher = data_fetcher
        api_key = os.getenv("OPENAI_API_KEY")   # ✅ FIXED

        if not api_key or not AI_AVAILABLE:
            print("⚠ AI features disabled — using fallback responses")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=api_key)
                print("✓ Groq AI initialized")
            except Exception as e:
                print(f"⚠ AI initialization failed: {e}")
                self.client = None

    # =========================================================
    # 🧠 GENERAL AI CHAT (CAN ANSWER ANYTHING)
    # =========================================================
    def chat_response(self, message):
        message = message.strip()

        # 🔹 Generic fallback responses if AI unavailable
        fallback_knowledge = {
            "hello": "Hi! How can I help you today?",
            "hi": "Hello! Ask me anything.",
            "help": "You can ask me about finance, investing, stocks, or even general knowledge.",
            "who are you": "I'm your AI assistant. I can help explain finance concepts and answer general questions.",
        }

        lower_msg = message.lower()
        for key in fallback_knowledge:
            if key in lower_msg:
                print("📚 Using fallback response")
                return fallback_knowledge[key]

        # 🔹 Use AI if available
        if self.client:
            try:
                print("🤖 AI GENERAL ASSISTANT ACTIVE")
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful AI assistant. "
                                "You can answer general knowledge, finance, investing, and educational questions. "
                                "Keep answers clear and beginner-friendly."
                            )
                        },
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print("⚠ AI failed:", e)

        return "I'm here to help! Ask me anything about finance, investing, or general knowledge."

    # =========================================================
    # 📈 STOCK INSIGHT GENERATOR (UNCHANGED PURPOSE)
    # =========================================================
    def generate_stock_insight(self, ticker, metrics):
        total_return = metrics['total_return']
        volatility = metrics['annualized_volatility']
        sharpe = metrics['sharpe_ratio']
        drawdown = metrics['max_drawdown']

        if total_return > 20:
            performance = "strong gains"
        elif total_return > 10:
            performance = "solid returns"
        elif total_return > 0:
            performance = "modest growth"
        elif total_return > -10:
            performance = "slight decline"
        else:
            performance = "significant losses"

        if volatility < 15:
            vol_desc = "with low volatility"
        elif volatility < 30:
            vol_desc = "with moderate volatility"
        else:
            vol_desc = "with high volatility"

        if sharpe > 2:
            sharpe_desc = "excellent risk-adjusted returns"
        elif sharpe > 1:
            sharpe_desc = "good risk-adjusted returns"
        elif sharpe > 0:
            sharpe_desc = "positive risk-adjusted returns"
        else:
            sharpe_desc = "below-average risk-adjusted returns"

        insight = f"{ticker} showed {performance} {vol_desc}, delivering {sharpe_desc}."

        if self.client:
            try:
                print("🤖 AI STOCK INSIGHT")
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a financial analyst."},
                        {"role": "user", "content": f"Explain this stock performance in one short sentence: {insight}"}
                    ],
                    max_tokens=60,
                    temperature=0.6
                )
                return response.choices[0].message.content.strip()
            except:
                pass

        return insight

    # =========================================================
    # 📊 WATCHLIST SUMMARY AI
    # =========================================================
    def generate_watchlist_summary(self, metrics_list):
        if not metrics_list:
            return "Watchlist analyzed successfully."

        avg_return = sum(m['total_return'] for m in metrics_list) / len(metrics_list)
        avg_volatility = sum(m['annualized_volatility'] for m in metrics_list) / len(metrics_list)

        summary = f"Your watchlist average return is {avg_return:.1f}% with volatility of {avg_volatility:.1f}%."

        if self.client:
            try:
                print("🤖 AI WATCHLIST SUMMARY")
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a financial advisor."},
                        {"role": "user", "content": summary}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except:
                pass

        return summary
