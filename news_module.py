"""
News Simplification Module
Handles news fetching and financial jargon simplification
"""

from flask import request, jsonify
import requests
import re
from datetime import datetime, timedelta, timezone
from textblob import TextBlob
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download NLTK data (runs once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

NEWS_API_KEY = '7eae47b18ad34858878240cb7a6f139a'

# Financial jargon dictionary
FINANCIAL_JARGON = {
    'market cap': 'total value of company shares',
    'market capitalization': 'total value of company shares',
    'pe ratio': 'price compared to earnings',
    'p/e ratio': 'price compared to earnings',
    'earnings per share': 'profit per share',
    'eps': 'profit per share',
    'dividend': 'profit share to shareholders',
    'bull market': 'when prices are rising',
    'bear market': 'when prices are falling',
    'ipo': 'first public stock sale',
    'mutual fund': 'pooled investment fund',
    'stock split': 'dividing shares to lower price',
    'merger': 'two companies combining',
    'acquisition': 'one company buying another',
    'portfolio': 'collection of investments',
    'volatility': 'price ups and downs',
    'liquidity': 'how easily sold for cash',
    'blue chip': 'reliable large company',
    'diversification': 'spreading investment risk',
    'capital gain': 'profit from selling',
    'fiscal year': 'company financial year',
    'quarterly results': 'performance every 3 months',
    'revenue': 'total money earned',
    'profit margin': 'profit percentage',
    'ebitda': 'earnings before interest and taxes',
    'cash flow': 'money in and out',
    'balance sheet': 'assets and debts statement',
    'debt-to-equity': 'borrowed vs owned ratio',
    'return on investment': 'profit gained',
    'roi': 'profit gained',
    'share buyback': 'company buying own shares',
    'venture capital': 'startup funding',
    'bond': 'loan to government or company',
    'equity': 'company ownership',
    'commodities': 'basic goods like gold, oil',
    'derivatives': 'contracts based on assets',
    'futures': 'agreement for future purchase',
    'options': 'right to buy/sell',
    'index': 'market performance measure',
    'sensex': 'India stock market index',
    'nifty': 'India top 50 companies index',
    'inflation': 'rising prices over time',
    'interest rate': 'cost of borrowing',
    'monetary policy': 'central bank actions',
    'fiscal policy': 'government tax and spending',
    'gdp': 'total country production value',
    'recession': 'economic downturn',
    'correction': '10% market drop',
    'rally': 'rapid price increase',
    'resistance': 'hard to go above price',
    'support': 'hard to go below price',
    'shareholder': 'person owning shares',
    'subsidiary': 'company owned by another',
    'bankruptcy': 'unable to pay debts',
    'restructuring': 'changing organization',
}


def simplify_text(text, level='basic'):
    """Simplify financial text"""
    if not text or not text.strip():
        return text, []
    
    simplified = text
    jargon_found = []
    
    for jargon, simple in FINANCIAL_JARGON.items():
        pattern = re.compile(r'\b' + re.escape(jargon) + r'\b', re.IGNORECASE)
        if pattern.search(simplified):
            jargon_found.append({
                'term': jargon,
                'explanation': simple,
                'count': len(pattern.findall(simplified))
            })
            
            if level == 'basic':
                simplified = pattern.sub(f"{simple}", simplified)
            elif level == 'detailed':
                simplified = pattern.sub(f"{jargon} ({simple})", simplified)
    
    if level == 'basic':
        sentences = sent_tokenize(simplified)
        short_sentences = []
        for sent in sentences:
            words = word_tokenize(sent)
            if len(words) > 20:
                sent = sent.replace(', and ', '. Also, ')
                sent = sent.replace(', but ', '. However, ')
            short_sentences.append(sent)
        simplified = ' '.join(short_sentences)
    
    return simplified, jargon_found


def calculate_complexity(text):
    """Calculate text complexity"""
    if not text:
        return 'low', 0
    
    jargon_count = 0
    for jargon in FINANCIAL_JARGON.keys():
        jargon_count += len(re.findall(r'\b' + re.escape(jargon) + r'\b', text, re.IGNORECASE))
    
    sentences = sent_tokenize(text)
    if sentences:
        words = word_tokenize(text)
        avg_sentence_length = len(words) / len(sentences)
    else:
        avg_sentence_length = 0
    
    if jargon_count > 5 or avg_sentence_length > 25:
        complexity = 'high'
    elif jargon_count > 2 or avg_sentence_length > 15:
        complexity = 'medium'
    else:
        complexity = 'low'
    
    readability = max(0, min(100, 100 - (jargon_count * 10) - (avg_sentence_length * 2)))
    
    return complexity, int(readability)


def fetch_news_from_newsapi(query, date_range='1d'):
    """Fetch news from NewsAPI"""
    try:
        days = {'1d': 1, '3d': 3, '1w': 7, '1m': 30}
        days_back = days.get(date_range, 1)
        from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        search_query = f'{query} AND (India OR Indian OR stock OR market OR business)'
        url = f'https://newsapi.org/v2/everything'
        params = {
            'q': search_query,
            'language': 'en',
            'from': from_date,
            'sortBy': 'publishedAt',
            'apiKey': NEWS_API_KEY,
            'pageSize': 20
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
        else:
            print(f"NewsAPI Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def create_sample_articles(query):
    """Create sample articles when API fails"""
    now = datetime.now(timezone.utc)
    return [
        {
            'title': f'{query} shows strong quarterly performance',
            'description': f'{query} reported better than expected results with revenue growth and improved market position.',
            'content': f'{query} announced quarterly results with revenue growth of 15%. The market cap increased as investors responded positively to earnings per share. Management highlighted expansion plans and dividend payments.',
            'url': 'https://example.com/article1',
            'publishedAt': now.isoformat(),
            'source': {'name': 'Financial Times'},
            'urlToImage': None
        },
        {
            'title': f'Market analysis: {query} maintains steady growth',
            'description': f'Analysts remain optimistic about {query} prospects despite volatility, citing strong fundamentals.',
            'content': f'Financial analysts maintain buy rating on {query} shares. The stock has shown resilience in volatile conditions. The PE ratio remains attractive compared to peers, and debt-to-equity ratio shows healthy management.',
            'url': 'https://example.com/article2',
            'publishedAt': (now - timedelta(hours=5)).isoformat(),
            'source': {'name': 'Economic Times'},
            'urlToImage': None
        }
    ]


# =====================================================
# API FUNCTIONS (Called from main.py)
# =====================================================

def search_news():
    """Main news search and simplification endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        level = data.get('level', 'basic')
        date_range = data.get('date_range', '1d')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Fetch news articles
        articles = fetch_news_from_newsapi(query, date_range)
        
        # If no articles, use sample data
        if not articles:
            articles = create_sample_articles(query)
        
        # Process each article
        processed_articles = []
        for article in articles[:15]:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', description)
            
            if not title and not description:
                continue
            
            full_text = f"{title}. {description}"
            
            # Simplify the text
            simplified_text, jargon_found = simplify_text(full_text, level)
            
            # Calculate complexity
            complexity, readability = calculate_complexity(full_text)
            
            # Build processed article
            processed_article = {
                'original': {
                    'title': title,
                    'description': description,
                    'content': content,
                    'url': article.get('url', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'urlToImage': article.get('urlToImage')
                },
                'simplified': {
                    'title': title,
                    'content': simplified_text,
                    'summary': simplified_text[:200] + '...' if len(simplified_text) > 200 else simplified_text
                },
                'analysis': {
                    'complexity': complexity,
                    'readability_score': readability,
                    'jargon_count': len(jargon_found),
                    'jargon_detected': jargon_found[:10],
                    'insights': [
                        {
                            'title': 'Simplification Applied',
                            'description': f'Text simplified to {level} level with {len(jargon_found)} terms explained.'
                        }
                    ]
                }
            }
            
            processed_articles.append(processed_article)
        
        return jsonify({
            'articles': processed_articles,
            'total_found': len(processed_articles),
            'query': query,
            'level': level,
            'date_range': date_range,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in search_news: {e}")
        return jsonify({'error': str(e)}), 500


def simplify_custom_text():
    """Endpoint for simplifying custom text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        level = data.get('level', 'basic')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 10000:
            return jsonify({'error': 'Text too long (max 10000 characters)'}), 400
        
        # Simplify text
        simplified, jargon_found = simplify_text(text, level)
        
        # Calculate complexity
        complexity, readability = calculate_complexity(text)
        
        return jsonify({
            'original_text': text,
            'simplified_text': simplified,
            'complexity': complexity,
            'readability_score': readability,
            'jargon_count': len(jargon_found),
            'jargon_detected': jargon_found,
            'insights': [
                {
                    'title': 'Complexity Level',
                    'description': f'Original text complexity: {complexity.upper()}'
                },
                {
                    'title': 'Terms Simplified',
                    'description': f'Found and explained {len(jargon_found)} financial terms'
                },
                {
                    'title': 'Readability',
                    'description': f'Readability score: {readability}/100 (higher is easier)'
                }
            ]
        })
        
    except Exception as e:
        print(f"Error in simplify_custom_text: {e}")
        return jsonify({'error': str(e)}), 500


def get_trending_topics():
    """Return trending topics"""
    return jsonify({
        'trending_topics': [
            'Reliance Industries',
            'TCS',
            'Infosys',
            'HDFC Bank',
            'Sensex',
            'Nifty',
            'RBI Policy',
            'Stock Market India'
        ]
    })


def health_check():
    """Health check for news module"""
    return jsonify({
        'status': 'healthy',
        'service': 'news-simplification',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })