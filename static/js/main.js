// Global variables
let watchlist = [];
const MAX_WATCHLIST = 10;
let currentAnalysisData = null;

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log("App initialized");
});

// ============================================
// SECTOR AND TICKER SELECTION
// ============================================

// Sector selection handler
document.getElementById('sectorSelect').addEventListener('change', function() {
    const sector = this.value;
    const tickerListContainer = document.getElementById('tickerListContainer');
    const tickerList = document.getElementById('tickerList');
    
    console.log("Sector selected:", sector);
    
    if (!sector) {
        tickerListContainer.style.display = 'none';
        return;
    }
    
    // Show loading
    tickerList.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div> Loading...</div>';
    tickerListContainer.style.display = 'block';
    
    // Fetch tickers for selected sector
    fetch(`/api/tickers/${encodeURIComponent(sector)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Tickers received:", data);
            tickerList.innerHTML = '';
            
            if (!data.tickers || data.tickers.length === 0) {
                tickerList.innerHTML = '<p class="text-muted">No tickers found for this sector</p>';
                return;
            }
            
            data.tickers.forEach(stock => {
                const div = document.createElement('div');
                div.className = 'ticker-item';
                div.title = stock.name; // Show full name on hover
                div.innerHTML = `
                    <div>
                        <span class="ticker-symbol">${stock.ticker}</span>
                    </div>
                    <button class="btn btn-sm btn-success" onclick="addToWatchlist('${stock.ticker}', '${stock.name.replace(/'/g, "\\'")}')">
                        <i class="fas fa-plus"></i>
                    </button>
                `;
                tickerList.appendChild(div);
            });
            
            console.log("Tickers displayed successfully");
        })
        .catch(error => {
            console.error('Error fetching tickers:', error);
            tickerList.innerHTML = '<div class="alert alert-danger">Error loading tickers. Please try again.</div>';
        });
});

// ============================================
// CHATBOT FUNCTIONALITY
// ============================================

const chatToggleBtn = document.getElementById('chatToggleBtn');
const chatWindow = document.getElementById('chatWindow');
const chatCloseBtn = document.getElementById('chatCloseBtn');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatBody = document.getElementById('chatBody');

// Toggle chat window
chatToggleBtn.addEventListener('click', function() {
    if (chatWindow.style.display === 'none' || chatWindow.style.display === '') {
        chatWindow.style.display = 'flex';
        chatInput.focus();
    } else {
        chatWindow.style.display = 'none';
    }
});

// Close chat window
chatCloseBtn.addEventListener('click', function() {
    chatWindow.style.display = 'none';
});

// Send message on button click
chatSendBtn.addEventListener('click', sendChatMessage);

// Send message on Enter key
chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

function sendChatMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
    removeTypingIndicator(typingId);

    if (data.reply) {
        addChatMessage(data.reply, 'bot');
    } else {
        addChatMessage("I'm here to help with finance and general questions!", 'bot');
    }
})


    .catch(error => {
        console.error('Search error:', error);
        removeTypingIndicator(typingId);
        addChatMessage("Oops! Something went wrong. Please try again.", 'bot');
    });
}

function addChatMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatBody.appendChild(messageDiv);
    
    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

function addStockResultToChat(stock) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div>I found this stock:</div>
        <div class="stock-result-card">
            <div class="ticker">${stock.ticker}</div>
            <div class="name">${stock.name}</div>
            <div class="sector-badge">${stock.sector}</div>
            <button class="btn btn-success btn-sm add-stock-btn" onclick="addToWatchlistFromChat('${stock.ticker}', '${stock.name.replace(/'/g, "\\'")}')">
                <i class="fas fa-plus"></i> Add to Watchlist
            </button>
        </div>
    `;
    
    messageDiv.appendChild(contentDiv);
    chatBody.appendChild(messageDiv);
    
    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    const id = 'typing-' + Date.now();
    typingDiv.id = id;
    typingDiv.className = 'chat-message bot-message';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatBody.appendChild(typingDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function addToWatchlistFromChat(ticker, name) {
    addToWatchlist(ticker, name);
    addChatMessage(`✓ Added ${ticker} to your watchlist!`, 'bot');
}

// ============================================
// WATCHLIST MANAGEMENT
// ============================================

// Add to watchlist
function addToWatchlist(ticker, name) {
    if (watchlist.length >= MAX_WATCHLIST) {
        alert(`Watchlist is full! Maximum ${MAX_WATCHLIST} stocks allowed.`);
        return;
    }
    
    if (watchlist.some(item => item.ticker === ticker)) {
        alert(`${ticker} is already in your watchlist!`);
        return;
    }
    
    watchlist.push({ ticker, name });
    updateWatchlistDisplay();
    
    console.log("Added to watchlist:", ticker);
}

// Remove from watchlist
function removeFromWatchlist(ticker) {
    watchlist = watchlist.filter(item => item.ticker !== ticker);
    updateWatchlistDisplay();
}

// Clear watchlist
document.getElementById('clearWatchlist').addEventListener('click', function() {
    if (confirm('Are you sure you want to clear the entire watchlist?')) {
        watchlist = [];
        updateWatchlistDisplay();
    }
});

// Update watchlist display
function updateWatchlistDisplay() {
    const watchlistContainer = document.getElementById('watchlist');
    const watchlistCount = document.getElementById('watchlistCount');
    const clearBtn = document.getElementById('clearWatchlist');
    
    watchlistCount.textContent = `${watchlist.length}/${MAX_WATCHLIST}`;
    
    if (watchlist.length === 0) {
        watchlistContainer.innerHTML = '<p class="text-muted text-center">No stocks added yet</p>';
        clearBtn.style.display = 'none';
        return;
    }
    
    watchlistContainer.innerHTML = '';
    watchlist.forEach(item => {
        const div = document.createElement('div');
        div.className = 'watchlist-item fade-in';
        div.title = item.name; // Show company name on hover
        div.innerHTML = `
            <div>
                <span class="watchlist-ticker">${item.ticker}</span>
            </div>
            <button class="btn btn-sm btn-outline-danger remove-btn" onclick="removeFromWatchlist('${item.ticker}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        watchlistContainer.appendChild(div);
    });
    
    clearBtn.style.display = 'block';
}

// ============================================
// ANALYSIS FUNCTIONALITY
// ============================================

// Analyze watchlist
document.getElementById('analyzeBtn').addEventListener('click', analyzeWatchlist);

function analyzeWatchlist() {
    if (watchlist.length === 0) {
        alert('Please add at least one stock to your watchlist!');
        return;
    }
    
    const period = document.querySelector('input[name="timePeriod"]:checked').value;
    const customStart = document.getElementById('customStartDate').value;
    const customEnd = document.getElementById('customEndDate').value;
    
    // Validate custom dates if selected
    if (period === 'custom' && (!customStart || !customEnd)) {
        alert('Please select both start and end dates for custom range');
        return;
    }
    
    // Show loading, hide other panels
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('welcomeMessage').style.display = 'none';
    document.getElementById('statisticsPanel').style.display = 'none';
    document.getElementById('aiInsightsPanel').style.display = 'none';
    
    const tickers = watchlist.map(item => item.ticker);
    
    console.log("Analyzing tickers:", tickers);
    
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tickers: tickers,
            period: period,
            custom_start: customStart,
            custom_end: customEnd
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Analysis complete:", data);
        currentAnalysisData = data;
        displayAnalysis(data);
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('statisticsPanel').style.display = 'block';
        document.getElementById('aiInsightsPanel').style.display = 'block';
    })
    .catch(error => {
        console.error('Error analyzing watchlist:', error);
        alert('Analysis failed. Please check your internet connection and try again.');
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('welcomeMessage').style.display = 'block';
    });
}

// Display analysis results
function displayAnalysis(data) {
    // Display AI Summary
    document.getElementById('aiSummary').textContent = data.ai_summary;
    
    // Display metrics table
    const tableBody = document.getElementById('metricsTableBody');
    tableBody.innerHTML = '';
    
    data.metrics.forEach(metric => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td title="${metric.name}"><strong>${metric.ticker}</strong></td>
            <td class="${metric.total_return >= 0 ? 'positive-value' : 'negative-value'}">
                ${metric.total_return >= 0 ? '+' : ''}${metric.total_return.toFixed(2)}%
            </td>
            <td class="${metric.annualized_return >= 0 ? 'positive-value' : 'negative-value'}">
                ${metric.annualized_return >= 0 ? '+' : ''}${metric.annualized_return.toFixed(2)}%
            </td>
            <td>${metric.annualized_volatility.toFixed(2)}%</td>
            <td class="${metric.sharpe_ratio > 1 ? 'positive-value' : ''}">
                ${metric.sharpe_ratio.toFixed(2)}
            </td>
            <td class="negative-value">${metric.max_drawdown.toFixed(2)}%</td>
            <td>$${metric.start_price.toFixed(2)}</td>
            <td>$${metric.end_price.toFixed(2)}</td>
            <td>${metric.days}</td>
        `;
        tableBody.appendChild(row);
    });
    
    // Display stock insights
    const insightsContainer = document.getElementById('stockInsights');
    insightsContainer.innerHTML = '<h6 class="mt-3">AI Stock Insights:</h6>';
    
    data.metrics.forEach(metric => {
        const div = document.createElement('div');
        div.className = 'stock-insight-card fade-in';
        div.innerHTML = `
            <div class="insight-ticker">${metric.ticker}</div>
            <p class="insight-text">${metric.ai_insight}</p>
        `;
        insightsContainer.appendChild(div);
    });
    
    // Create visualizations
    createNormalizedChart(data.normalized_prices);
    createReturnsChart(data.metrics);
    createScatterChart(data.metrics);
    createCorrelationMatrix(data.correlation_matrix);
}

// ============================================
// CHART CREATION
// ============================================

// Create normalized performance chart
function createNormalizedChart(normalizedData) {
    const traces = [];
    
    for (const [ticker, data] of Object.entries(normalizedData)) {
        traces.push({
            x: data.dates,
            y: data.values,
            type: 'scatter',
            mode: 'lines',
            name: ticker,
            line: { width: 2 }
        });
    }
    
    const layout = {
        title: 'Normalized Performance (Base 100)',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Normalized Value' },
        hovermode: 'x unified',
        legend: { orientation: 'h', y: -0.2 }
    };
    
    Plotly.newPlot('normalizedChart', traces, layout, { responsive: true });
}

// Create returns bar chart
function createReturnsChart(metrics) {
    const sortedMetrics = [...metrics].sort((a, b) => b.total_return - a.total_return);
    
    const trace = {
        x: sortedMetrics.map(m => m.ticker),
        y: sortedMetrics.map(m => m.total_return),
        type: 'bar',
        marker: {
            color: sortedMetrics.map(m => m.total_return >= 0 ? '#198754' : '#dc3545')
        },
        text: sortedMetrics.map(m => `${m.total_return.toFixed(2)}%`),
        textposition: 'outside'
    };
    
    const layout = {
        title: 'Total Returns by Stock',
        xaxis: { title: 'Ticker' },
        yaxis: { title: 'Return (%)' },
        showlegend: false
    };
    
    Plotly.newPlot('returnsChart', [trace], layout, { responsive: true });
}

// Create risk-return scatter plot
function createScatterChart(metrics) {
    const trace = {
        x: metrics.map(m => m.annualized_volatility),
        y: metrics.map(m => m.annualized_return),
        mode: 'markers+text',
        type: 'scatter',
        text: metrics.map(m => m.ticker),
        textposition: 'top center',
        marker: {
            size: 12,
            color: metrics.map(m => m.sharpe_ratio),
            colorscale: 'Viridis',
            showscale: true,
            colorbar: { title: 'Sharpe Ratio' }
        }
    };
    
    const layout = {
        title: 'Risk vs Return',
        xaxis: { title: 'Volatility (%)' },
        yaxis: { title: 'Annualized Return (%)' },
        hovermode: 'closest'
    };
    
    Plotly.newPlot('scatterChart', [trace], layout, { responsive: true });
}

// Create correlation heatmap
function createCorrelationMatrix(correlationData) {
    if (!correlationData) {
        document.getElementById('correlationChart').innerHTML = '<p class="text-muted">Not enough data for correlation analysis</p>';
        return;
    }
    
    const tickers = Object.keys(correlationData);
    const zValues = tickers.map(ticker1 => 
        tickers.map(ticker2 => correlationData[ticker1][ticker2])
    );
    
    const trace = {
        z: zValues,
        x: tickers,
        y: tickers,
        type: 'heatmap',
        colorscale: 'RdBu',
        zmid: 0,
        colorbar: { title: 'Correlation' }
    };
    
    const layout = {
        title: 'Stock Correlation Matrix',
        xaxis: { side: 'bottom' },
        yaxis: { autorange: 'reversed' }
    };
    
    Plotly.newPlot('correlationChart', [trace], layout, { responsive: true });
}

// ============================================
// EXPORT FUNCTIONALITY
// ============================================

// Export to CSV
document.getElementById('exportBtn').addEventListener('click', function() {
    if (!currentAnalysisData || !currentAnalysisData.metrics) {
        alert('No data to export. Please analyze your watchlist first.');
        return;
    }
    
    fetch('/api/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ metrics: currentAnalysisData.metrics })
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `watchlist_analysis_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Export error:', error);
        alert('Export failed. Please try again.');
    });
});

// ============================================
// EXPLANATION MODAL
// ============================================

// Explain concept function
function explainConcept(concept) {
    const modal = new bootstrap.Modal(document.getElementById('explanationModal'));
    document.getElementById('explanationModalLabel').textContent = concept;
    document.getElementById('explanationContent').innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    modal.show();
    
    fetch('/api/explain', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ concept: concept })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('explanationContent').innerHTML = `
            <div class="explanation-text">${data.explanation.replace(/\n/g, '<br><br>')}</div>
        `;
    })
    .catch(error => {
        console.error('Explanation error:', error);
        document.getElementById('explanationContent').innerHTML = `
            <div class="alert alert-danger">Failed to load explanation. Please try again.</div>
        `;
    });
}

// ============================================
// CUSTOM DATE HANDLING
// ============================================

// Handle custom date selection
document.getElementById('customStartDate').addEventListener('change', function() {
    // Auto-select custom period when dates are chosen
    const customRadio = document.getElementById('periodCustom');
    if (customRadio) {
        customRadio.checked = true;
    }
});

document.getElementById('customEndDate').addEventListener('change', function() {
    const customRadio = document.getElementById('periodCustom');
    if (customRadio) {
        customRadio.checked = true;
    }
});

console.log("All event listeners initialized");

const stockSearchInput = document.getElementById('stockSearchInput');
const searchResultsBox = document.getElementById('searchResults');

stockSearchInput.addEventListener('input', function () {
    const query = this.value.trim();

    if (query.length < 2) {
        searchResultsBox.style.display = 'none';
        return;
    }

    fetch('/api/search_ticker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        searchResultsBox.innerHTML = '';

        if (!data.results || data.results.length === 0) {
            searchResultsBox.style.display = 'none';
            return;
        }

        data.results.forEach(stock => {
            const item = document.createElement('button');
            item.className = 'list-group-item list-group-item-action';
            item.innerHTML = `<strong>${stock.ticker}</strong> — ${stock.name} <span class="badge bg-secondary">${stock.sector}</span>`;

            item.onclick = () => {
                addToWatchlist(stock.ticker, stock.name);
                stockSearchInput.value = '';
                searchResultsBox.style.display = 'none';
            };

            searchResultsBox.appendChild(item);
        });

        searchResultsBox.style.display = 'block';
    });
});
