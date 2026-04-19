import io
from flask import Flask, render_template, request, jsonify, send_file
import openai
from utils.data_fetcher import DataFetcher
from utils.portfolio_manager import PortfolioManager
from utils.calculations import MetricsCalculator
from utils.ai_helper import AIHelper
import json
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from openai import OpenAI
app = Flask(__name__)

# Initialize utilities
data_fetcher = DataFetcher()
portfolio_manager = PortfolioManager()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) 
ai_helper = AIHelper(data_fetcher)
 
@app.route('/') # loads the website
def index():
    """Render main page"""
    sectors = data_fetcher.get_sectors()
    return render_template('index.html', sectors=sectors)

@app.route('/api/sectors', methods=['GET']) #search stocks
def get_sectors():
    """Get all available sectors"""
    sectors = data_fetcher.get_sectors()
    return jsonify({'sectors': sectors})

@app.route('/api/tickers/<sector>', methods=['GET']) #show stocks by sector
def get_tickers(sector):
    """Get all tickers for a specific sector"""
    tickers = data_fetcher.get_tickers_by_sector(sector)
    return jsonify({'tickers': tickers})

@app.route('/api/search', methods=['POST'])
def search_ticker():
    """Search for ticker using natural language"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # First try exact match in our database
    results = data_fetcher.search_ticker(query)
    
    # If no results and AI is available, use AI search
    if not results and ai_helper.client:
        ai_ticker = ai_helper.smart_search(query)
        if ai_ticker:
            try:
                test = yf.download(ai_ticker,period='5d',progress=False)
                if not test.empty:
                    results = [{
                        'ticker': ai_ticker,
                        'name': ai_ticker,
                        'sector': 'AI Suggested'
                    }]
            except:
                pass
    
    return jsonify({'results': results})

@app.route('/api/company/<ticker>', methods=['GET'])
def get_company_name(ticker):
    """Get company name for a ticker"""
    name = data_fetcher.get_company_name(ticker)
    return jsonify({'ticker': ticker, 'name': name})

@app.route('/api/portfolio/create', methods=['POST'])
def create_portfolio():
    """Create a new portfolio"""
    data = request.get_json()
    
    initial_cash = data.get('initial_cash', 10000)
    allocations = data.get('allocations', [])
    
    if not allocations:
        return jsonify({'error': 'No allocations provided'}), 400
    
    try:
        portfolio = portfolio_manager.create_portfolio(initial_cash, allocations)
        return jsonify({'portfolio': portfolio, 'message': 'Portfolio created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio"""
    portfolio = portfolio_manager.get_portfolio()
    
    if not portfolio:
        return jsonify({'portfolio': None})
    
    return jsonify({'portfolio': portfolio})

@app.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """Get comprehensive portfolio summary"""
    summary = portfolio_manager.get_portfolio_summary()
    
    if not summary:
        return jsonify({'summary': None})
    
    return jsonify(summary)

@app.route('/api/portfolio/update', methods=['POST'])
def update_portfolio_snapshot():
    """Update daily portfolio snapshot"""
    try:
        snapshot = portfolio_manager.update_daily_snapshot()
        return jsonify({'snapshot': snapshot, 'message': 'Portfolio updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/portfolio/history', methods=['GET'])
def get_portfolio_history():
    """Get portfolio performance history"""
    history = portfolio_manager.get_performance_history()
    return jsonify(history)

@app.route('/api/portfolio/delete', methods=['DELETE'])
def delete_portfolio():
    """Delete current portfolio"""
    try:
        portfolio_manager.delete_portfolio()
        return jsonify({'message': 'Portfolio deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_watchlist():
    data = request.get_json()

    tickers = data.get('tickers', [])
    period = data.get('period', '6M')
    custom_start = data.get('custom_start')
    custom_end = data.get('custom_end')

    print("=== ANALYZE REQUEST ===")
    print("Tickers:", tickers)
    print("Period:", period)
    print("Custom start/end:", custom_start, custom_end)

    
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    
    # Get date range
    if period == 'custom' and custom_start and custom_end:
        start_date = custom_start
        end_date = custom_end
    else:
        start_date, end_date = data_fetcher.get_date_range(period)
        print("Date Range:", start_date, "→", end_date)
    
    # Fetch stock data
    stock_data = data_fetcher.fetch_stock_data(tickers, start_date, end_date)
    
    if not stock_data:
        return jsonify({'error': 'No data could be fetched for the provided tickers'}), 400
    
    # Calculate metrics
    calculator = MetricsCalculator(stock_data)
    
    metrics_list = []
    for ticker in tickers:
        metrics = calculator.calculate_all_metrics(ticker)
        if metrics:
            # Add company name
            metrics['name'] = data_fetcher.get_company_name(ticker)
            
            # Generate AI insight if available
            if ai_helper.client:
                metrics['ai_insight'] = ai_helper.generate_stock_insight(ticker, metrics)
            else:
                metrics['ai_insight'] = f"{ticker}: Performance data available"
            
            metrics_list.append(metrics)
    
    # Get correlation matrix
    correlation_matrix = calculator.calculate_correlation_matrix()
    
    # Get normalized prices for comparison chart
    normalized_prices = calculator.get_normalized_prices()
    
    # Get actual prices for individual charts
    price_data = calculator.get_price_data()
    
    # Get watchlist summary
    watchlist_summary = calculator.get_watchlist_summary(metrics_list)
    
    # Generate AI summary for watchlist
    if ai_helper.client and metrics_list:
        ai_summary = ai_helper.generate_watchlist_summary(metrics_list)
    else:
        ai_summary = "Watchlist analysis complete"
    
    return jsonify({
        'metrics': metrics_list,
        'correlation_matrix': correlation_matrix,
        'normalized_prices': normalized_prices,
        'price_data': price_data,
        'watchlist_summary': watchlist_summary,
        'ai_summary': ai_summary,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    })

@app.route('/api/explain', methods=['POST'])
def explain_concept():
    """Get AI explanation for a financial concept"""
    data = request.get_json()
    concept = data.get('concept', '')
    context = data.get('context', '')
    
    if not concept:
        return jsonify({'error': 'No concept provided'}), 400
    
    explanation = ai_helper.explain_concept(concept, context)
    return jsonify({'explanation': explanation})

@app.route('/api/search_ticker', methods=['POST'])
def search_ticker_api():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"results": []})

    results = data_fetcher.search_ticker(query)

    return jsonify({"results": results})


@app.route('/api/export', methods=['POST'])
def export_data():
    """Export watchlist data as CSV"""
    data = request.get_json()
    metrics = data.get('metrics', [])
    
    if not metrics:
        return jsonify({'error': 'No data to export'}), 400
    
    df = pd.DataFrame(metrics)
    
    # Write data
    df.rename(columns={
        'ticker': 'Ticker',
        'name': 'Company Name',
        'total_return': 'Total Return (%)',
        'annualized_return': 'Annualized Return (%)',
        'annualized_volatility': 'Annualized Volatility (%)',
        'sharpe_ratio': 'Sharpe Ratio',
        'max_drawdown': 'Max Drawdown (%)',
        'start_price': 'Start Price',
        'end_price': 'End Price',
        'days': 'Days'
    }, inplace=True)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'watchlist_analysis_{datetime.now().strftime("%Y%m%d")}.csv'
    )
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'reply': 'Please ask a finance question.'})

    reply = ai_helper.chat_response(message)

    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)