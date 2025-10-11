// News Simplifier Frontend - For Unified Backend Deployment
// All APIs on same domain/port now!

// Configuration - Single API URL since everything runs together
const API_BASE_URL = window.location.origin;  // Uses current domain

let currentSimplificationLevel = 'basic';
let isSearching = false;
let currentSearchQuery = '';
let currentArticles = [];

// DOM Elements
const elements = {
    newsSearchInput: null,
    customText: null,
    customCharCount: null,
    loadingOverlay: null,
    toastContainer: null,
    newsResults: null,
    articlesContainer: null,
    resultsCount: null,
    customTextResults: null,
    articleModal: null
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 News Simplifier initializing...');
    initializeElements();
    setupEventListeners();
    loadTrendingTopics();
    updateCharCounter();
    console.log('✅ Initialization complete');
});

function initializeElements() {
    elements.newsSearchInput = document.getElementById('newsSearchInput');
    elements.customText = document.getElementById('customText');
    elements.customCharCount = document.getElementById('customCharCount');
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.toastContainer = document.getElementById('toastContainer');
    elements.newsResults = document.getElementById('newsResults');
    elements.articlesContainer = document.getElementById('articlesContainer');
    elements.resultsCount = document.getElementById('resultsCount');
    elements.customTextResults = document.getElementById('customTextResults');
    elements.articleModal = document.getElementById('articleModal');
}

function setupEventListeners() {
    if (elements.newsSearchInput) {
        elements.newsSearchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') searchNews();
        });
    }
    
    if (elements.customText) {
        elements.customText.addEventListener('input', updateCharCounter);
    }
    
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentSimplificationLevel = this.getAttribute('data-level');
        });
    });
}

// Tab Switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    
    const selectedTab = document.getElementById(tabName + 'Tab');
    if (selectedTab) selectedTab.classList.add('active');
    
    event.target.classList.add('active');
}

// Character Counter
function updateCharCounter() {
    if (elements.customText && elements.customCharCount) {
        const count = elements.customText.value.length;
        elements.customCharCount.textContent = count;
        
        if (count > 10000) elements.customCharCount.style.color = 'var(--color-error)';
        else if (count > 9000) elements.customCharCount.style.color = 'var(--color-warning)';
        else elements.customCharCount.style.color = 'var(--color-text-muted)';
    }
}

// Load Trending Topics
async function loadTrendingTopics() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/trending-topics`);
        const data = await response.json();
        
        if (data.trending_topics) {
            const container = document.getElementById('trendingTopics');
            if (container) {
                container.innerHTML = data.trending_topics.map(topic => 
                    `<button class="trending-item" onclick="searchTrendingTopic('${topic}')">${topic}</button>`
                ).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load trending topics:', error);
    }
}

// Search Trending Topic
function searchTrendingTopic(topic) {
    if (elements.newsSearchInput) {
        elements.newsSearchInput.value = topic;
        searchNews();
    }
}

// Main Search Function
async function searchNews() {
    if (isSearching) return;
    
    const query = elements.newsSearchInput.value.trim();
    if (!query) {
        showToast('Please enter a search term', 'error');
        return;
    }
    
    console.log('🔍 Searching for:', query);
    currentSearchQuery = query;
    isSearching = true;
    showLoadingOverlay(true, 'Fetching & Simplifying News...', 'Please wait...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/search-news`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                level: currentSimplificationLevel,
                date_range: '1d'
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        console.log('📰 Received data:', data);
        
        if (data.error) throw new Error(data.error);
        
        currentArticles = data.articles || [];
        displayNewsResults(data);
        showToast(`Found ${data.total_found} articles`, 'success');
        
    } catch (error) {
        console.error('❌ Search error:', error);
        showToast('Failed to fetch news. Please try again.', 'error');
        displayNoResults();
    } finally {
        isSearching = false;
        showLoadingOverlay(false);
    }
}

// Display Results
function displayNewsResults(data) {
    if (!elements.newsResults || !elements.articlesContainer) return;
    
    elements.newsResults.style.display = 'block';
    
    const resultsTitle = document.getElementById('resultsTitle');
    if (resultsTitle) resultsTitle.textContent = `Results for "${currentSearchQuery}"`;
    
    if (elements.resultsCount) {
        elements.resultsCount.textContent = `${data.total_found || 0} articles found`;
    }
    
    elements.articlesContainer.innerHTML = '';
    
    if (!data.articles || data.articles.length === 0) {
        displayNoResults();
        return;
    }
    
    data.articles.forEach((article, index) => {
        const articleElement = createArticleElement(article, index);
        elements.articlesContainer.appendChild(articleElement);
    });
    
    setTimeout(() => {
        elements.newsResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Create Article Card
function createArticleElement(article, index) {
    const div = document.createElement('div');
    div.className = 'article-card';
    
    const complexity = article.analysis?.complexity || 'medium';
    const publishedDate = article.original?.publishedAt ? 
        new Date(article.original.publishedAt).toLocaleDateString() : 'Recently';
    
    div.innerHTML = `
        <div class="article-header">
            <h4 class="article-title">${article.original?.title || 'Untitled'}</h4>
            <div class="article-meta">
                <span class="article-source">${article.original?.source || 'Unknown'}</span>
                <span class="article-date">${publishedDate}</span>
                <span class="complexity-badge ${complexity}">${complexity.toUpperCase()}</span>
            </div>
        </div>
        
        <div class="article-content">
            <div class="article-preview">
                <h5>Simplified Summary:</h5>
                <p>${article.simplified?.summary || article.simplified?.content?.substring(0, 200) + '...' || 'No summary available'}</p>
            </div>
            
            <div class="article-stats">
                <div class="stat">
                    <span class="stat-value">${article.analysis?.jargon_count || 0}</span>
                    <span class="stat-label">Terms Simplified</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${article.analysis?.readability_score || 0}</span>
                    <span class="stat-label">Readability Score</span>
                </div>
            </div>
        </div>
        
        <div class="article-actions">
            <button class="btn-secondary" onclick="openArticleModal(${index})">View Details</button>
            ${article.original?.url ? 
                `<button class="btn-primary" onclick="openOriginalArticle('${article.original.url}')">Read Original</button>` :
                '<button class="btn-primary" disabled>URL Not Available</button>'
            }
        </div>
    `;
    
    return div;
}

// No Results Display
function displayNoResults() {
    if (elements.articlesContainer) {
        elements.articlesContainer.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h3>No Articles Found</h3>
                <p>We couldn't find any recent news for "${currentSearchQuery}".</p>
                <button class="btn-primary" onclick="elements.newsSearchInput.focus()">Try Another Search</button>
            </div>
        `;
    }
}

// Simplify Custom Text
async function simplifyCustomText() {
    const text = elements.customText.value.trim();
    
    if (!text) {
        showToast('Please enter some text to simplify', 'error');
        return;
    }
    
    if (text.length > 10000) {
        showToast('Text too long. Max 10,000 characters.', 'error');
        return;
    }
    
    showLoadingOverlay(true, 'Simplifying Text...', 'Analyzing financial terms...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/simplify-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                level: currentSimplificationLevel
            })
        });
        
        if (!response.ok) throw new Error('Failed to simplify');
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        displayCustomTextResults(data);
        showToast('Text simplified successfully!', 'success');
        
    } catch (error) {
        console.error('Simplification error:', error);
        showToast('Failed to simplify. Please try again.', 'error');
    } finally {
        showLoadingOverlay(false);
    }
}

// Display Custom Text Results
function displayCustomTextResults(data) {
    if (!elements.customTextResults) return;
    
    elements.customTextResults.innerHTML = `
        <div class="results-header">
            <h3>Simplification Results</h3>
            <div class="results-meta">
                <span class="complexity-badge ${data.complexity}">${data.complexity.toUpperCase()}</span>
                <span>Readability: ${data.readability_score}/100</span>
            </div>
        </div>

        <div class="text-comparison">
            <div class="original-text">
                <div class="text-header">
                    <h4>Original Text</h4>
                    <button class="copy-btn" onclick="copyText(\`${data.original_text.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">📋</button>
                </div>
                <div class="text-content">${data.original_text}</div>
            </div>

            <div class="simplified-text">
                <div class="text-header">
                    <h4>Simplified Version</h4>
                    <button class="copy-btn" onclick="copyText(\`${data.simplified_text.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">📋</button>
                </div>
                <div class="text-content">${data.simplified_text}</div>
            </div>
        </div>

        ${data.jargon_detected.length > 0 ? `
        <div class="simplifications-section">
            <h4>Financial Terms Explained (${data.jargon_count})</h4>
            <div class="jargon-explanations">
                ${data.jargon_detected.map(item => `
                    <div class="jargon-item">
                        <div class="jargon-term">${item.term}${item.count > 1 ? ` (${item.count}x)` : ''}</div>
                        <div class="jargon-explanation">${item.explanation}</div>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
    
    elements.customTextResults.style.display = 'block';
    setTimeout(() => {
        elements.customTextResults.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

// Modal Functions
function openArticleModal(index) {
    if (index >= currentArticles.length) return;
    
    const article = currentArticles[index];
    
    document.getElementById('modalTitle').textContent = article.original?.title || 'Untitled';
    document.getElementById('modalSource').textContent = article.original?.source || 'Unknown';
    document.getElementById('modalDate').textContent = article.original?.publishedAt ? 
        new Date(article.original.publishedAt).toLocaleDateString() : 'Recently';
    
    const complexityBadge = document.querySelector('#articleModal .complexity-badge');
    if (complexityBadge) {
        const complexity = article.analysis?.complexity || 'medium';
        complexityBadge.textContent = complexity.toUpperCase();
        complexityBadge.className = `complexity-badge ${complexity}`;
    }
    
    document.getElementById('modalOriginalContent').textContent = 
        article.original?.content || article.original?.description || 'No content available';
    document.getElementById('modalSimplifiedContent').textContent = 
        article.simplified?.content || 'No simplified version available';
    
    document.getElementById('modalJargonCount').textContent = article.analysis?.jargon_count || 0;
    document.getElementById('modalReadabilityScore').textContent = article.analysis?.readability_score || 0;
    
    const jargonContainer = document.getElementById('modalJargonList');
    if (article.analysis?.jargon_detected?.length > 0) {
        jargonContainer.innerHTML = article.analysis.jargon_detected.map(item => `
            <div class="jargon-item">
                <div class="jargon-term">${item.term}${item.count > 1 ? ` (${item.count}x)` : ''}</div>
                <div class="jargon-explanation">${item.explanation}</div>
            </div>
        `).join('');
    } else {
        jargonContainer.innerHTML = '<p>No complex terms detected.</p>';
    }
    
    const insightsContainer = document.getElementById('modalInsights');
    if (article.analysis?.insights?.length > 0) {
        insightsContainer.innerHTML = article.analysis.insights.map(insight => `
            <div class="insight-item">
                <div class="insight-title">${insight.title}</div>
                <div class="insight-description">${insight.description}</div>
            </div>
        `).join('');
    } else {
        insightsContainer.innerHTML = '<p>No insights available.</p>';
    }
    
    if (elements.articleModal) {
        elements.articleModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeArticleModal() {
    if (elements.articleModal) {
        elements.articleModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

function switchModalTab(tabName) {
    document.querySelectorAll('.modal-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.modal-tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    const tabContent = document.getElementById(tabName + 'Tab');
    if (tabContent) tabContent.classList.add('active');
}

function openOriginalArticle(url) {
    if (url && url !== 'null') {
        window.open(url, '_blank');
    } else {
        showToast('Article URL not available', 'info');
    }
}

// Utility Functions
function showLoadingOverlay(show, title = 'Loading...', description = 'Please wait...') {
    if (!elements.loadingOverlay) return;
    
    if (show) {
        document.getElementById('loadingTitle').textContent = title;
        document.getElementById('loadingDescription').textContent = description;
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressText').textContent = '0%';
        elements.loadingOverlay.classList.add('show');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            const fill = document.getElementById('progressFill');
            const text = document.getElementById('progressText');
            if (fill) fill.style.width = `${progress}%`;
            if (text) text.textContent = `${progress}%`;
            if (progress >= 90) clearInterval(interval);
        }, 200);
    } else {
        elements.loadingOverlay.classList.remove('show');
    }
}

function copyText(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyText(text);
        });
    } else {
        fallbackCopyText(text);
    }
}

function fallbackCopyText(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy', 'error');
    }
    
    document.body.removeChild(textArea);
}

function goBackHome() {
    window.location.href = '/';
}

// Toast Notification System
function showToast(message, type = 'info', duration = 4000) {
    if (!elements.toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

console.log('📰 News Simplifier loaded successfully!');