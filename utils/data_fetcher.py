import yfinance as yf
yf.set_tz_cache_location("timezone_cache")
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import requests
class DataFetcher:
    def __init__(self):
        # Load sector data
        sectors_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sectors.json')
        with open(sectors_path, 'r') as f:
            self.sectors_data = json.load(f)
    
    def get_sectors(self):
        """Return list of available sectors"""
        return list(self.sectors_data.keys())
    
    def get_tickers_by_sector(self, sector):
        """Get all tickers for a given sector"""
        if sector in self.sectors_data:
            return self.sectors_data[sector]
        return []
        
    def get_company_name(self, ticker):
        """Get company name for a ticker"""
        for sector, companies in self.sectors_data.items():
            for company in companies:
                if company['ticker'] == ticker:
                    return company['name']
        return ticker
    
    def fetch_stock_data(self, tickers, start_date, end_date):
        """
        Fetch historical stock data for multiple tickers
        Returns: Dictionary with ticker as key and dataframe as value
        """
        print("=== FETCHING STOCK DATA ===")
        print("Tickers:", tickers)
        print("Start:", start_date, "End:", end_date)

        stock_data = {}

        try:
            data = yf.download(
                tickers=" ".join(tickers),
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            print("Downloaded data type:", type(data))

            if data.empty:
                print("⚠ Yahoo returned empty dataset")
                return stock_data

            # ===== Single ticker =====
            if len(tickers) == 1:
                ticker = tickers[0]

                if isinstance(data.columns, pd.MultiIndex):
                    df = data.xs(ticker, axis=1, level=1)
                else:
                    df = data.copy()

                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.dropna(inplace=True)

                stock_data[ticker] = df
                print(f"{ticker} dataframe shape:", df.shape)

            # ===== Multiple tickers =====
            else:
                if isinstance(data.columns, pd.MultiIndex):
                    for ticker in tickers:
                        try:
                            df = data.xs(ticker, axis=1, level=1).copy()

                            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                            df.dropna(inplace=True)

                            print(f"{ticker} dataframe shape:", df.shape)

                            if not df.empty:
                                stock_data[ticker] = df

                        except KeyError:
                            print(f"No data found for {ticker}")
                else:
                    print("⚠ Unexpected column format for multiple tickers")

        except Exception as e:
            print(f"Yahoo Finance download error: {e}")

        return stock_data

    def search_ticker(self, query):
        query = query.strip()
        if not query:
            return []

        results = []

        # 🔹 1. Search local sectors.json first
        query_upper = query.upper()
        for sector, companies in self.sectors_data.items():
            for company in companies:
                if query_upper in company['ticker'] or query_upper in company['name'].upper():
                    results.append({
                        'ticker': company['ticker'],
                        'name': company['name'],
                        'sector': sector
                    })

        # 🔹 2. Yahoo Finance Search API (if not found locally)
        if not results:
            try:
                url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    quotes = data.get('quotes', [])

                    for quote in quotes:
                        symbol = quote.get('symbol')
                        name = quote.get('longname') or quote.get('shortname') or symbol
                        quote_type = quote.get('quoteType')

                        # Only include stocks and ETFs
                        if symbol and quote_type in ['EQUITY', 'ETF']:
                            results.append({
                                'ticker': symbol.upper(),
                                'name': name,
                                'sector': quote.get('sector', 'Unknown')
                            })
            except Exception as e:
                print("Yahoo search API failed:", e)

        # 🔹 3. Final fallback: direct ticker check
        if not results:
            try:
                test = yf.download(query.upper(), period="5d", progress=False, threads=False)
                if not test.empty:
                    results.append({
                        'ticker': query.upper(),
                        'name': query.upper(),
                        'sector': 'Unknown'
                    })
            except:
                pass

        return results[:10]
    
    def get_date_range(self, period):
        """
        Convert period string to date range
        period: '1M', '3M', '6M', '1Y', 'YTD', or 'custom'
        """
        end_date = datetime.now()
        
        if period == '1M':
            start_date = end_date - timedelta(days=30)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'YTD':
            start_date = datetime(end_date.year, 1, 1)
        else:
            # Default to 6 months
            start_date = end_date - timedelta(days=180)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
