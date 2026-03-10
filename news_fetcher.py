"""
RSS Football News Fetcher - integrated with Football Score Prediction app.
Reads RSS_NEWS_URLS from config or env. Uses in-memory cache.
"""
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Optional

try:
    from config import RSS_NEWS_URLS as RSS_FEED_URLS_STR
except ImportError:
    RSS_FEED_URLS_STR = os.environ.get('RSS_NEWS_URLS', '')

RSS_FEED_URLS = [url.strip() for url in RSS_FEED_URLS_STR.split(',') if url.strip()]

try:
    import requests
except ImportError:
    requests = None

NEWS_CATEGORIES = {
    'MATCH_RESULT': 'KẾT QUẢ TRẬN ĐẤU',
    'UPCOMING_MATCH': 'TRẬN SẮP DIỄN RA',
    'HOT_NEWS': 'TIN NÓNG BÓNG ĐÁ'
}

TARGET_LEAGUES = {
    'champions-league': {
        'name': 'Champions League',
        'display_name': 'UEFA Champions League',
        'keywords': ['champions league', 'ucl', 'uefa champions', 'c1'],
        'football_data_id': 'CL',
        'api_football_id': 2,
        'priority': 1
    },
    'premier-league': {
        'name': 'Premier League',
        'display_name': 'English Premier League',
        'keywords': ['premier league', 'epl', 'english premier', 'ngoại hạng anh'],
        'football_data_id': 'PL',
        'api_football_id': 39,
        'priority': 2
    },
    'la-liga': {
        'name': 'La Liga',
        'display_name': 'Spanish La Liga',
        'keywords': ['la liga', 'laliga', 'spanish league', 'tây ban nha'],
        'football_data_id': 'PD',
        'api_football_id': 140,
        'priority': 3
    },
    'serie-a': {
        'name': 'Serie A',
        'display_name': 'Italian Serie A',
        'keywords': ['serie a', 'italian league', 'calcio', 'ý'],
        'football_data_id': 'SA',
        'api_football_id': 135,
        'priority': 4
    },
    'bundesliga': {
        'name': 'Bundesliga',
        'display_name': 'German Bundesliga',
        'keywords': ['bundesliga', 'german league', 'đức'],
        'football_data_id': 'BL1',
        'api_football_id': 78,
        'priority': 5
    },
    'euro': {
        'name': 'Euro',
        'display_name': 'UEFA European Championship',
        'keywords': ['euro 2024', 'euro 2025', 'euro 2026', 'european championship', 'uefa euro'],
        'football_data_id': 'EC',
        'api_football_id': 4,
        'priority': 6
    },
    'copa-america': {
        'name': 'Copa America',
        'display_name': 'Copa América',
        'keywords': ['copa america', 'copa américa', 'conmebol', 'nam mỹ'],
        'football_data_id': None,
        'api_football_id': 9,
        'priority': 7
    }
}
LEAGUE_CLUBS = {
    'champions-league': [
        'real madrid', 'barcelona', 'bayern munich', 'manchester city',
        'paris saint-germain', 'psg', 'liverpool', 'chelsea', 'arsenal',
        'manchester united', 'juventus', 'inter milan', 'ac milan',
        'borussia dortmund', 'atletico madrid', 'tottenham', 'napoli'
    ],
    'premier-league': [
        'manchester city', 'man city', 'arsenal', 'liverpool', 'chelsea',
        'manchester united', 'man united', 'tottenham', 'newcastle',
        'brighton', 'aston villa', 'west ham', 'crystal palace',
        'brentford', 'fulham', 'everton', 'wolves', 'bournemouth'
    ],
    'la-liga': [
        'real madrid', 'barcelona', 'atletico madrid', 'atletico',
        'sevilla', 'real sociedad', 'real betis', 'villarreal',
        'athletic bilbao', 'valencia', 'getafe', 'girona'
    ],
    'serie-a': [
        'inter milan', 'juventus', 'ac milan', 'napoli', 'roma',
        'lazio', 'atalanta', 'fiorentina', 'bologna', 'torino'
    ],
    'bundesliga': [
        'bayern munich', 'bayern', 'borussia dortmund', 'dortmund',
        'bayer leverkusen', 'leverkusen', 'rb leipzig', 'leipzig',
        'union berlin', 'eintracht frankfurt', 'frankfurt',
        'wolfsburg', 'vfl wolfsburg', 'stuttgart', 'vfb stuttgart',
        'borussia gladbach', 'gladbach', 'monchengladbach',
        'hoffenheim', 'tsg hoffenheim', 'mainz', 'mainz 05',
        'augsburg', 'fc augsburg', 'freiburg', 'sc freiburg',
        'cologne', 'köln', 'fc koln', '1. fc köln',
        'werder bremen', 'bremen', 'bochum', 'vfl bochum',
        'heidenheim', 'fc heidenheim'
    ],
    'euro': [
        'england', 'france', 'germany', 'spain', 'italy', 'portugal',
        'netherlands', 'belgium', 'croatia', 'denmark', 'switzerland'
    ],
    'copa-america': [
        'brazil', 'argentina', 'uruguay', 'colombia', 'chile',
        'peru', 'ecuador', 'venezuela', 'paraguay', 'bolivia'
    ]
}


class MultiSourceNewsFetcher:
    """Fetches football news from RSS. Uses in-memory cache."""

    def __init__(self):
        self.cache = {}
        self.cache_timeout = 120  # 2 phút
        self.session = requests.Session() if requests else None
        if self.session:
            self.session.timeout = 15

    def _get_cache_key(self, source: str, league: str) -> str:
        return f"{source}_{league}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}"

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        cached_time = self.cache[key].get('timestamp', 0)
        return (datetime.now(timezone.utc).timestamp() - cached_time) < self.cache_timeout

    def _generate_article_id(self, title: str, source: str) -> str:
        import hashlib
        content = f"{title.lower()[:100]}_{source}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _is_within_days(self, date_str: str, days: int = 3) -> bool:
        try:
            if isinstance(date_str, str):
                date_str = date_str.replace('Z', '+00:00')
                if '+' not in date_str and 'T' in date_str:
                    date_str += '+00:00'
                pub_date = datetime.fromisoformat(date_str)
            else:
                pub_date = date_str
            now = datetime.now(timezone.utc)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            diff = now - pub_date
            return 0 <= diff.days < days
        except Exception:
            return False

    def _get_relative_time(self, date_str: str) -> str:
        try:
            if isinstance(date_str, str):
                date_str = date_str.replace('Z', '+00:00')
                if '+' not in date_str and 'T' in date_str:
                    date_str += '+00:00'
                pub_time = datetime.fromisoformat(date_str)
            else:
                pub_time = date_str
            if pub_time.tzinfo is None:
                pub_time = pub_time.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = now - pub_time
            seconds = diff.total_seconds()
            if seconds < 0:
                seconds = abs(seconds)
                if seconds < 3600:
                    return f"Còn {int(seconds / 60)} phút"
                elif seconds < 86400:
                    return f"Còn {int(seconds / 3600)} giờ"
                else:
                    return f"Còn {int(seconds / 86400)} ngày"
            elif seconds < 60:
                return "Vừa xong"
            elif seconds < 3600:
                return f"{int(seconds / 60)} phút trước"
            elif seconds < 86400:
                return f"{int(seconds / 3600)} giờ trước"
            else:
                return f"{int(seconds / 86400)} ngày trước"
        except Exception:
            return "N/A"

    def _categorize_article_vn(self, title: str, description: str = "") -> str:
        text = (title + ' ' + (description or '')).lower()
        result_keywords = [
            'beat', 'defeated', 'won', 'win', 'victory', 'lose', 'lost', 'draw', 'drew',
            'score', 'scored', 'goal', 'goals', 'final score',
            'thắng', 'thua', 'hòa', 'kết quả', 'bàn thắng', 'tỷ số',
            'match report', 'post-match', 'highlights', 'recap',
            'hạ gục', 'đánh bại', 'chiến thắng', 'trận đấu kết thúc'
        ]
        if any(word in text for word in result_keywords):
            return NEWS_CATEGORIES['MATCH_RESULT']
        upcoming_keywords = [
            'preview', 'ahead of', 'upcoming', 'to face', 'will play', 'set to',
            'lineup', 'team news', 'predicted', 'starting xi',
            'trước trận', 'đội hình', 'dự kiến', 'sắp diễn ra', 'chuẩn bị',
            'đối đầu', 'gặp nhau', 'so tài', 'nhận định trước'
        ]
        if any(word in text for word in upcoming_keywords):
            return NEWS_CATEGORIES['UPCOMING_MATCH']
        return NEWS_CATEGORIES['HOT_NEWS']

    def _detect_league(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for league_id, teams in LEAGUE_CLUBS.items():
            for team in teams:
                if team in text_lower:
                    return TARGET_LEAGUES[league_id]['name']
        for league_id, config in TARGET_LEAGUES.items():
            for keyword in config['keywords']:
                if keyword in text_lower:
                    return config['name']
        return None

    def _is_valid_football_article(self, title: str, description: str = "") -> bool:
        text = (title + " " + (description or "")).lower()
        blacklist = [
            "girls soccer", "high school", "school soccer", "state soccer",
            "youth soccer", "college soccer", "ncaa", "district", "superintendent",
            "coach arrested", "employee", "porn", "arrest", "crime", "police"
        ]
        if any(b in text for b in blacklist):
            return False
        for league_teams in LEAGUE_CLUBS.values():
            for team in league_teams:
                if team in text:
                    return True
        for league in TARGET_LEAGUES.values():
            for kw in league["keywords"]:
                if kw in text:
                    return True
        return False

    def _is_hot_article(self, title: str, description: str = "", league: str = "") -> bool:
        text = (title + ' ' + (description or '')).lower()
        decisive_keywords = [
            'derby', 'el clasico', 'clásico', 'final', 'chung kết',
            'semi-final', 'semifinal', 'bán kết',
            'knockout', 'vòng loại trực tiếp', 'quarter-final', 'tứ kết',
            'title decider', 'title race', 'tranh vô địch',
            'relegation', 'trụ hạng', 'survival',
            'champions league spot', 'vé c1', 'top 4'
        ]
        for keyword in decisive_keywords:
            if keyword in text:
                return True
        if 'champions league' in text and any(w in text for w in ['knockout', 'quarter', 'semi', 'final']):
            return True
        return False

    def _estimate_read_time(self, content: str) -> str:
        if not content:
            return "3 phút đọc"
        words = len(content.split())
        minutes = max(2, min(15, int(words / 200)))
        return f"{minutes} phút đọc"

    def _extract_image_from_html(self, html_content: str) -> str:
        if not html_content:
            return ''
        match = re.search(r'<img[^>]+src="([^"]+)"', html_content)
        if match:
            return match.group(1)
        return ''

    def _clean_html(self, html_content: str) -> str:
        if not html_content:
            return ''
        text = re.sub(r'<img[^>]*>', '', html_content)
        text = re.sub(r'<[^>]+>', '', text)
        text = ' '.join(text.split())
        return text.strip()

    def fetch_from_rss(self, league_id: str = 'all') -> List[Dict]:
        if not requests or not RSS_FEED_URLS:
            return []
        articles = []
        seen_urls = set()
        for feed_url in RSS_FEED_URLS:
            try:
                response = self.session.get(feed_url, timeout=15)
                if response.status_code != 200:
                    continue
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') is not None else ''
                        link = item.find('link').text if item.find('link') is not None else ''
                        if link in seen_urls:
                            continue
                        seen_urls.add(link)
                        description_elem = item.find('description')
                        description_html = description_elem.text if description_elem is not None else ''
                        image_url = self._extract_image_from_html(description_html)
                        if not image_url:
                            media_ns = {'media': 'http://search.yahoo.com/mrss/'}
                            media_content = item.find('media:content', media_ns)
                            if media_content is not None:
                                image_url = media_content.get('url', '')
                        description = self._clean_html(description_html)
                        pub_date_elem = item.find('pubDate')
                        pub_date = pub_date_elem.text if pub_date_elem is not None else ''
                        pub_date_iso = ''
                        if pub_date:
                            try:
                                from email.utils import parsedate_to_datetime
                                dt = parsedate_to_datetime(pub_date)
                                pub_date_iso = dt.isoformat()
                            except Exception:
                                pub_date_iso = pub_date
                        if pub_date_iso and not self._is_within_days(pub_date_iso, days=5):
                            continue
                        creator_elem = item.find('{http://purl.org/dc/elements/1.1/}creator')
                        author = creator_elem.text if creator_elem is not None else 'RSS News'
                        detected_league = self._detect_league(title + ' ' + description)
                        if not self._is_valid_football_article(title, description):
                            continue
                        article = {
                            'id': self._generate_article_id(title, 'rss'),
                            'title': title,
                            'description': description[:300] if description else '',
                            'content': description,
                            'urlToImage': image_url,
                            'url': link,
                            'source': {'name': author},
                            'author': author,
                            'publishedAt': pub_date_iso,
                            'relativeTime': self._get_relative_time(pub_date_iso) if pub_date_iso else 'Mới cập nhật',
                            'league': detected_league or 'Football',
                            'category': self._categorize_article_vn(title, description),
                            'readTime': self._estimate_read_time(description),
                            'isHot': self._is_hot_article(title, description),
                            'apiSource': 'rss_feed'
                        }
                        articles.append(article)
                    except Exception:
                        continue
            except Exception:
                continue
        return articles

    def fetch_news(self, league_id: str = 'all', force_refresh: bool = False) -> List[Dict]:
        cache_key = self._get_cache_key('news', league_id)
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get('data', [])
        new_articles = self.fetch_from_rss(league_id)
        all_articles = new_articles
        rss_list = [a for a in all_articles if a.get('apiSource') == 'rss_feed']
        other_list = [a for a in all_articles if a.get('apiSource') != 'rss_feed']
        other_list.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        all_articles = rss_list + other_list
        self.cache[cache_key] = {
            'data': all_articles,
            'timestamp': datetime.now(timezone.utc).timestamp()
        }
        return all_articles

    def clear_cache(self):
        self.cache = {}


news_fetcher = MultiSourceNewsFetcher()
