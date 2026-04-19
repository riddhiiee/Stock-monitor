import json
import os
import math
from datetime import datetime, timedelta
import yfinance as yf

class PortfolioManager:
    def __init__(self):
        self.portfolio_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'portfolio.json')
        self.history_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'portfolio_history.json')
        
    def create_portfolio(self, initial_cash, allocations):
        """
        Create a new portfolio
        allocations: [{"ticker": "AAPL", "amount": 3000}, ...]
        """
        portfolio = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "initial_cash": initial_cash,
            "holdings": [],
            "cash_remaining": initial_cash
        }
        
        total_allocated = 0
        
        # Buy stocks at current market price
        for allocation in allocations:
            ticker = allocation['ticker']
            amount = allocation['amount']
            
            try:
                # Get current price
                stock = yf.download(ticker, period="1d", progress=False)
                if stock.empty or 'Close' not in stock:
                    continue
                    
                close_data = stock['Close']

                # If it's a DataFrame (multi-column)
                if hasattr(close_data, "columns"):
                    current_price = close_data.iloc[-1].values[0]
                else:
                    current_price = close_data.iloc[-1]

                current_price = float(current_price)
                if current_price is None or math.isnan(current_price) or current_price == 0:
                    print(f"Invalid price for {ticker}")
                    continue

                current_price = float(current_price)
                shares = float(amount / current_price)
                
                portfolio['holdings'].append({
                    "ticker": ticker,
                    "shares": round(shares, 4),
                    "buy_price": round(current_price, 2),
                    "buy_date": datetime.now().strftime("%Y-%m-%d"),
                    "amount_invested": amount
                })
                
                total_allocated += amount
                
            except Exception as e:
                print(f"Error buying {ticker}: {e}")
        
        portfolio['cash_remaining'] = initial_cash - total_allocated
        
        # Save portfolio
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
        
        # Initialize history
        self._record_daily_snapshot(portfolio)
        
        return portfolio
    
    def get_portfolio(self):
        """Get current portfolio"""
        if not os.path.exists(self.portfolio_file):
            return None
        
        with open(self.portfolio_file, 'r') as f:
            return json.load(f)
    
    def calculate_current_value(self, portfolio=None):
        """Calculate current portfolio value"""
        if portfolio is None:
            portfolio = self.get_portfolio()
        
        if not portfolio:
            return 0
        
        total_value = portfolio['cash_remaining']
        holdings_value = {}
        
        for holding in portfolio['holdings']:
            try:
                stock = yf.download(holding['ticker'], period="1d", progress=False)
                if not stock.empty:
                    current_price = stock['Close'].iloc[-1]

                    # force scalar
                    if hasattr(current_price, "item"):
                        current_price = current_price.item()

                    current_price = float(current_price)

                    import math
                    if math.isnan(current_price) or current_price == 0:
                        continue

                    holding_value = float(holding['shares']) * current_price
                    total_value += holding_value
                    holdings_value[holding['ticker']] = {
                        'current_price': round(current_price, 2),
                        'value': round(holding_value, 2),
                        'gain_loss': round(holding_value - holding['amount_invested'], 2),
                        'gain_loss_pct': round(((holding_value - holding['amount_invested']) / holding['amount_invested']) * 100, 2)
                    }
            except Exception as e:
                print(f"Error fetching {holding['ticker']}: {e}")
        
        return {
            'total_value': round(total_value, 2),
            'holdings_value': holdings_value,
            'cash': portfolio['cash_remaining']
        }
    
    def update_daily_snapshot(self):
        """Record daily portfolio value"""
        portfolio = self.get_portfolio()
        if not portfolio:
            return None
        
        return self._record_daily_snapshot(portfolio)
    
    def _record_daily_snapshot(self, portfolio):
        """Internal method to record snapshot"""
        current_value_data = self.calculate_current_value(portfolio)
        
        snapshot = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_value": current_value_data['total_value'],
            "cash": current_value_data['cash'],
            "holdings_value": current_value_data['holdings_value']
        }
        
        # Load history
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {"snapshots": []}
        
        # Check if today's snapshot already exists
        today = snapshot['date']
        existing_index = None
        for i, snap in enumerate(history['snapshots']):
            if snap['date'] == today:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing snapshot
            history['snapshots'][existing_index] = snapshot
        else:
            # Add new snapshot
            history['snapshots'].append(snapshot)
        
        # Calculate daily returns
        if len(history['snapshots']) > 1:
            for i in range(1, len(history['snapshots'])):
                prev_value = history['snapshots'][i-1]['total_value']
                curr_value = history['snapshots'][i]['total_value']
                daily_return = ((curr_value - prev_value) / prev_value) * 100
                history['snapshots'][i]['daily_return'] = round(daily_return, 2)
        
        # Save history
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return snapshot
    
    def get_performance_history(self):
        """Get portfolio performance history"""
        if not os.path.exists(self.history_file):
            return {"snapshots": []}
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        portfolio = self.get_portfolio()
        if not portfolio:
            return history
        
        # Calculate metrics
        snapshots = history['snapshots']
        if len(snapshots) > 0:
            initial_value = portfolio['initial_cash']
            current_value = snapshots[-1]['total_value']
            
            total_return = ((current_value - initial_value) / initial_value) * 100
            
            # Calculate volatility
            if len(snapshots) > 1:
                daily_returns = [s.get('daily_return', 0) for s in snapshots[1:]]
                import numpy as np
                volatility = np.std(daily_returns) if daily_returns else 0
            else:
                volatility = 0
            
            history['metrics'] = {
                'initial_value': initial_value,
                'current_value': current_value,
                'total_return': round(total_return, 2),
                'total_gain_loss': round(current_value - initial_value, 2),
                'volatility': round(volatility, 2),
                'days_tracked': len(snapshots)
            }
        
        return history
    
    def delete_portfolio(self):
        """Delete current portfolio and history"""
        if os.path.exists(self.portfolio_file):
            os.remove(self.portfolio_file)
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        return True
    
    def get_portfolio_summary(self):
        """Get comprehensive portfolio summary"""
        portfolio = self.get_portfolio()
        if not portfolio:
            return None
        
        current_value_data = self.calculate_current_value(portfolio)
        history = self.get_performance_history()
        
        # Calculate individual stock performance
        stock_performance = []
        for holding in portfolio['holdings']:
            ticker = holding['ticker']
            if ticker in current_value_data['holdings_value']:
                perf = current_value_data['holdings_value'][ticker]
                stock_performance.append({
                    'ticker': ticker,
                    'shares': holding['shares'],
                    'buy_price': holding['buy_price'],
                    'current_price': perf['current_price'],
                    'invested': holding['amount_invested'],
                    'current_value': perf['value'],
                    'gain_loss': perf['gain_loss'],
                    'gain_loss_pct': perf['gain_loss_pct']
                })
        
        return {
            'portfolio': portfolio,
            'current_value': current_value_data,
            'history': history,
            'stock_performance': stock_performance
        }
