// Super Simple News App - For Everyone to Understand
// No complex scoring, just simple explanations!

const API_BASE_URL = window.location.origin;
let currentSimplificationLevel = 'basic';
let currentArticles = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading simple news...');
    setupSimpleListeners();
    updateCharCounter();
});

function setupSimpleListeners() {
    // Search on Enter key
    const searchInput = document.getElementById('newsSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') searchNews();
        });
    }
    
    // Character counter for text simplifier
    const customText = document.getElementById('customText');
    if (customText) {
        customText.addEventListener('input', updateCharCounter);
    }
    
    // Simplification level buttons
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
    const customText = document.getElementById('customText');
    const charCount = document.getElementById('customCharCount');
    if (customText && charCount) {
        const count = customText.value.length;
        charCount.textContent = count;
        charCount.style.color = count > 9000 ? '#ef4444' : 'rgba(255,255,255,0.5)';
    }
}

// Search Trending Topic
function searchTrendingTopic(topic) {
    const searchInput = document.getElementById('newsSearchInput');
    if (searchInput) {
        searchInput.value = topic;
        searchNews();
    }
}

// Main Search Function - SIMPLIFIED
async function searchNews() {
    const searchInput = document.getElementById('newsSearchInput');
    const query = searchInput?.value.trim();
    
    if (!query) {
        showSimpleToast('Please type something to search', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/search-news`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                level: currentSimplificationLevel
            })
        });
        
        if (!response.ok) throw new Error('Failed to get news');
        
        const data = await response.json();
        currentArticles = data.articles || [];
        
        displaySimpleResults(data, query);
        showSimpleToast(`Found ${data.total_found} news articles`,'success');
        
    } catch (error) {
        console.error(error);
        showSimpleToast('Could not get news. Please try again', 'error');
    } finally {
        showLoading(false);
    }
}

// Display Results - SUPER SIMPLE
function displaySimpleResults(data, query) {
    const container = document.getElementById('articlesContainer');
    const resultsSection = document.getElementById('newsResults');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!container) return;
    
    resultsSection.style.display = 'block';
    resultsTitle.textContent = `News about "${query}"`;
    resultsCount.textContent = `${data.total_found} articles`;
    
    container.innerHTML = '';
    
    if (!data.articles || data.articles.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h3>No News Found</h3>
                <p>Try searching for something else</p>
            </div>
        `;
        return;
    }
    
    // Create simple cards
    data.articles.forEach((article, index) => {
        const card = createSimpleCard(article, index);
        container.appendChild(card);
    });
    
    setTimeout(() => resultsSection.scrollIntoView({ behavior: 'smooth' }), 100);
}

// Create Simple Card - NO SCORES, JUST SIMPLE TEXT
function createSimpleCard(article, index) {
    const div = document.createElement('div');
    div.className = 'simple-article-card';
    
    const title = article.original?.title || 'No title';
    const source = article.original?.source || 'Unknown source';
    const date = article.original?.publishedAt ? 
        new Date(article.original.publishedAt).toLocaleDateString() : 'Recently';
    const simplified = article.simplified?.summary || article.simplified?.content || 'No summary';
    const url = article.original?.url;
    
    div.innerHTML = `
        <div class="simple-card-header">
            <h3 class="simple-title">${title}</h3>
            <div class="simple-meta">
                <span>${source}</span> • <span>${date}</span>
            </div>
        </div>
        
        <div class="simple-explanation">
            <h4>📝 In Simple Words:</h4>
            <p>${simplified}</p>
        </div>
        
        <div class="simple-actions">
            <button class="btn-simple-details" onclick="openSimpleModal(${index})">
                Read Full Explanation
            </button>
            ${url ? `<button class="btn-simple-original" onclick="window.open('${url}', '_blank')">
                Read Original Article
            </button>` : ''}
        </div>
    `;
    
    return div;
}

// Simple Modal - ONLY TITLE AND SIMPLE EXPLANATION
function openSimpleModal(index) {
    if (index >= currentArticles.length) return;
    
    const article = currentArticles[index];
    const modal = document.getElementById('simpleModal');
    
    document.getElementById('simpleModalTitle').textContent = article.original?.title || 'News';
    document.getElementById('simpleModalSource').textContent = article.original?.source || 'Unknown';
    document.getElementById('simpleModalDate').textContent = article.original?.publishedAt ? 
        new Date(article.original.publishedAt).toLocaleDateString() : 'Recently';
    
    // Full simplified explanation
    document.getElementById('simpleModalExplanation').textContent = 
        article.simplified?.content || article.simplified?.summary || 'No explanation available';
    
    // Set up original button
    const originalBtn = document.getElementById('simpleModalOriginalBtn');
    if (article.original?.url) {
        originalBtn.onclick = () => window.open(article.original.url, '_blank');
        originalBtn.style.display = 'inline-block';
    } else {
        originalBtn.style.display = 'none';
    }
    
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeSimpleModal() {
    const modal = document.getElementById('simpleModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

// Simplify Custom Text
async function simplifyCustomText() {
    const textArea = document.getElementById('customText');
    const text = textArea?.value.trim();
    
    if (!text) {
        showSimpleToast('Please paste some text first', 'error');
        return;
    }
    
    if (text.length > 10000) {
        showSimpleToast('Text is too long. Please use less than 10,000 characters', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/simplify-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                level: currentSimplificationLevel
            })
        });
        
        if (!response.ok) throw new Error('Failed');
        
        const data = await response.json();
        displaySimpleTextResults(data);
        showSimpleToast('Text simplified!', 'success');
        
    } catch (error) {
        console.error(error);
        showSimpleToast('Could not simplify. Try again', 'error');
    } finally {
        showLoading(false);
    }
}

// Display Simple Text Results - CLEAN AND SIMPLE
function displaySimpleTextResults(data) {
    const results = document.getElementById('customTextResults');
    if (!results) return;
    
    results.innerHTML = `
        <div class="simple-text-result">
            <h3>✨ Simplified Version:</h3>
            <div class="simple-text-box">
                <p>${data.simplified_text}</p>
                <button class="copy-btn-simple" onclick="copySimpleText(\`${data.simplified_text.replace(/`/g, '\\`')}\`)">
                    📋 Copy
                </button>
            </div>
            
            ${data.jargon_detected && data.jargon_detected.length > 0 ? `
                <h4>📚 Words We Made Simple:</h4>
                <div class="simple-words-list">
                    ${data.jargon_detected.slice(0, 8).map(item => `
                        <div class="simple-word-item">
                            <strong>${item.term}</strong> = ${item.explanation}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
    
    results.style.display = 'block';
    setTimeout(() => results.scrollIntoView({ behavior: 'smooth' }), 100);
}

// Copy Text Function
function copySimpleText(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSimpleToast('Copied!', 'success');
        }).catch(() => {
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showSimpleToast('Copied!', 'success');
}

// Simple Loading Indicator
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.toggle('show', show);
    }
}

// Simple Toast Notifications
function showSimpleToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `simple-toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span>${icons[type]} ${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 3000);
}

function goBackHome() {
    window.location.href = '/';
}

console.log('✅ Simple news app ready!');