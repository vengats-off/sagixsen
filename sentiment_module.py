"""
Sentiment Analysis Module
Extracted from your existing app.py - keeps all your sentiment logic
"""

from flask import request, jsonify
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Your existing API key
API_KEY = '7eae47b18ad34858878240cb7a6f139a'
analyzer = SentimentIntensityAnalyzer()


def finbert_sentiment_analysis(text):
    """Enhanced financial sentiment analysis"""
    if not text or text.strip() == "":
        return "neutral", 0.5, "No content to analyze"
    
    text_lower = text.lower().strip()
    
    positive_indicators = {
        'partnership': 0.5, 'pact': 0.5, 'agreement': 0.4, 'tie-up': 0.4,
        'collaboration': 0.4, 'alliance': 0.4, 'joint venture': 0.5,
        'launch': 0.4, 'introduces': 0.4, 'expansion': 0.5, 'foray': 0.4,
        'growth': 0.4, 'increase': 0.3, 'rise': 0.3, 'surge': 0.5,
        'profit': 0.6, 'revenue growth': 0.5, 'earnings': 0.4, 'dividend': 0.4,
        'buyback': 0.5, 'bonus': 0.3, 'record': 0.4, 'strong': 0.3,
        'contract': 0.4, 'deal': 0.4, 'order': 0.3, 'wins': 0.5,
        'acquisition': 0.4, 'investment': 0.4, 'funding': 0.4,
        'upgrade': 0.5, 'outperform': 0.6, 'buy rating': 0.7,
        'target raised': 0.6, 'bullish': 0.5, 'beat estimates': 0.6
    }
    
    negative_indicators = {
        'slashed': -0.7, 'cut': -0.5, 'reduced': -0.4, 'lowered': -0.4,
        'downgrade': -0.6, 'target cut': -0.6, 'decline': -0.4, 'fall': -0.4,
        'drop': -0.5, 'plunge': -0.7, 'loss': -0.6, 'losses': -0.6,
        'deficit': -0.5, 'bearish': -0.5, 'concern': -0.4, 'worry': -0.4,
        'investigation': -0.6, 'probe': -0.5, 'lawsuit': -0.5,
        'penalty': -0.5, 'scandal': -0.8, 'layoffs': -0.7,
        'bankruptcy': -0.9, 'debt': -0.4, 'underperform': -0.5,
        'sell rating': -0.7, 'missed estimates': -0.6
    }
    
    vader_scores = analyzer.polarity_scores(text)
    base_score = vader_scores['compound']
    
    financial_adjustment = 0
    positive_matches = []
    negative_matches = []
    
    for indicator, weight in positive_indicators.items():
        if indicator in text_lower:
            financial_adjustment += weight
            positive_matches.append(indicator)
    
    for indicator, weight in negative_indicators.items():
        if indicator in text_lower:
            financial_adjustment += weight
            negative_matches.append(indicator)
    
    final_score = base_score + financial_adjustment
    final_score = max(-1.0, min(1.0, final_score))
    
    if final_score >= 0.2:
        sentiment = "positive"
        confidence = min(0.95, 0.6 + abs(final_score * 0.4))
    elif final_score <= -0.2:
        sentiment = "negative"
        confidence = min(0.95, 0.6 + abs(final_score * 0.4))
    else:
        sentiment = "neutral"
        confidence = 0.6
    
    reasoning_parts = []
    if positive_matches:
        reasoning_parts.append(f"Positive: {', '.join(positive_matches[:3])}")
    if negative_matches:
        reasoning_parts.append(f"Negative: {', '.join(negative_matches[:3])}")
    if not positive_matches and not negative_matches:
        reasoning_parts.append("Based on overall tone")
    
    reasoning = " | ".join(reasoning_parts) + f" (Score: {final_score:.2f})"
    
    return sentiment, confidence, reasoning


def get_company_variations(company_name):
    """Get company name variations"""
    variations = [company_name.lower(), company_name.upper()]
    
    company_mappings = {
        'TCS': ['tata consultancy', 'tcs ltd'],
        'SBIN': ['state bank', 'sbi'],
        'RELIANCE': ['reliance industries', 'ril'],
        'INFY': ['infosys', 'infosys ltd'],
        'HDFC': ['hdfc bank', 'hdfc ltd'],
        'ICICIBANK': ['icici bank'],
        'M&M': ['mahindra', 'mahindra & mahindra'],
        'MARUTI': ['maruti suzuki'],
        'BHARTIARTL': ['bharti airtel', 'airtel'],
        'WIPRO': ['wipro ltd'],
        'LT': ['larsen toubro', 'l&t'],
        'TATASTEEL': ['tata steel'],
        'TATAMOTORS': ['tata motors'],
        'AXISBANK': ['axis bank'],
        'SUNPHARMA': ['sun pharma'],
        'DRREDDY': ['dr reddy', 'drl'],
        'HINDUNILVR': ['hindustan unilever', 'hul'],
        'ASIANPAINT': ['asian paints'],
        'BAJFINANCE': ['bajaj finance'],
        'ADANIENT': ['adani enterprises', 'adani group'],
        'ITC': ['itc ltd'],
        'ONGC': ['oil natural gas'],
        'NTPC': ['ntpc ltd'],
        'COALINDIA': ['coal india'],
        'IOC': ['indian oil'],
        'BPCL': ['bharat petroleum'],
        'HINDPETRO': ['hindustan petroleum']
    }
    
    if company_name.upper() in company_mappings:
        variations.extend(company_mappings[company_name.upper()])
    
    return variations


def get_date_filter(date_range):
    """Convert date range to NewsAPI format"""
    now = datetime.now(timezone.utc)
    
    if date_range == '1d':
        from_date = now - timedelta(days=1)
    elif date_range == '3d':
        from_date = now - timedelta(days=3)
    elif date_range == '1w':
        from_date = now - timedelta(days=7)
    elif date_range == '1m':
        from_date = now - timedelta(days=30)
    else:
        from_date = now - timedelta(days=1)
    
    return from_date.strftime('%Y-%m-%d')


def get_newsapi_articles(company_name, date_range):
    """Get articles from NewsAPI"""
    articles = []
    
    try:
        from_date = get_date_filter(date_range)
        query = f'"{company_name}" AND (India OR Indian OR stock OR market OR business)'
        url = f'https://newsapi.org/v2/everything?q={query}&language=en&from={from_date}&sortBy=publishedAt&apiKey={API_KEY}'
        
        print(f"  NewsAPI query: {query} from {from_date}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            company_variations = get_company_variations(company_name)
            
            for article in data.get('articles', []):
                title = article.get('title', '') or ''
                description = article.get('description', '') or ''
                
                combined_text = f"{title} {description}".lower()
                if any(var in combined_text for var in company_variations):
                    text_for_analysis = f"{title} {description}"
                    sentiment, confidence, reasoning = finbert_sentiment_analysis(text_for_analysis)
                    
                    article['sentiment'] = sentiment
                    article['sentiment_confidence'] = round(confidence, 3)
                    article['sentiment_reasoning'] = reasoning
                    
                    articles.append(article)
                    
                    if len(articles) >= 15:
                        break
            
            print(f"  NewsAPI: Found {len(articles)} relevant articles")
        
        elif response.status_code == 429:
            print("  NewsAPI: Rate limited")
        else:
            print(f"  NewsAPI: Error {response.status_code}")
    
    except Exception as e:
        print(f"  NewsAPI error: {e}")
    
    return articles


def get_rss_articles(company_name):
    """Get articles from RSS feeds"""
    articles = []
    company_variations = get_company_variations(company_name)
    
    rss_feeds = [
        {'url': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms', 'name': 'Economic Times'},
        {'url': 'https://www.business-standard.com/rss/markets-106.rss', 'name': 'Business Standard'},
        {'url': 'https://www.livemint.com/rss/markets', 'name': 'LiveMint'}
    ]
    
    for feed in rss_feeds:
        try:
            parsed_feed = feedparser.parse(feed['url'])
            
            for entry in parsed_feed.entries[:10]:
                title = getattr(entry, 'title', '')
                summary = getattr(entry, 'summary', '')
                combined_text = f"{title} {summary}".lower()
                
                if any(var in combined_text for var in company_variations):
                    sentiment, confidence, reasoning = finbert_sentiment_analysis(f"{title} {summary}")
                    
                    articles.append({
                        'title': title,
                        'description': summary,
                        'url': getattr(entry, 'link', ''),
                        'publishedAt': getattr(entry, 'published', datetime.now(timezone.utc).isoformat()),
                        'source': {'name': feed['name']},
                        'sentiment': sentiment,
                        'sentiment_confidence': round(confidence, 3),
                        'sentiment_reasoning': reasoning,
                        'urlToImage': None
                    })
                    
                    if len(articles) >= 5:
                        break
                        
        except Exception as e:
            print(f"  RSS {feed['name']} error: {e}")
            continue
    
    print(f"  RSS: Found {len(articles)} articles")
    return articles


def create_enhanced_sample_articles(company_name, date_range):
    """Create sample articles"""
    now = datetime.now(timezone.utc)
    
    if date_range == '1m':
        return [
            {
                'title': f'{company_name} reports quarterly earnings with mixed results',
                'description': f'Latest quarterly earnings from {company_name} show revenue growth but margin pressures.',
                'url': 'https://example.com/earnings',
                'publishedAt': (now - timedelta(days=7)).isoformat(),
                'source': {'name': 'Financial Express'},
                'sentiment': 'neutral',
                'sentiment_confidence': 0.68,
                'sentiment_reasoning': 'Mixed indicators (Score: 0.1)',
                'urlToImage': None
            }
        ]
    else:
        return [
            {
                'title': f'{company_name} maintains steady performance',
                'description': f'{company_name} trading within expected ranges with stable investor sentiment.',
                'url': 'https://example.com/analysis',
                'publishedAt': now.isoformat(),
                'source': {'name': 'Market Analysis'},
                'sentiment': 'neutral',
                'sentiment_confidence': 0.65,
                'sentiment_reasoning': 'Based on overall tone (Score: 0.02)',
                'urlToImage': None
            }
        ]


def remove_duplicates(articles):
    """Remove duplicate articles"""
    seen_titles = set()
    unique_articles = []
    
    for article in articles:
        title = article.get('title', '').lower().strip()
        first_words = ' '.join(title.split()[:5])
        
        if first_words and first_words not in seen_titles:
            seen_titles.add(first_words)
            unique_articles.append(article)
    
    return unique_articles


def generate_reasoning_text(sentiment_counts, overall_sentiment):
    """Generate reasoning text"""
    total = sum(sentiment_counts.values())
    if total == 0:
        return "No articles found"
    
    if overall_sentiment == 'positive':
        return f"Positive sentiment in {sentiment_counts['positive']} out of {total} articles"
    elif overall_sentiment == 'negative':
        return f"Negative sentiment in {sentiment_counts['negative']} out of {total} articles"
    else:
        return f"Mixed sentiment: {sentiment_counts['positive']} positive, {sentiment_counts['negative']} negative, {sentiment_counts['neutral']} neutral"


# =====================================================
# MAIN API FUNCTION (Called from main.py)
# =====================================================

def get_news():
    """Main sentiment analysis endpoint"""
    company_name = request.args.get('company', '').strip()
    if not company_name:
        return jsonify({'error': 'Company name required'}), 400
    
    date_range = request.args.get('date_range', '1d').lower()
    
    print(f"Sentiment analysis for {company_name} (range: {date_range})")
    
    try:
        all_articles = []
        
        if date_range in ['1d', '3d', '1w', '1m']:
            newsapi_articles = get_newsapi_articles(company_name, date_range)
            all_articles.extend(newsapi_articles)
        
        rss_articles = get_rss_articles(company_name)
        all_articles.extend(rss_articles)
        
        unique_articles = remove_duplicates(all_articles)
        
        if not unique_articles:
            unique_articles = create_enhanced_sample_articles(company_name, date_range)
        
        max_articles = 20 if date_range == '1m' else 15
        final_articles = unique_articles[:max_articles]
        
        sentiments = [a['sentiment'] for a in final_articles]
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        overall_sentiment = (
            'positive' if sentiment_counts['positive'] > sentiment_counts['negative']
            else 'negative' if sentiment_counts['negative'] > sentiment_counts['positive']
            else 'neutral'
        )
        
        avg_confidence = sum(a['sentiment_confidence'] for a in final_articles) / len(final_articles) if final_articles else 0.6
        sources_used = list(set(a.get('source', {}).get('name', '') for a in final_articles))
        
        return jsonify({
            'articles': final_articles,
            'totalResults': len(final_articles),
            'summary': {
                'overall_sentiment': overall_sentiment,
                'sentiment_counts': sentiment_counts,
                'average_confidence': round(avg_confidence, 3),
                'company': company_name,
                'date_range': date_range,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'reasoning': generate_reasoning_text(sentiment_counts, overall_sentiment),
                'sources_used': sources_used
            },
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sample_articles = create_enhanced_sample_articles(company_name, date_range)
        
        return jsonify({
            'articles': sample_articles,
            'totalResults': len(sample_articles),
            'summary': {
                'overall_sentiment': 'neutral',
                'sentiment_counts': {'positive': 0, 'negative': 0, 'neutral': 1},
                'average_confidence': 0.65,
                'company': company_name
            },
            'status': 'sample_data'
        }), 200


def health_check():
    """Health check for sentiment module"""
    return jsonify({
        'status': 'healthy',
        'service': 'sentiment-analysis',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })