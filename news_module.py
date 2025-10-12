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
    # Basic Market Terms
    'market': 'buying and selling of stocks',
    'stock market': 'place where company shares are bought and sold',
    'share': 'small piece of company ownership',
    'shares': 'small pieces of company ownership',
    'stock': 'piece of company ownership',
    'stocks': 'pieces of company ownership',
    'investor': 'person who buys stocks',
    'investors': 'people who buy stocks',
    'trading': 'buying and selling',
    'trader': 'person who buys and sells stocks',
    
    # Company Actions
    'going public': 'company selling shares to public for first time',
    'ipo': 'company selling shares to public for first time',
    'launches': 'starts or introduces',
    'launched': 'started or introduced',
    'unveils': 'shows or announces',
    'unveiled': 'showed or announced',
    'announces': 'tells publicly',
    'announced': 'told publicly',
    'introduces': 'brings in something new',
    'introduced': 'brought in something new',
    
    # Financial Performance
    'ascent': 'going up or growing',
    'growth': 'increase or expansion',
    'rise': 'going up',
    'surge': 'big increase',
    'rally': 'prices going up fast',
    'gain': 'profit or increase',
    'gains': 'profits or increases',
    'profit': 'money earned after expenses',
    'profits': 'money earned after expenses',
    'loss': 'money lost',
    'losses': 'money lost',
    'revenue': 'total money earned',
    'earnings': 'money made',
    'income': 'money received',
    
    # Market Movement
    'close': 'end of trading day',
    'closes': 'ends trading day',
    'closed': 'ended trading day',
    'settled': 'ended at a price',
    'lead': 'be first or main',
    'leads': 'is first or main',
    'led': 'was first or main',
    
    # Specific Terms from Your Articles
    'fraud': 'cheating or dishonest activity',
    'decoded': 'explained simply',
    'litmus test': 'important test to check something',
    'sector': 'industry or business area',
    'banking sector': 'all banks together',
    'pharma': 'medicine companies',
    'public listings': 'companies selling shares to public',
    'digital': 'online or electronic',
    'instant': 'very fast or immediate',
    'storefront': 'shop or store',
    'merchants': 'shop owners or sellers',
    'small businesses': 'small shops and companies',
    'revolutionising': 'completely changing',
    'connect': 'link or join',
    'customers': 'people who buy',
    
    # Indian Market Terms
    'sensex': 'India\'s main stock market number',
    'nifty': 'India\'s top 50 companies index number',
    'index': 'number showing market performance',
    'banking': 'money lending and saving business',
    'week': '7 days',
    'strong note': 'good performance',
    'points': 'units to measure market',
    'higher': 'more or increased',
    
    # Financial Ratios & Metrics
    'market cap': 'total company value',
    'market capitalization': 'total company value',
    'pe ratio': 'how expensive stock is',
    'p/e ratio': 'how expensive stock is',
    'eps': 'profit per share',
    'earnings per share': 'profit for each share',
    
    # Investment Terms
    'dividend': 'company giving money to shareholders',
    'bull market': 'when prices keep going up',
    'bear market': 'when prices keep going down',
    'mutual fund': 'money pooled from many people to invest',
    'portfolio': 'all investments someone owns',
    'diversification': 'not putting all eggs in one basket',
    
    # Company Structure
    'merger': 'two companies becoming one',
    'acquisition': 'one company buying another',
    'subsidiary': 'company owned by another company',
    'partnership': 'two companies working together',
    'collaboration': 'working together',
    'alliance': 'agreement to work together',
    'joint venture': 'two companies starting something together',
    
    # Financial Health
    'debt': 'money borrowed',
    'loan': 'borrowed money',
    'credit': 'borrowed money',
    'equity': 'ownership in company',
    'assets': 'things company owns',
    'liabilities': 'money company owes',
    'balance sheet': 'report of what company owns and owes',
    'cash flow': 'money coming in and going out',
    
    # Market Activity
    'volatility': 'prices moving up and down a lot',
    'liquidity': 'how easily something can be sold',
    'volume': 'amount of trading',
    'bid': 'offer to buy',
    'ask': 'offer to sell',
    
    # Company Size & Type
    'blue chip': 'big reliable company',
    'startup': 'new company',
    'sme': 'small and medium business',
    'msme': 'micro, small and medium enterprise',
    'corporation': 'big company',
    
    # Government & Policy
    'rbi': 'Reserve Bank of India, controls money supply',
    'monetary policy': 'RBI\'s decisions about money',
    'fiscal policy': 'government tax and spending plans',
    'interest rate': 'cost of borrowing money',
    'inflation': 'things becoming more expensive',
    'gdp': 'total value of country\'s production',
    'recession': 'when economy is doing badly',
    
    # Investment Strategies
    'buy': 'purchase',
    'sell': 'give away for money',
    'hold': 'keep without selling',
    'long term': 'for many years',
    'short term': 'for few days or months',
    
    # Financial Documents
    'quarterly results': 'company report every 3 months',
    'annual report': 'yearly company report',
    'prospectus': 'document about company',
    
    # Risk Terms
    'risk': 'chance of losing money',
    'hedge': 'protection against loss',
    'insurance': 'protection',
    
    # Other Business Terms
    'expansion': 'growing bigger',
    'restructuring': 'changing how company works',
    'bankruptcy': 'can\'t pay debts',
    'layoffs': 'firing employees',
    'hiring': 'giving jobs',
    'investment': 'putting money to make more money',
    'funding': 'getting money',
    'venture capital': 'money for new companies',
    
    # Price Terms
    'valuation': 'how much company is worth',
    'overvalued': 'priced too high',
    'undervalued': 'priced too low',
    'premium': 'extra cost',
    'discount': 'reduced price',
    
    # Trading Terms
    'futures': 'agreement to buy later',
    'options': 'right to buy or sell',
    'derivatives': 'financial contracts',
    'commodities': 'basic goods like gold, oil',
    'bond': 'loan to government or company',
    
    # Performance Indicators
    'profit margin': 'how much profit from sales',
    'return on investment': 'profit made from investment',
    'roi': 'profit made from investment',
    'yield': 'return or profit',
    
    # Corporate Actions
    'share buyback': 'company buying its own shares',
    'stock split': 'dividing shares to lower price',
    'bonus shares': 'free shares given to shareholders',
    'rights issue': 'offering shares to existing shareholders',
    
    # Market Conditions
    'correction': 'market falling 10%',
    'crash': 'market falling very fast',
    'boom': 'market doing very well',
    'bubble': 'prices too high, will fall',
    'resistance': 'price level hard to cross up',
    'support': 'price level hard to go below',
    
    # Company Events
    'agm': 'annual general meeting',
    'board meeting': 'meeting of company leaders',
    'shareholder': 'person owning shares',
    'stakeholder': 'anyone affected by company',
    
    # Financial Reporting
    'ebitda': 'earnings before costs',
    'net profit': 'final profit after all expenses',
    'gross profit': 'profit before all costs',
    'operating profit': 'profit from main business',
    
    # Analyst Terms
    'upgrade': 'saying stock will do better',
    'downgrade': 'saying stock will do worse',
    'target price': 'expected future price',
    'rating': 'expert opinion',
    'recommendation': 'expert advice',
    'bullish': 'expecting prices to go up',
    'bearish': 'expecting prices to go down',
    
    # Legal & Compliance
    'sebi': 'Securities and Exchange Board of India, market regulator',
    'compliance': 'following rules',
    'regulation': 'official rule',
    'audit': 'official check of accounts',
    'disclosure': 'revealing information',
    
    # Additional Common Terms
    'quarter': '3 months',
    'fiscal year': 'company\'s financial year',
    'year-on-year': 'compared to last year',
    'month-on-month': 'compared to last month',

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