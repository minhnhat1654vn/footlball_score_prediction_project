"""
Configuration module for Football Score Prediction application.
Contains all configuration constants, API keys, and league mappings.
"""
import os
import pytz
from pathlib import Path

# Load .env from project root (giống folder "file thêm": RSS_NEWS_URLS trong .env)
_ROOT = Path(__file__).resolve().parent
_ENV_PATH = _ROOT / '.env'
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_PATH)
except ImportError:
    pass

# RSS News: ưu tiên biến môi trường (từ .env hoặc env), không có thì dùng default từ "file thêm"
_RSS_DEFAULT = (
    'https://rss.app/feeds/teCEwBrpa0l2F8Zl.xml,'
    'https://rss.app/feeds/tUYYnoZX9Sv41uYg.xml,'
    'https://rss.app/feeds/tPcwzq14qA1rNUFD.xml,'
    'https://rss.app/feeds/tfuYODKYwqhozXSA.xml,'
    'https://rss.app/feeds/tET2jFvHq4nDcfxW.xml'
)
RSS_NEWS_URLS = os.environ.get('RSS_NEWS_URLS', _RSS_DEFAULT).strip() or _RSS_DEFAULT

# Default timezone for date filtering (Vietnam)
APP_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# Flask app configuration
FLASK_SECRET_KEY = 'football-prediction-secret-key'

# ======================== SOFASCORE API CONFIGURATION ========================
SOFASCORE_API_KEY = "34fc4fbef4msh48c151d85c45711p104adbjsn1a811e7e88ad"
SOFASCORE_API_HOST = "sofascore.p.rapidapi.com"
SOFASCORE_BASE_URL = "https://sofascore.p.rapidapi.com"

# API Headers
SOFASCORE_HEADERS = {
    "x-rapidapi-key": SOFASCORE_API_KEY,
    "x-rapidapi-host": SOFASCORE_API_HOST,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Retry và delay configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # giây
REQUEST_DELAY = 0.1  # Delay giữa các requests để tránh rate limit (faster UI)

# Leagues to fetch fixtures for (fast mode)
FIXTURES_LEAGUES = [
    39,   # Premier League
    61,   # Ligue 1
    78,   # Bundesliga
    140,  # La Liga
    135,  # Serie A
    2,    # UEFA Champions League
]

# ======================== LEAGUE CONFIGURATION ========================
# Sofascore unique tournament IDs
SOFASCORE_TOURNAMENT_IDS = {
    39: 17,      # Premier League
    140: 8,      # La Liga
    135: 23,     # Serie A
    78: 35,      # Bundesliga
    61: 34,      # Ligue 1
    2: 178,        # UEFA Champions League (football, id=7 như JSON bạn gửi)
    88: 37,      # Eredivisie
    94: 238,     # Primeira Liga
    253: 42,     # MLS
    340: 52,     # V.League 1
}

# Sofascore season IDs (2025/26 season - CURRENT).
# Với Champions League, dùng seasonId thật từ RapidAPI ví dụ: 29415.
SOFASCORE_SEASON_IDS = {
    39: 76986,   # Premier League 25/26 (CURRENT SEASON)
    140: 76986,  # La Liga (sẽ được get_season_id cập nhật chính xác)
    135: 76986,  # Serie A
    78: 76986,   # Bundesliga
    61: 76986,   # Ligue 1
    2: 29415,    # UEFA Champions League 25/26 (seasonId ví dụ từ RapidAPI)
    88: 76986,   # Eredivisie
    94: 76986,   # Primeira Liga
    253: 76986,  # MLS
    340: 76986,  # V.League 1
}

POPULAR_LEAGUES = {
    39: 'Premier League',           # England
    140: 'La Liga',                # Spain
    135: 'Serie A',                # Italy
    78: 'Bundesliga',              # Germany
    61: 'Ligue 1',                 # France
    2: 'UEFA Champions League',    # Europe
    88: 'Eredivisie',              # Netherlands
    94: 'Primeira Liga',           # Portugal
    253: 'MLS',                    # USA
    340: 'V.League 1'              # Vietnam
}

# League logos (fallback for UI)
LEAGUE_LOGOS = {
    39: "https://media.api-sports.io/football/leagues/39.png",
    140: "https://media.api-sports.io/football/leagues/140.png",
    135: "https://media.api-sports.io/football/leagues/135.png",
    78: "https://media.api-sports.io/football/leagues/78.png",
    61: "https://media.api-sports.io/football/leagues/61.png",
    2: "https://media.api-sports.io/football/leagues/2.png",
    88: "https://media.api-sports.io/football/leagues/88.png",
    94: "https://media.api-sports.io/football/leagues/94.png",
    253: "https://media.api-sports.io/football/leagues/253.png",
    340: "https://media.api-sports.io/football/leagues/340.png",
}

# League teams data
LEAGUE_TEAMS = {
    'premier-league': [
        {'name': 'Manchester City', 'image': 'manchester-city', 'league': 'Premier League', 'league_id': 39},
        {'name': 'Liverpool', 'image': 'liverpool', 'league': 'Premier League', 'league_id': 39},
        {'name': 'Arsenal', 'image': 'arsenal', 'league': 'Premier League', 'league_id': 39},
        {'name': 'Manchester United', 'image': 'manchester-united', 'league': 'Premier League', 'league_id': 39},
        {'name': 'Chelsea', 'image': 'chelsea', 'league': 'Premier League', 'league_id': 39}
    ],
    'la-liga': [
        {'name': 'Real Madrid', 'image': 'real-madrid', 'league': 'La Liga', 'league_id': 140},
        {'name': 'Barcelona', 'image': 'barcelona', 'league': 'La Liga', 'league_id': 140},
        {'name': 'Atletico Madrid', 'image': 'atletico-madrid', 'league': 'La Liga', 'league_id': 140},
        {'name': 'Sevilla', 'image': 'sevilla', 'league': 'La Liga', 'league_id': 140},
        {'name': 'Real Sociedad', 'image': 'real-sociedad', 'league': 'La Liga', 'league_id': 140}
    ],
    'bundesliga': [
        {'name': 'Bayern Munich', 'image': 'bayern-munich', 'league': 'Bundesliga', 'league_id': 78},
        {'name': 'Borussia Dortmund', 'image': 'borussia-dortmund', 'league': 'Bundesliga', 'league_id': 78},
        {'name': 'RB Leipzig', 'image': 'rb-leipzig', 'league': 'Bundesliga', 'league_id': 78},
        {'name': 'Bayer Leverkusen', 'image': 'bayer-leverkusen', 'league': 'Bundesliga', 'league_id': 78},
        {'name': 'Borussia Monchengladbach', 'image': 'borussia-monchengladbach', 'league': 'Bundesliga', 'league_id': 78}
    ],
    'serie-a': [
        {'name': 'Inter Milan', 'image': 'inter-milan', 'league': 'Serie A', 'league_id': 135},
        {'name': 'AC Milan', 'image': 'ac-milan', 'league': 'Serie A', 'league_id': 135},
        {'name': 'Juventus', 'image': 'juventus', 'league': 'Serie A', 'league_id': 135},
        {'name': 'Napoli', 'image': 'napoli', 'league': 'Serie A', 'league_id': 135},
        {'name': 'Roma', 'image': 'roma', 'league': 'Serie A', 'league_id': 135}
    ],
    'ligue-1': [
        {'name': 'Paris Saint-Germain', 'image': 'psg', 'league': 'Ligue 1', 'league_id': 61},
        {'name': 'Marseille', 'image': 'marseille', 'league': 'Ligue 1', 'league_id': 61},
        {'name': 'Lyon', 'image': 'lyon', 'league': 'Ligue 1', 'league_id': 61},
        {'name': 'Monaco', 'image': 'monaco', 'league': 'Ligue 1', 'league_id': 61},
        {'name': 'Lille', 'image': 'lille', 'league': 'Ligue 1', 'league_id': 61}
    ]
}

# ======================== CACHE CONFIGURATION ========================
CACHE_DIR = Path("cache")
PERMANENT_CACHE_DIR = Path("permanent_cache")
LOGO_DIR = Path("static/images/team_logos")

# Flask app configuration dict
app_config = {
    'SECRET_KEY': FLASK_SECRET_KEY
}
