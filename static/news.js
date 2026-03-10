// Lưu trữ danh sách tin tức, giải đấu hiện tại, chế độ xem (list/detail)
let allArticles = [];
let currentLeague = 'all';

// Cấu hình giải đấu: tên, màu sắc, từ khóa để lọc
const LEAGUES = {
    'premier-league': { name: 'Premier League', color: '#38003c', keywords: ['premier', 'liverpool', 'arsenal', 'chelsea', 'man city', 'manchester', 'tottenham', 'united', 'everton', 'newcastle'] },
    'la-liga': { name: 'La Liga', color: '#ee2737', keywords: ['la liga', 'laliga', 'real madrid', 'barcelona', 'atletico', 'sevilla', 'valencia', 'villarreal'] },
    'serie-a': { name: 'Serie A', color: '#024494', keywords: ['serie a', 'juventus', 'inter milan', 'ac milan', 'napoli', 'roma', 'lazio', 'fiorentina'] },
    'bundesliga': { name: 'Bundesliga', color: '#cf0a2c', keywords: ['bundesliga', 'bayern', 'dortmund', 'leverkusen', 'leipzig', 'frankfurt'] },
    'champions-league': { name: 'Champions League', color: '#071c4d', keywords: ['champions league', 'ucl', 'uefa', 'champions'] }
};

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function goHome() {
    showListView();
    filterByLeague('all');
}

function goBack() {
    showListView();
}

// Chuyển giữa chế độ hiển thị: danh sách tin hoặc chi tiết bài viết
function showListView() {
    document.getElementById('news-list-view').style.display = 'block';
    document.getElementById('article-detail-view').style.display = 'none';
    window.scrollTo(0, 0);
}

function showDetailView() {
    document.getElementById('news-list-view').style.display = 'none';
    document.getElementById('article-detail-view').style.display = 'block';
    window.scrollTo(0, 0);
}

function bindTopNavEvents() {
    // Tránh ăn vào navbar của base.html
    document.querySelectorAll('.news-page-wrapper .main-nav .nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            showListView();
            filterByLeague(link.dataset.league);
            document.querySelectorAll('.news-page-wrapper .main-nav .nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

// === LẤY TIN TỨC TỪ SERVER ===
async function loadNews(forceRefresh = false) {
    const loadingState = document.getElementById('loading-state');
    const heroSection = document.getElementById('hero-section');
    const newsSection = document.getElementById('news-section');
    const emptyState = document.getElementById('empty-state');

    loadingState.style.display = 'flex';
    heroSection.style.display = 'none';
    newsSection.style.display = 'none';
    emptyState.style.display = 'none';

    try {
        const url = forceRefresh ? '/api/news?refresh=true' : '/api/news';
        const response = await fetch(url);
        const data = await response.json();
        loadingState.style.display = 'none';

        if (data.success && data.articles && data.articles.length > 0) {
            allArticles = data.articles;
            renderNews(allArticles, currentLeague);
            renderTrending(selectTrendingArticles(allArticles));
        } else {
            emptyState.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error loading news:', error);
        loadingState.style.display = 'none';
        emptyState.style.display = 'flex';
    }
}

// === MỞ CHI TIẾT BÀI VIẾT ===
// Hiển thị layout ngay với skeleton loading, sau đó gọi AI để lấy nội dung tiếng Việt
function openArticle(index) {
    const article = allArticles[index];
    if (!article) return;

    const articleLeague = getArticleLeague(article);
    const leagueInfo = LEAGUES[articleLeague] || { name: 'Football', color: '#1a56db' };
    const articleContent = document.getElementById('article-content');

    articleContent.innerHTML = `
        <div class="article-header">
            <span class="article-badge" style="background: ${leagueInfo.color}">${escapeHtml(leagueInfo.name)}</span>
            <h1 class="article-title">${escapeHtml(article.title)}</h1>
            <div class="article-meta">
                <span class="meta-source">${escapeHtml(article.source?.name || 'FootballNews')}</span>
                <span class="meta-dot">•</span>
                <span class="meta-time">${escapeHtml(article.relativeTime || 'Mới cập nhật')}</span>
                <span class="meta-dot">•</span>
                <span class="meta-readtime">⏱ ${escapeHtml(article.readTime || '3 phút đọc')}</span>
            </div>
        </div>

        <div class="article-image">
            <img src="${article.urlToImage || 'https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200&h=600&fit=crop'}"
                 alt="${escapeHtml(article.title)}"
                 onerror="this.src='https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200&h=600&fit=crop'">
        </div>

        <div class="article-body">
            <p class="article-lead">${escapeHtml(article.description || '')}</p>

            <div id="ai-content-area">
                <div class="ai-loading-badge">
                    <span class="ai-spinner"></span>
                    <span class="ai-loading-text">Đang tạo nội dung...</span>
                </div>
                <div class="skeleton-block">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                </div>
            </div>
        </div>

        <div class="related-section">
            <h3>Tin liên quan</h3>
            <div class="related-grid">
                ${getRelatedArticles(index).map((a) => `
                    <div class="related-card" onclick="openArticle(${allArticles.indexOf(a)})">
                        <img src="${a.urlToImage || 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=200&h=120&fit=crop'}" alt="">
                        <div class="related-info">
                            <h4>${escapeHtml((a.title || '').substring(0, 60))}${(a.title || '').length > 60 ? '...' : ''}</h4>
                            <span>${escapeHtml(a.relativeTime || '')}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    showDetailView();
    loadAIContent(article, leagueInfo);
}

// Gọi API AI và điền nội dung vào #ai-content-area
async function loadAIContent(article, leagueInfo) {
    const aiArea = document.getElementById('ai-content-area');
    if (!aiArea) return;

    // ✅ Nếu bài đã có AI content từ server (đã lưu lần trước) → hiển thị ngay
    if (article.ai_content) {
        const paragraphs = String(article.ai_content)
            .split('\n')
            .filter(p => p.trim().length > 0)
            .map(p => `<p>${escapeHtml(p.trim())}</p>`)
            .join('');
        aiArea.innerHTML = `
            <div class="ai-badge">
                <a href="${article.url}" target="_blank" rel="noopener" class="source-link">Nguồn</a>
            </div>
            <div class="article-text ai-generated">${paragraphs}</div>
        `;
        return;
    }

    const category = article.category || '';
    const mode = String(category).includes('SẮP DIỄN RA') ? 'preview' : 'expand';

    try {
        const response = await fetch('/api/ai/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: article.title,
                description: article.description || article.content || '',
                league: leagueInfo.name,
                mode: mode,
                url: article.url || ''
            })
        });

        const data = await response.json().catch(() => ({}));

        if (data.success && data.content) {
            article.ai_content = data.content;

            const paragraphs = String(data.content)
                .split('\n')
                .filter(p => p.trim().length > 0)
                .map(p => `<p>${escapeHtml(p.trim())}</p>`)
                .join('');

            aiArea.innerHTML = `
                <div class="ai-badge">
                    <a href="${article.url}" target="_blank" rel="noopener" class="source-link">Nguồn</a>
                </div>
                <div class="article-text ai-generated">
                    ${paragraphs}
                </div>
            `;
        } else {
            // Fallback: hiện nội dung gốc từ RSS nếu AI lỗi
            aiArea.innerHTML = `
                <div class="ai-badge ai-badge-warn">AI chưa sẵn sàng</div>
                <div class="article-text">
                    <p>${escapeHtml(article.content || article.description || 'Nội dung đang được cập nhật...')}</p>
                </div>
            `;
        }
    } catch (err) {
        console.error('[AI] Lỗi gọi API:', err);
        aiArea.innerHTML = `
            <div class="ai-badge ai-badge-warn">Không thể kết nối AI</div>
            <div class="article-text">
                <p>${escapeHtml(article.content || article.description || 'Nội dung đang được cập nhật...')}</p>
            </div>
        `;
    }
}

// 4 bài viết liên quan
function getRelatedArticles(currentIndex) {
    return allArticles.filter((_, i) => i !== currentIndex).slice(0, 4);
}

// Lọc tin theo giải đấu (all, premier-league, la-liga, ...)
function filterByLeague(league) {
    currentLeague = league;
    showListView();

    document.querySelectorAll('.news-page-wrapper .league-chip').forEach(chip => {
        chip.classList.toggle('active', chip.dataset.league === league);
    });

    document.querySelectorAll('.news-page-wrapper .main-nav .nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.league === league);
    });

    renderNews(allArticles, league);
}

function getArticleLeague(article) {
    const text = ((article.title || '') + ' ' + (article.description || '')).toLowerCase();
    for (const [leagueId, leagueInfo] of Object.entries(LEAGUES)) {
        if (leagueInfo.keywords.some(kw => text.includes(kw))) {
            return leagueId;
        }
    }
    return 'other';
}

function renderNews(articles, league) {
    const heroSection = document.getElementById('hero-section');
    const newsSection = document.getElementById('news-section');
    const newsGrid = document.getElementById('news-grid');
    const emptyState = document.getElementById('empty-state');

    let filteredArticles = articles;
    if (league !== 'all') {
        filteredArticles = articles.filter(a => getArticleLeague(a) === league);
    }

    if (filteredArticles.length === 0) {
        heroSection.style.display = 'none';
        newsSection.style.display = 'none';
        emptyState.style.display = 'flex';
        return;
    }

    emptyState.style.display = 'none';

    const hero = filteredArticles[0];
    const heroIndex = articles.indexOf(hero);
    const heroLeagueInfo = LEAGUES[getArticleLeague(hero)] || { name: 'Football', color: '#1a56db' };

    heroSection.style.display = 'block';
    heroSection.innerHTML = `
        <div class="hero-card" onclick="openArticle(${heroIndex})">
            <div class="hero-image">
                <img src="${hero.urlToImage || 'https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200&h=600&fit=crop'}" 
                     alt="${escapeHtml(hero.title)}"
                     onerror="this.src='https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200&h=600&fit=crop'">
                <div class="hero-overlay"></div>
            </div>
            <div class="hero-content">
                <span class="hero-badge" style="background: ${heroLeagueInfo.color}">${heroLeagueInfo.name}</span>
                <h1 class="hero-title">${escapeHtml(hero.title)}</h1>
                <p class="hero-excerpt">${escapeHtml(hero.description || '')}</p>
                <div class="hero-meta">
                    <span class="meta-source">${escapeHtml(hero.source?.name || 'FootballNews')}</span>
                    <span class="meta-dot">•</span>
                    <span class="meta-time">${escapeHtml(hero.relativeTime || 'Mới cập nhật')}</span>
                </div>
            </div>
        </div>
    `;

    const gridArticles = filteredArticles.slice(1, 17);
    newsSection.style.display = 'block';

    newsGrid.innerHTML = gridArticles.map(article => {
        const articleIndex = articles.indexOf(article);
        const leagueInfo = LEAGUES[getArticleLeague(article)] || { name: 'Football', color: '#1a56db' };
        return `
            <article class="news-card" onclick="openArticle(${articleIndex})">
                <div class="card-image">
                    <img src="${article.urlToImage || 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=400&h=250&fit=crop'}" 
                         alt="${escapeHtml(article.title)}"
                         onerror="this.src='https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=400&h=250&fit=crop'">
                    <div class="card-overlay"></div>
                    <span class="card-badge" style="background: ${leagueInfo.color}">${leagueInfo.name}</span>
                </div>
                <div class="card-content">
                    <h3 class="card-title">${escapeHtml(article.title)}</h3>
                    <div class="card-meta">
                        <span>${escapeHtml(article.source?.name || 'News')}</span>
                        <span>•</span>
                        <span>${escapeHtml(article.relativeTime || '')}</span>
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

// Hiển thị danh sách trending ở sidebar
function renderTrending(articles) {
    document.getElementById('trending-list').innerHTML = articles.map(article => `
        <div class="trending-item" onclick="openArticle(${allArticles.indexOf(article)})">
            <img class="trending-thumb" src="${article.urlToImage || 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=100&h=70&fit=crop'}"
                alt="${escapeHtml(article.title)}"
                onerror="this.src='https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=100&h=70&fit=crop'">
                <div class="trending-content">
                    <p class="trending-title">${escapeHtml((article.title || '').substring(0, 60))}${(article.title || '').length > 60 ? '...' : ''}</p>
                    <span class="trending-time">${escapeHtml(article.relativeTime || '')}</span>
                </div>
            </div>
    `).join('');
}

// === TÌM KIẾM — DROPDOWN ===
function positionDropdown() {
    const input = document.getElementById('search-input');
    const dropdown = document.getElementById('search-dropdown');
    if (!input || !dropdown) return;
    const rect = input.getBoundingClientRect();
    dropdown.style.top = (rect.bottom + 8) + 'px';
    dropdown.style.left = (rect.right - 360) + 'px';
}

function searchNews(query) {
    const dropdown = document.getElementById('search-dropdown');
    const q = query.trim().toLowerCase();

    if (!q) {
        closeSearchDropdown();
        return;
    }

    const results = allArticles.filter(a => {
        const text = ((a.title || '') + ' ' + (a.description || '')).toLowerCase();
        return text.includes(q);
    }).slice(0, 10);

    if (results.length === 0) {
        dropdown.innerHTML = `<div class="search-drop-empty">Không tìm thấy kết quả cho "<b>${escapeHtml(query)}</b>"</div>`;
    } else {
        dropdown.innerHTML =
            `<div class="search-drop-header">🔍 ${results.length} kết quả cho "${escapeHtml(query)}"</div>` +
            results.map(article => {
                const idx = allArticles.indexOf(article);
                const thumb = article.urlToImage || 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=120&h=80&fit=crop';
                const league = LEAGUES[getArticleLeague(article)]?.name || 'Football';
                return `
                    <div class="search-drop-item" onclick="openFromSearch(${idx})">
                        <img class="search-drop-thumb" src="${thumb}"
                             onerror="this.src='https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=120&h=80&fit=crop'"
                             alt="">
                        <div class="search-drop-info">
                            <div class="search-drop-title">${escapeHtml(article.title)}</div>
                            <div class="search-drop-meta">${escapeHtml(league)} · ${escapeHtml(article.relativeTime || '')}</div>
                        </div>
                    </div>`;
            }).join('');
    }

    positionDropdown();
    dropdown.style.display = 'block';
}

function openFromSearch(index) {
    closeSearchDropdown();
    const input = document.getElementById('search-input');
    if (input) input.value = '';
    openArticle(index);
}

function closeSearchDropdown() {
    const dropdown = document.getElementById('search-dropdown');
    if (dropdown) dropdown.style.display = 'none';
}

function handleSearchKey(event) {
    if (event.key === 'Escape') clearSearch();
}

function clearSearch() {
    const input = document.getElementById('search-input');
    if (input) { input.value = ''; input.focus(); }
    closeSearchDropdown();
}

document.addEventListener('click', function (e) {
    const box = document.querySelector('.news-page-wrapper .search-box');
    if (box && !box.contains(e.target)) {
        closeSearchDropdown();
    }
});

// === KHỞI TẠO ===
document.addEventListener('DOMContentLoaded', function () {
    bindTopNavEvents();
    loadNews();
});

function selectTrendingArticles(articles) {
    const trending = [];
    const getArticlesByLeague = (leagueId, count) => {
        const leagueArticles = articles.filter(a => getArticleLeague(a) === leagueId);
        return leagueArticles.slice(0, count);
    };
    trending.push(...getArticlesByLeague('premier-league', 2));
    trending.push(...getArticlesByLeague('la-liga', 1));
    trending.push(...getArticlesByLeague('serie-a', 1));
    trending.push(...getArticlesByLeague('bundesliga', 1));
    trending.push(...getArticlesByLeague('champions-league', 1));
    while (trending.length < 6 && trending.length < articles.length) {
        const nextArticle = articles.find(a => !trending.includes(a));
        if (nextArticle) trending.push(nextArticle);
        else break;
    }
    return trending;
}
