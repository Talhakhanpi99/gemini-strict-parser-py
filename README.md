# 📰 AI News Aggregator Core: Data Fetcher & Scorer (`fetch.py`)

## 💡 This is a Sample!
**This script is a powerful, standalone demonstration of the advanced article collection, filtering, and scoring logic that forms the **foundation** of our complete, production-ready **AI News Aggregator Web App Template**.

### ✨ Live Demo
See the final, deployed application in action before you buy the source code:

➡️ **[View the Live Demo of CryptoPulse Here](https://cryptopulse.pythonanywhere.com/)**

---

## 🚀 Get the Full Source Code & Launch Your App Today

**Ready to move beyond the sample script and launch your fully-automated, SEO-optimized news platform?**

The complete template includes **100% of the source code** for the FastAPI backend and Vue.js frontend, pre-integrated with Gemini, authentication, database, and scheduled deployment settings.

### **[🛒 Click Here to Buy the Complete AI Web App Template on Itch.io!](https://talha-ghayas-khan.itch.io/ai-news-aggregator-full-stack-template)])**

---

## What is `fetch.py`? (The Brains of the Operation)

The `fetch.py` script is a high-quality Python tool that performs a crucial task: **It filters the noise out of the cryptocurrency news landscape to find high-value, SEO-worthy articles.**

It works by:

1.  **Multi-Source Aggregation:** Pulling articles from multiple RSS feeds and the CryptoPanic API.
2.  **Deep Web Scraping:** Using a combination of BeautifulSoup and `newspaper3k` to reliably extract the clean, full article text from diverse news sites.
3.  **Intelligent Scoring:** Applying a custom scoring algorithm based on:
    * **Source Authority** (e.g., Coindesk gets a higher score than a generic blog).
    * **High-Value Keywords** (e.g., "SEC," "ETF," "Binance" give a strong positive boost).
    * **Low-Value Keywords** (e.g., "Prediction," "Top 10," "Today's Update" give a strong penalty).
    * **Recency** and **Content Length**.
4.  **Caching:** Using a local `cache.json` file to prevent re-fetching or re-processing the same articles, saving time and API calls.

This script ensures that only the **top 10 most relevant, high-signal articles** are selected for the next stage of the pipeline (which, in the full application, is the **AI Rewriting Engine**).

---

## 🛠️ How to Run the Sample Script

### **1. Setup**

You will need **Python 3.8+** installed.

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # (requires a requirements.txt file with: feedparser requests beautifulsoup4 newspaper3k)
    ```

2.  **Set Your API Key:**
    The script uses a placeholder API key for CryptoPanic. For the script to work reliably, you should replace the placeholder key:
    ```python
    # In fetch.py, update this line with your actual key if the placeholder fails
    CRYPTOPANIC_API_KEY = "  " 
    ```

### **2. Execution**

Run the script from your terminal:

```bash
python fetch.py

3. Output
The script will log its progress and, upon completion, will generate a file named news.json containing an array of the top 10 articles, fully scraped and scored, ready for the next step of AI rewriting and summarization.

🔑 The Missing Piece (Why You Need the Full Template)
The fetch.py script stops at collecting and filtering the raw data. This raw data is NOT suitable for direct publishing due to potential copyright issues and SEO penalties for duplicate content. While the sample provides the crucial Data Fetching & Scoring logic, it is only the first step.

The Full Template completes this workflow and provides a production-ready application.

Beyond the data fetching provided here, the purchased template includes the complete AI Rewrite (Gemini) engine, which uses the specialized rewrite_prompt.txt to generate 100% original, SEO-optimized content. It also features Data Parsing using the parse_gemini_strict_output function to ensure reliable extraction of structured data from the AI's response, and it integrates Sentiment Analysis (VADER) to auto-generate valuable sentiment tags for every article.

Crucially, the full template gives you the entire application shell, including a Full FastAPI Backend for a robust, scalable API with a built-in scheduler, a professional Vue.js Frontend, and complete User Authentication allowing users to log in, register, and save articles.

Stop building from scratch and start customizing today.

[🛒 Click Here to Buy the Complete AI Web App Template on Itch.io!](https://talha-ghayas-khan.itch.io/ai-news-aggregator-full-stack-template])
