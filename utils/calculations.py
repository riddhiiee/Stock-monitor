import pandas as pd
import numpy as np
from scipy import stats

class MetricsCalculator:
    def __init__(self, stock_data):
        """
        stock_data: Dictionary with ticker as key and dataframe as value
        """
        self.stock_data = stock_data
    
    def calculate_returns(self, df):
        """Calculate daily returns"""
        return df['Close'].pct_change().dropna()
    
    def calculate_total_return(self, df): 
        """Calculate total return percentage"""
        if df.empty or len(df) < 2:
            return 0
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        return ((end_price - start_price) / start_price) * 100
    
    def calculate_annualized_return(self, df):
        """Calculate annualized return"""
        if df.empty or len(df) < 2:
            return 0
        
        total_return = self.calculate_total_return(df)
        days = len(df)
        years = days / 252  # 252 trading days in a year
        
        if years > 0:
            annualized_return = ((1 + total_return/100) ** (1/years) - 1) * 100
            return annualized_return
        return 0
    
    def calculate_volatility(self, df):
        """Calculate annualized volatility"""
        if df.empty or len(df) < 2:
            return 0
        
        returns = self.calculate_returns(df)
        daily_volatility = returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252) * 100
        return annualized_volatility
    
    def calculate_sharpe_ratio(self, df, risk_free_rate=0.02):
        """
        Calculate Sharpe Ratio
        risk_free_rate: Annual risk-free rate (default 2%)
        """
        if df.empty or len(df) < 2:
            return 0
        
        returns = self.calculate_returns(df)
        
        # Convert annual risk-free rate to daily
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1
        
        excess_returns = returns - daily_rf
        
        if excess_returns.std() == 0:
            return 0
        
        sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        return sharpe_ratio
    
    def calculate_max_drawdown(self, df):
        """Calculate maximum drawdown percentage"""
        if df.empty or len(df) < 2:
            return 0
        
        prices = df['Close']
        
        # Calculate cumulative returns
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        return max_drawdown
    
    def calculate_all_metrics(self, ticker):


        """Calculate all metrics for a single ticker"""
        if ticker not in self.stock_data:
            return None
        
        df = self.stock_data[ticker]
        
        if df.empty or len(df) < 2:
            return None
        print(f"Calculating metrics for {ticker}")
        print("Dataframe length:", len(df))
        print(df.head())
        metrics = {
            'ticker': ticker,
            'total_return': round(self.calculate_total_return(df), 2),
            'annualized_return': round(self.calculate_annualized_return(df), 2),
            'annualized_volatility': round(self.calculate_volatility(df), 2),
            'sharpe_ratio': round(self.calculate_sharpe_ratio(df), 2),
            'max_drawdown': round(self.calculate_max_drawdown(df), 2),
            'start_price': round(df['Close'].iloc[0], 2),
            'end_price': round(df['Close'].iloc[-1], 2),
            'days': len(df)
        }
        
        return metrics
    
    def calculate_correlation_matrix(self):
        """Calculate correlation matrix between all stocks"""
        if not self.stock_data:
            return None
        
        # Create a dataframe with all closing prices
        price_data = pd.DataFrame()
        
        for ticker, df in self.stock_data.items():
            if not df.empty:
                price_data[ticker] = df['Close']
        
        if price_data.empty:
            return None
        
        # Calculate returns
        returns = price_data.pct_change().dropna()
        
        # Calculate correlation matrix
        correlation_matrix = returns.corr()
        
        return correlation_matrix.round(3).to_dict()
    
    def get_normalized_prices(self):
        """
        Get normalized prices (starting at 100) for comparison
        Returns: Dictionary with dates and normalized prices for each ticker
        """
        normalized_data = {}
        
        for ticker, df in self.stock_data.items():
            if not df.empty and len(df) > 0:
                normalized = (df['Close'] / df['Close'].iloc[0]) * 100
                normalized_data[ticker] = {
                    'dates': df.index.strftime('%Y-%m-%d').tolist(),
                    'values': normalized.round(2).tolist()
                }
        
        return normalized_data
    
    def get_price_data(self):
        """Get actual price data for charts"""
        price_data = {}
        
        for ticker, df in self.stock_data.items():
            if not df.empty:
                price_data[ticker] = {
                    'dates': df.index.strftime('%Y-%m-%d').tolist(),
                    'prices': df['Close'].round(2).tolist()
                }
        
        return price_data
    
    def get_watchlist_summary(self, metrics_list):
        """Calculate summary statistics for the entire watchlist"""
        if not metrics_list:
            return None
        
        returns = [m['total_return'] for m in metrics_list]
        volatilities = [m['annualized_volatility'] for m in metrics_list]
        
        summary = {
            'average_return': round(np.mean(returns), 2),
            'best_performer': max(metrics_list, key=lambda x: x['total_return']),
            'worst_performer': min(metrics_list, key=lambda x: x['total_return']),
            'most_volatile': max(metrics_list, key=lambda x: x['annualized_volatility']),
            'least_volatile': min(metrics_list, key=lambda x: x['annualized_volatility'])
        }
        
        return summary
