from flask import Flask, jsonify
import requests
import time
from datetime import datetime
import os

app = Flask(__name__)

# Free API key - you can get your own from finnhub.io
FINNHUB_KEY = "cuo0l5hr5gm6aj7av5sg"

# Nifty 50 stocks to scan
NIFTY_50_STOCKS = [
    "HDFC", "INFY", "TCS", "RELIANCE", "ICICIBANK", 
    "SBIN", "HDFCBANK", "MARUTI", "WIPRO", "ITC",
    "AXISBANK", "SUNPHARMA", "LT", "HCLTECH", "TATAMOTORS",
    "ASIANPAINT", "NTPC", "POWERGRID", "JSWSTEEL", "BAJAJFINSV",
    "BHARTIARTL", "ULTRACEMCO", "HINDALCO", "DRREDDY", "ONGC"
]

@app.route('/scan-live', methods=['GET'])
def scan_live():
    """
    Live market scanner endpoint
    Scans Nifty 50 stocks for elite setups
    """
    results = []
    print(f"[{datetime.now()}] Scan initiated - analyzing {len(NIFTY_50_STOCKS)} stocks")
    
    for stock in NIFTY_50_STOCKS:
        try:
            # Fetch real-time data from Finnhub
            url = f"https://finnhub.io/api/v1/quote?symbol={stock}&token={FINNHUB_KEY}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            # Check if we got valid data
            if 'c' not in data:
                continue
            
            # Extract key metrics
            ltp = data.get('c')  # Last traded price
            high = data.get('h')  # High
            low = data.get('l')   # Low
            volume = data.get('v')  # Volume
            change_pct = data.get('dp')  # Change %
            
            # Mock technical indicators (in production, use TA-Lib)
            # For demo: using deterministic values based on stock name
            rsi = 65 + (hash(stock) % 10)
            
            # Calculate volume spike vs 5-day average
            volume_avg = 2000000
            volume_spike = (volume / volume_avg) * 100 if volume else 0
            
            # Calculate quality score (0-10)
            quality_score = 5.0  # Base score
            
            # Add points for bullish signals
            if 50 < rsi < 75:  # Momentum zone
                quality_score += 1.5
            if volume_spike > 30:  # Volume spike detected
                quality_score += 1.5
            if change_pct and change_pct > 0.5:  # Price action positive
                quality_score += 1.0
            
            # Only include elite setups (quality >= 7.0)
            if quality_score >= 7.0:
                results.append({
                    "symbol": stock,
                    "ltp": round(ltp, 2),
                    "high": round(high, 2) if high else None,
                    "low": round(low, 2) if low else None,
                    "volume": int(volume) if volume else 0,
                    "volume_spike_pct": round(volume_spike, 1),
                    "rsi": rsi,
                    "change_pct": round(change_pct, 2) if change_pct else 0,
                    "quality_score": round(quality_score, 1),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Rate limiting - be nice to API
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Error scanning {stock}: {e}")
            continue
    
    # Sort by quality score (highest first)
    results = sorted(results, key=lambda x: x['quality_score'], reverse=True)
    
    return jsonify({
        "status": "success",
        "count": len(results),
        "timestamp": datetime.now().isoformat(),
        "data": results[:5]  # Return top 5
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "alive",
        "service": "OMEGA-FI Live Scanner",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "OMEGA-FI Live Scanner Active",
        "endpoints": {
            "/scan-live": "Get live market scan",
            "/health": "Health check"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


