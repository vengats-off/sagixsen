"""
Main Application Entry Point - FIXED VERSION
"""

from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import os

# Create main Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure CORS
CORS(app, origins=[
    "https://sagixsen.onrender.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

# Import sentiment analysis module
try:
    from sentiment_module import (
        get_news as sentiment_get_news,
        health_check as sentiment_health_check
    )
    print("✅ Sentiment module loaded")
except ImportError as e:
    print(f"⚠️ Warning: Could not load sentiment module: {e}")
    sentiment_get_news = None
    sentiment_health_check = None

# Import news simplification module
try:
    from news_module import (
        search_news,
        simplify_custom_text,
        get_trending_topics,
        health_check as news_health_check
    )
    print("✅ News simplification module loaded")
except ImportError as e:
    print(f"⚠️ Warning: Could not load news module: {e}")
    search_news = None
    simplify_custom_text = None
    get_trending_topics = None
    news_health_check = None


# =====================================================
# FRONTEND ROUTES
# =====================================================

@app.route('/')
def homepage():
    """Main homepage"""
    return render_template('index.html')

@app.route('/sentiment')
def sentiment_page():
    """Sentiment analysis page"""
    return render_template('sentiment.html')

@app.route('/news')
def news_page():
    """News simplification page"""
    return render_template('news.html')


# =====================================================
# STATIC FILE ROUTES
# =====================================================

@app.route('/companies.js')
def serve_companies_js():
    return send_from_directory('static/js', 'companies.js')

@app.route('/sentment-app.js')
def serve_sentiment_app_js():
    return send_from_directory('static/js', 'sentment-app.js')

@app.route('/sentiment-style.css')
def serve_sentiment_css():
    return send_from_directory('static/css', 'sentiment-style.css')

@app.route('/news_app.js')
def serve_news_app_js():
    return send_from_directory('static/js', 'news-app.js')

@app.route('/news-style.css')
def serve_news_css():
    return send_from_directory('static/css', 'news-style.css')

@app.route('/logo.png')
def serve_logo():
    return send_from_directory('.', 'logo.png')


# =====================================================
# SENTIMENT ANALYSIS API ROUTES
# =====================================================

@app.route('/api/news', methods=['GET'])
def api_sentiment_news():
    """Sentiment analysis endpoint"""
    if sentiment_get_news:
        return sentiment_get_news()
    else:
        return {"error": "Sentiment module not loaded"}, 500

@app.route('/api/sentiment-health', methods=['GET'])
def api_sentiment_health():
    """Sentiment health check"""
    if sentiment_health_check:
        return sentiment_health_check()
    else:
        return {"status": "unavailable"}, 503


# =====================================================
# NEWS SIMPLIFICATION API ROUTES
# =====================================================

@app.route('/api/search-news', methods=['POST'])
def api_search_news():
    """News search and simplification endpoint"""
    if search_news:
        return search_news()
    else:
        return {"error": "News module not loaded"}, 500

@app.route('/api/simplify-text', methods=['POST'])
def api_simplify_text():
    """Simplify custom text endpoint"""
    if simplify_custom_text:
        return simplify_custom_text()
    else:
        return {"error": "News module not loaded"}, 500

@app.route('/api/trending-topics', methods=['GET'])
def api_trending_topics():
    """Trending topics endpoint"""
    if get_trending_topics:
        return get_trending_topics()
    else:
        return {"error": "News module not loaded"}, 500

@app.route('/api/trending', methods=['GET'])
def api_trending():
    """Alternative trending endpoint"""
    return api_trending_topics()

@app.route('/api/news-health', methods=['GET'])
def api_news_health():
    """News health check"""
    if news_health_check:
        return news_health_check()
    else:
        return {"status": "unavailable"}, 503


# =====================================================
# MASTER HEALTH CHECK
# =====================================================

@app.route('/api/health', methods=['GET'])
def master_health_check():
    """Combined health check for all services"""
    from datetime import datetime, timezone
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': {
            'sentiment_analysis': 'available' if sentiment_get_news else 'unavailable',
            'news_simplification': 'available' if search_news else 'unavailable'
        },
        'deployment': 'unified',
        'message': 'All services running in single process'
    }
    
    return health_status


# =====================================================
# APPLICATION STARTUP
# =====================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("🚀 SagiX Application Starting")
    print("="*60)
    print(f"📍 Port: {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print("\n📦 Available Services:")
    print(f"   {'✅' if sentiment_get_news else '❌'} Sentiment Analysis")
    print(f"   {'✅' if search_news else '❌'} News Simplification")
    print("\n📄 Pages:")
    print(f"   🏠 Homepage:    http://localhost:{port}/")
    print(f"   📊 Sentiment:   http://localhost:{port}/sentiment")
    print(f"   📰 News:        http://localhost:{port}/news")
    print("\n🔌 API Endpoints:")
    print(f"   GET  /api/news              (Sentiment)")
    print(f"   POST /api/search-news       (News Search)")
    print(f"   POST /api/simplify-text     (Text Simplify)")
    print(f"   GET  /api/trending-topics   (Trending)")
    print(f"   GET  /api/health            (Health Check)")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)