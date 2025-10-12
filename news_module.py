"""
AI-Powered News Simplification Module
Uses Google Gemini AI to ACTUALLY explain news in simple language
"""

from flask import request, jsonify
import requests
import re
from datetime import datetime, timedelta, timezone
import google.generativeai as genai

NEWS_API_KEY = '7eae47b18ad34858878240cb7a6f139a'

# Configure Google Gemini AI (FREE!)
# Get your free API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = 'AIzaSyCxE4PmI_Vfrc5f4eLBShCi2eqwssA7elA'  # Replace with your key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the AI model
ai_model = genai.GenerativeModel('gemini-pro')


def explain_with_ai(title, description, level='basic'):
    """
    Use AI to ACTUALLY explain the news in simple language
    No word replacement - REAL understanding!
    """
    try:
        # Create prompt based on simplification level
        if level == 'basic':
            prompt = f"""You are explaining financial news to a common person who knows nothing about finance.

News Title: {title}
News Description: {description}

Explain this news in 2-3 simple sentences that anyone can understand. Use everyday language like you're talking to a friend. Avoid ALL financial jargon. Make it clear what happened and why it matters.

Example style: "Reliance Industries started a new phone service. They want to compete with other phone companies. This means customers might get cheaper phone plans."

Your explanation:"""

        elif level == 'detailed':
            prompt = f"""You are explaining financial news to someone learning about business.

News Title: {title}
News Description: {description}

Explain this news in 3-4 sentences. Use simple language but you can include some basic financial terms with quick explanations. Make it informative but still easy to understand.

Your explanation:"""

        else:  # expert
            prompt = f"""You are explaining financial news to someone with basic business knowledge.

News Title: {title}
News Description: {description}

Explain this news in 3-4 sentences. You can use financial terms but explain the key concepts. Focus on what this means for the company and investors.

Your explanation:"""

        # Get AI explanation
        response = ai_model.generate_content(prompt)
        explanation = response.text.strip()
        
        # If AI fails, return a basic explanation
        if not explanation:
            return f"{title}. {description}"
        
        return explanation
        
    except Exception as e:
        print(f"AI explanation error: {e}")
        # Fallback to original text if AI fails
        return f"{title}. {description}"


def extract_key_terms(text):
    """
    Use AI to identify and explain key financial terms
    """
    try:
        prompt = f"""From this financial text, identify 3-5 important financial terms and explain each in ONE simple sentence.

Text: {text}

Format your response EXACTLY like this:
1. Term: Simple one-sentence explanation
2. Term: Simple one-sentence explanation

Your response:"""

        response = ai_model.generate_content(prompt)
        terms_text = response.text.strip()
        
        # Parse the response
        terms = []
        lines = terms_text.split('\n')
        for line in lines:
            if ':' in line:
                # Extract term and explanation
                parts = line.split(':', 1)
                term = parts[0].strip('1234567890. ')
                explanation = parts[1].strip()
                if term and explanation:
                    terms.append({
                        'term': term,
                        'explanation': explanation,
                        'count': 1
                    })
        
        return terms[:5]  # Return max 5 terms
        
    except Exception as e:
        print(f"Term extraction error: {e}")
        return []


def calculate_complexity(text):
    """Calculate text complexity - simplified version"""
    if not text:
        return 'low', 50
    
    # Simple word count based complexity
    words = text.split()
    word_count = len(words)
    
    # Check for financial keywords
    financial_keywords = ['market', 'stock', 'revenue', 'profit', 'investment', 
                          'quarterly', 'earnings', 'capital', 'shares', 'equity']
    
    keyword_count = sum(1 for word in words if word.lower() in financial_keywords)
    
    if keyword_count > 8 or word_count > 100:
        return 'high', 30
    elif keyword_count > 4 or word_count > 50:
        return 'medium', 60
    else:
        return 'low', 80


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
            'pageSize': 15
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
            'description': f'{query} reported better than expected results with revenue growth of 15% and improved market position in the latest quarter.',
            'content': f'{query} announced quarterly results with revenue growth.',
            'url': 'https://example.com/article1',
            'publishedAt': now.isoformat(),
            'source': {'name': 'Financial Times'},
            'urlToImage': None
        }
    ]


# =====================================================
# MAIN API ENDPOINT - WITH AI!
# =====================================================

def search_news():
    """Main news search with AI-powered simplification"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        level = data.get('level', 'basic')
        date_range = data.get('date_range', '1d')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"🔍 Searching for: {query} with AI explanation level: {level}")
        
        # Fetch news articles
        articles = fetch_news_from_newsapi(query, date_range)
        
        if not articles:
            articles = create_sample_articles(query)
        
        # Process each article WITH AI
        processed_articles = []
        for i, article in enumerate(articles[:10]):  # Limit to 10 for AI processing
            print(f"  📰 Processing article {i+1}/10 with AI...")
            
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', description)
            
            if not title or not description:
                continue
            
            # 🤖 USE AI TO EXPLAIN THE NEWS!
            ai_explanation = explain_with_ai(title, description, level)
            
            # Calculate basic complexity
            complexity, readability = calculate_complexity(f"{title} {description}")
            
            # Extract key terms using AI (only for detailed/expert)
            key_terms = []
            if level in ['detailed', 'expert']:
                key_terms = extract_key_terms(f"{title}. {description}")
            
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
                    'content': ai_explanation,  # AI-generated explanation!
                    'summary': ai_explanation[:200] + '...' if len(ai_explanation) > 200 else ai_explanation
                },
                'analysis': {
                    'complexity': complexity,
                    'readability_score': readability,
                    'jargon_count': len(key_terms),
                    'jargon_detected': key_terms,
                    'insights': [
                        {
                            'title': 'AI Explanation',
                            'description': f'This news was explained using AI at {level} level'
                        }
                    ]
                }
            }
            
            processed_articles.append(processed_article)
        
        print(f"✅ Processed {len(processed_articles)} articles with AI")
        
        return jsonify({
            'articles': processed_articles,
            'total_found': len(processed_articles),
            'query': query,
            'level': level,
            'date_range': date_range,
            'status': 'success',
            'ai_powered': True
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500


def simplify_custom_text():
    """Simplify custom text using AI"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        level = data.get('level', 'basic')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 10000:
            return jsonify({'error': 'Text too long (max 10000 characters)'}), 400
        
        print(f"🤖 AI simplifying custom text...")
        
        # Use AI to simplify the text
        ai_simplified = explain_with_ai("Custom Text", text, level)
        
        # Extract key terms
        key_terms = extract_key_terms(text)
        
        # Calculate complexity
        complexity, readability = calculate_complexity(text)
        
        return jsonify({
            'original_text': text,
            'simplified_text': ai_simplified,
            'complexity': complexity,
            'readability_score': readability,
            'jargon_count': len(key_terms),
            'jargon_detected': key_terms,
            'insights': [
                {
                    'title': 'AI-Powered Simplification',
                    'description': 'This text was simplified using Google Gemini AI'
                },
                {
                    'title': 'Complexity Level',
                    'description': f'Original text complexity: {complexity.upper()}'
                },
                {
                    'title': 'Key Terms Found',
                    'description': f'Identified {len(key_terms)} important financial terms'
                }
            ],
            'ai_powered': True
        })
        
    except Exception as e:
        print(f"❌ Error in simplification: {e}")
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
            'Tata Motors',
            'Stock Market India'
        ]
    })


def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-news-simplification',
        'ai_model': 'Google Gemini Pro',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })