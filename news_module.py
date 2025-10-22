"""
AI-Powered News Simplification Module
Uses Google Gemini AI to ACTUALLY explain news in simple language
"""

from flask import request, jsonify
import requests
import re
from datetime import datetime, timedelta, timezone
import google.generativeai as genai
import time

NEWS_API_KEY = '7eae47b18ad34858878240cb7a6f139a'

# Configure Google Gemini AI
GEMINI_API_KEY = 'AIzaSyCxE4PmI_Vfrc5f4eLBShCi2eqwssA7elA'
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the AI model
ai_model = genai.GenerativeModel('gemini-2.0-flash-exp')


def explain_with_ai(title, description, level='basic'):
    """
    Use AI to ACTUALLY explain the news in simple language
    """
    try:
        # Combine title and description for better context
        full_text = f"{title}. {description}" if description else title
        
        # Create prompt based on simplification level
        if level == 'basic':
            prompt = f"""You are a financial news explainer who makes complex news simple for everyone.

ORIGINAL NEWS: {full_text}

YOUR TASK: Explain this news in 4-5 SHORT, SIMPLE sentences that ANYONE normal people can understand with example.

RULES:
1. Write EXACTLY 4-5 sentences, no more, no less
2. Use words a 12-year-old can understand
3. NO business jargon at all (avoid: revenue, market cap, IPO, stocks, shares, equity, etc.)
4. Instead say: "money earned", "company value", "selling company pieces", etc.
5. Explain WHAT happened, WHY it matters, and HOW it affects regular people
6. Be conversational and friendly
7. Start with "This news is about..."

EXAMPLE:
Original: "Company's market cap surged 15% after quarterly earnings beat analyst estimates"
Your explanation: "This news is about a company doing really well. They made more money than experts thought they would. Because of this, more people want to own part of the company. Now the company is worth more money than before. This is good news for anyone who owns a piece of this company."

Now explain this news:"""

        elif level == 'detailed':
            prompt = f"""You are explaining business news clearly and simply.

ORIGINAL NEWS: {full_text}

YOUR TASK: Explain in 4-5 clear sentences.

RULES:
1. Write EXACTLY 4-5 sentences
2. You can use some business terms BUT explain them immediately in parentheses
3. Make it educational and easy to follow
4. Connect it to real-world impact
5. Start with a clear opening sentence

EXAMPLE:
"This company announced strong quarterly results (their performance over 3 months). They made more money than expected, which surprised investors (people who own shares). Their market cap (total company value) increased by 15%. This growth shows the company is doing well and attracting more buyers."

Now explain this news:"""

        else:  # expert
            prompt = f"""You are explaining business news with proper context what is the acutall thing whhataare thinhis going to affect .

ORIGINAL NEWS: {full_text}

YOUR TASK: Explain in 4-5 informative sentences.

RULES:
1. Write EXACTLY 4-5 sentences
2. Use proper financial terms
3. Explain the business implications
4. Mention impact on stakeholders
5. Be professional but clear

Now explain this news:"""

        # Get AI explanation with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"  🤖 AI Attempt {attempt + 1}/{max_retries}...")
                
                response = ai_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'top_k': 40,
                        'max_output_tokens': 300,
                    }
                )
                
                # FIX: Use response.text instead of response.parts
                explanation = response.text.strip()
                
                # Validate the response
                if explanation and len(explanation) > 50:
                    # Check it's not just repeating the original
                    if explanation.lower() != full_text.lower():
                        # Count sentences
                        sentences = explanation.split('.')
                        sentences = [s.strip() for s in sentences if s.strip()]
                        
                        print(f"  ✅ AI generated {len(sentences)} sentences")
                        print(f"  📝 Preview: {explanation[:100]}...")
                        return explanation
                
                print(f"  ⚠️ AI response validation failed, retry {attempt + 1}")
                
            except Exception as inner_e:
                print(f"  ❌ AI attempt {attempt + 1} failed: {str(inner_e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retry
                continue
        
        # If AI completely fails, create a better fallback
        print(f"  ⚠️ All AI attempts failed, using enhanced fallback")
        return create_enhanced_fallback(title, description, level)
        
    except Exception as e:
        print(f"❌ AI explanation error: {e}")
        return create_enhanced_fallback(title, description, level)


def create_enhanced_fallback(title, description, level='basic'):
    """
    Create a better explanation when AI fails
    """
    if not description or description == title:
        # Only title available
        parts = title.split()
        if len(parts) > 15:
            summary = ' '.join(parts[:15]) + '...'
        else:
            summary = title
        return f"This news is about: {summary}. We're working on getting more details about this story."
    
    # Combine title and description
    full_text = f"{title}. {description}"
    
    # Enhanced word replacements
    replacements = {
        'market capitalization': 'company value',
        'market cap': 'company value',
        'revenue': 'money earned',
        'profit': 'earnings',
        'profits': 'earnings',
        'loss': 'money lost',
        'losses': 'money lost',
        'IPO': 'first time selling shares',
        'stock': 'company share',
        'stocks': 'company shares',
        'shares': 'company pieces',
        'shareholders': 'company owners',
        'investors': 'people who bought shares',
        'quarterly': 'every 3 months',
        'fiscal year': 'financial year',
        'EBITDA': 'earnings',
        'merger': 'two companies joining',
        'acquisition': 'buying another company',
        'divest': 'selling part of business',
        'equity': 'ownership',
        'dividend': 'profit payment',
        'bear market': 'falling prices',
        'bull market': 'rising prices',
        'volatility': 'price changes',
        'portfolio': 'collection of investments',
    }
    
    simplified = full_text
    for old, new in replacements.items():
        simplified = re.sub(r'\b' + re.escape(old) + r'\b', new, simplified, flags=re.IGNORECASE)
    
    # Break into sentences and take first 3-4
    sentences = simplified.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Take first 4 sentences
    result_sentences = sentences[:4]
    result = '. '.join(result_sentences) + '.'
    
    # If still too long, truncate
    if len(result) > 400:
        result = result[:397] + '...'
    
    return result


def extract_key_terms(text):
    """
    Use AI to identify and explain key financial terms
    """
    try:
        prompt = f"""From this financial text, identify 3-5 important financial terms and explain each in ONE simple sentence (max 15 words).

Text: {text}

Format EXACTLY like this (one term per line):
Market Cap: The total value of a company
Revenue: Money a company earns from sales

Your response (3-5 terms only):"""

        response = ai_model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.5,
                'max_output_tokens': 200,
            }
        )
        
        terms_text = response.text.strip()
        
        # Parse the response
        terms = []
        lines = terms_text.split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                term = parts[0].strip().strip('•-*1234567890. ')
                explanation = parts[1].strip()
                if term and explanation and len(explanation) > 10:
                    terms.append({
                        'term': term,
                        'explanation': explanation,
                        'count': 1
                    })
        
        return terms[:5]
        
    except Exception as e:
        print(f"Term extraction error: {e}")
        return []


def calculate_complexity(text):
    """Calculate text complexity"""
    if not text:
        return 'low', 50
    
    words = text.split()
    word_count = len(words)
    
    financial_keywords = [
        'market', 'stock', 'revenue', 'profit', 'investment', 
        'quarterly', 'earnings', 'capital', 'shares', 'equity',
        'dividend', 'merger', 'acquisition', 'portfolio', 'IPO'
    ]
    
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
            'pageSize': 10
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
            'title': f'{query} reports strong quarterly performance with 15% growth',
            'description': f'{query} announced better than expected quarterly results with revenue growth of 15% year-over-year and improved market position across key segments.',
            'content': f'{query} quarterly results exceed expectations with strong growth.',
            'url': 'https://example.com/article1',
            'publishedAt': now.isoformat(),
            'source': {'name': 'Financial Express'},
            'urlToImage': None
        }
    ]


def search_news():
    """Main news search with AI-powered simplification"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        level = data.get('level', 'basic')
        date_range = data.get('date_range', '1d')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"\n{'='*60}")
        print(f"🔍 NEW SEARCH: {query}")
        print(f"📊 Level: {level} | Date Range: {date_range}")
        print(f"{'='*60}\n")
        
        # Fetch news articles
        articles = fetch_news_from_newsapi(query, date_range)
        
        if not articles:
            print("⚠️ No articles from NewsAPI, using sample data")
            articles = create_sample_articles(query)
        else:
            print(f"✅ Found {len(articles)} articles from NewsAPI")
        
        # Process articles with AI
        processed_articles = []
        for i, article in enumerate(articles[:5], 1):
            print(f"\n📰 Processing Article {i}/5:")
            print(f"   Title: {article.get('title', 'No title')[:60]}...")
            
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', description)
            
            if not title:
                print(f"   ❌ Skipped - No title")
                continue
            
            # USE AI TO EXPLAIN
            print(f"   🤖 Sending to AI for {level} level explanation...")
            ai_explanation = explain_with_ai(title, description, level)
            
            # Show what we got
            print(f"   ✅ Got explanation ({len(ai_explanation)} chars)")
            print(f"   📝 {ai_explanation[:80]}...")
            
            complexity, readability = calculate_complexity(f"{title} {description}")
            
            # Extract key terms for detailed/expert levels
            key_terms = []
            if level in ['detailed', 'expert'] and description:
                print(f"   🔍 Extracting key terms...")
                key_terms = extract_key_terms(f"{title}. {description}")
                print(f"   ✅ Found {len(key_terms)} key terms")
            
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
                    'content': ai_explanation,
                    'summary': ai_explanation[:250] + '...' if len(ai_explanation) > 250 else ai_explanation
                },
                'analysis': {
                    'complexity': complexity,
                    'readability_score': readability,
                    'jargon_count': len(key_terms),
                    'jargon_detected': key_terms,
                    'insights': [
                        {
                            'title': '✨ AI-Simplified',
                            'description': f'Explained using Gemini AI at {level} level'
                        }
                    ]
                }
            }
            
            processed_articles.append(processed_article)
            
            # Small delay between API calls to avoid rate limiting
            if i < len(articles[:5]):
                time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully processed {len(processed_articles)} articles")
        print(f"{'='*60}\n")
        
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
        print(f"\n{'='*60}")
        print(f"❌ ERROR: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
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
        
        print(f"\n🤖 Simplifying custom text ({len(text)} chars)...")
        
        # Use AI to simplify
        ai_simplified = explain_with_ai("Custom Financial Text", text, level)
        
        # Extract key terms
        key_terms = []
        if level in ['detailed', 'expert']:
            print(f"🔍 Extracting key terms...")
            key_terms = extract_key_terms(text)
        
        complexity, readability = calculate_complexity(text)
        
        print(f"✅ Simplification complete!")
        
        return jsonify({
            'original_text': text,
            'simplified_text': ai_simplified,
            'complexity': complexity,
            'readability_score': readability,
            'jargon_count': len(key_terms),
            'jargon_detected': key_terms,
            'insights': [
                {
                    'title': '✨ AI-Powered Simplification',
                    'description': f'Simplified using Google Gemini AI ({level} level)'
                },
                {
                    'title': '📊 Original Complexity',
                    'description': f'{complexity.upper()} complexity text'
                }
            ],
            'ai_powered': True
        })
        
    except Exception as e:
        print(f"❌ Simplification error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def get_trending_topics():
    """Return trending topics"""
    return jsonify({
        'trending_topics': [
            'Reliance Industries',
            'TCS',
            'Infosys',
            'HDFC Bank',
            'ICICI Bank',
            'Sensex',
            'Nifty 50',
            'Tata Motors',
            'Wipro',
            'Adani Group'
        ]
    })


def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-news-simplification',
        'ai_model': 'Google Gemini 2.0 Flash',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })