"""
Sofascore API client module for Football Score Prediction application.
Handles all API requests to Sofascore with retry logic and error handling.
"""
import time
import requests
from datetime import datetime
from config import (
    SOFASCORE_BASE_URL, SOFASCORE_HEADERS, MAX_RETRIES, RETRY_DELAY, REQUEST_DELAY,
    SOFASCORE_TOURNAMENT_IDS, SOFASCORE_SEASON_IDS, APP_TZ
)
from cache_utils import (
    load_from_cache, save_to_cache, is_cache_valid,
    cache_team_logo, get_cached_team_logo, cache_team_logos_from_standings
)
from utils import safe_float


def sofascore_get(endpoint, params=None):
    """Make a request to Sofascore API with retry logic"""
    url = f"{SOFASCORE_BASE_URL}{endpoint}"
    
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url, headers=SOFASCORE_HEADERS, params=params, timeout=15)
            print(f"[SOFASCORE] {endpoint} - Status: {response.status_code}")
            
            if response.status_code == 429:
                print(f"[SOFASCORE] ⚠️ Rate limit! Waiting {RETRY_DELAY * (2 ** attempt)}s...")
                time.sleep(RETRY_DELAY * (2 ** attempt))
                continue
            
            # Handle 204 No Content (empty response)
            if response.status_code == 204:
                print(f"[SOFASCORE] No content (204) for {endpoint}")
                return None
            
            response.raise_for_status()
            
            # Check if response has content before parsing JSON
            if not response.text or response.text.strip() == '':
                return None
            
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"[SOFASCORE] Error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(wait_time)
            else:
                print(f"[SOFASCORE] Failed after {MAX_RETRIES} attempts: {e}")
                return None
        except ValueError as e:
            # JSON decode error (empty response, etc.)
            print(f"[SOFASCORE] JSON decode error: {e}")
            return None
    return None


def sofascore_get_binary(endpoint, params=None):
    """Make a request to Sofascore API that returns binary (e.g. image/png)."""
    url = f"{SOFASCORE_BASE_URL}{endpoint}"

    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url, headers=SOFASCORE_HEADERS, params=params, timeout=15)
            print(f"[SOFASCORE] {endpoint} - Status: {response.status_code} (binary)")

            if response.status_code == 429:
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"[SOFASCORE] ⚠️ Rate limit! Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            if response.status_code == 204:
                print(f"[SOFASCORE] No content (204) for {endpoint}")
                return None

            response.raise_for_status()
            return response.content, response.headers.get("content-type")
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"[SOFASCORE] Error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(wait_time)
            else:
                print(f"[SOFASCORE] Failed after {MAX_RETRIES} attempts: {e}")
                return None
    return None


def get_season_id(league_id):
    """Get season ID for a given league"""
    def desired_season_year_string():
        now = datetime.now(APP_TZ)
        yy = now.year % 100
        if now.month >= 7:
            return f"{yy:02d}/{(yy+1):02d}"
        return f"{(yy-1):02d}/{yy:02d}"

    desired_year = desired_season_year_string()

    # Với Champions League (league_id=2), bỏ qua cache cũ để tránh dùng sai seasonId
    cached = None
    if league_id != 2:
        cached = load_from_cache(f"season_{league_id}", "season")
        if cached and cached.get("season_id") and cached.get("year") == desired_year:
            return cached["season_id"]

    # Try mapping first
    default_season = SOFASCORE_SEASON_IDS.get(league_id, 76986)
    try:
        tournament_id = SOFASCORE_TOURNAMENT_IDS.get(league_id, league_id)
        endpoint = "/tournaments/get-seasons"
        params = {"tournamentId": tournament_id}
        data = sofascore_get(endpoint, params)
        seasons = []
        if data:
            if "seasons" in data:
                seasons = data["seasons"]
            elif "uniqueTournamentSeasons" in data:
                for ut in data["uniqueTournamentSeasons"]:
                    if ut.get("uniqueTournament", {}).get("id") == tournament_id:
                        seasons = ut.get("seasons", [])
                        break
        if seasons:
            # Prefer the season matching current football season year string (e.g. 25/26)
            match = None
            for s in seasons:
                if s.get("year") == desired_year or (s.get("name") and desired_year in s.get("name")):
                    match = s
                    break
            picked = match or seasons[0]
            # Fallback: pick the season with the largest id (usually newest)
            try:
                picked = match or sorted(seasons, key=lambda s: int(s.get("id", 0)), reverse=True)[0]
            except Exception:
                picked = match or seasons[0]

            season_id = picked.get("id", default_season)
            save_to_cache(
                f"season_{league_id}",
                "season",
                {"season_id": season_id, "year": picked.get("year") or desired_year},
            )
            SOFASCORE_SEASON_IDS[league_id] = season_id
            return season_id
    except Exception:
        pass
    return default_season


def get_match_by_id(match_id):
    """Fetch match details from Sofascore"""
    key = f"match_{match_id}"
    
    if is_cache_valid(key, "match"):
        return load_from_cache(key, "match")
    
    # Sofascore endpoint for match details (RapidAPI format)
    endpoint = "/matches/detail"
    params = {"matchId": match_id}
    
    data = sofascore_get(endpoint, params)
    
    if data and 'event' in data:
        match = data['event']
        save_to_cache(key, "match", match)
        return match
    
    return None


def get_match_incidents(match_id):
    """Fetch match incidents (goals, cards, etc.) from Sofascore. Kết quả được cache để giảm request."""
    key = f"incidents_{match_id}"
    cached = load_from_cache(key, "incidents")
    if cached is not None and isinstance(cached, list):
        return cached
    endpoint = "/matches/get-incidents"
    params = {"matchId": match_id}
    data = sofascore_get(endpoint, params)
    if data and "incidents" in data:
        incidents = data["incidents"]
        if incidents:
            save_to_cache(key, "incidents", incidents)
        return incidents
    return []


def get_or_fetch_team_stats(team_id, league_id, season):
    """Fetch team statistics from Sofascore"""
    key = f"{team_id}_{league_id}_{season}"
    
    cached = load_from_cache(key, "team_stats")
    if cached:
        return cached
    
    print(f"[SOFASCORE] Fetching team stats for team {team_id}, league {league_id}")
    
    # Get Sofascore tournament ID and season ID
    sofascore_tournament_id = SOFASCORE_TOURNAMENT_IDS.get(league_id, league_id)
    sofascore_season_id = get_season_id(league_id)
    
    # Sofascore endpoint for team statistics (RapidAPI format)
    endpoint = "/teams/get-statistics"
    params = {
        "teamId": team_id,
        "tournamentId": sofascore_tournament_id,
        "seasonId": sofascore_season_id,
        "type": "overall"
    }
    
    data = sofascore_get(endpoint, params)
    
    if data and 'statistics' in data:
        save_to_cache(key, "team_stats", data)
        return data
    
    return None


def get_or_fetch_standings(league_id, season):
    """Fetch league standings from Sofascore"""
    key = f"{league_id}_{season}"
    
    cached = load_from_cache(key, "standings")
    if cached:
        return cached
    
    print(f"[SOFASCORE] Fetching standings for league {league_id}")
    
    # Get Sofascore tournament ID and season ID
    sofascore_tournament_id = SOFASCORE_TOURNAMENT_IDS.get(league_id, league_id)
    sofascore_season_id = get_season_id(league_id)
    
    # Sofascore endpoint for standings (RapidAPI format)
    endpoint = "/tournaments/get-standings"
    params = {
        "tournamentId": sofascore_tournament_id,
        "seasonId": sofascore_season_id,
        "type": "total"
    }
    
    data = sofascore_get(endpoint, params)
    
    if data:
        save_to_cache(key, "standings", data)
        cache_team_logos_from_standings(data, cache_team_logo)
        return data
    
    return None


def get_or_fetch_h2h(home_id, away_id):
    """Fetch head-to-head records using team matches"""
    key = f"{home_id}_{away_id}"
    
    cached = load_from_cache(key, "h2h")
    if cached:
        return cached
    
    print(f"[SOFASCORE] Fetching h2h for {home_id} vs {away_id}")
    
    # Get recent matches for home team
    endpoint = "/teams/get-matches"
    params = {
        "teamId": home_id,
        "pageIndex": 0
    }
    
    data = sofascore_get(endpoint, params)
    
    if data and 'events' in data:
        # Filter matches where away_id is opponent
        h2h_matches = []
        for event in data['events']:
            home_team_id = event.get('homeTeam', {}).get('id')
            away_team_id = event.get('awayTeam', {}).get('id')
            
            # Check if this is a h2h match
            if (home_team_id == home_id and away_team_id == away_id) or \
               (home_team_id == away_id and away_team_id == home_id):
                h2h_matches.append(event)
        
        h2h_data = {'events': h2h_matches}
        save_to_cache(key, "h2h", h2h_data)
        return h2h_data
    
    return None


def get_team_id_from_name(team_name, league_id=None):
    """
    Resolve Sofascore teamId by name.
    
    IMPORTANT: If league_id is provided, prefer resolving from that league's standings
    to avoid wrong matches from /teams/search (common source of incorrect logos).
    """
    if not team_name:
        return None

    normalized = str(team_name).strip().lower()

    # 1) Prefer standings for the league (more reliable than global search)
    if league_id:
        try:
            standings_data = get_or_fetch_standings(league_id, get_season_id(league_id))
            if standings_data and "standings" in standings_data:
                rows = standings_data["standings"][0]["rows"]
                for row in rows:
                    t = row.get("team", {}) or {}
                    if str(t.get("name", "")).strip().lower() == normalized:
                        return t.get("id")
        except Exception:
            pass

    # 2) Fallback: global search
    endpoint = "/teams/search"
    params = {"name": team_name}
    
    data = sofascore_get(endpoint, params)

    teams = (data or {}).get("teams") or []
    if not teams:
        return None

    # Try exact match first, otherwise best-effort first result.
    for t in teams:
        if str(t.get("name", "")).strip().lower() == normalized:
            return t.get("id")
    return teams[0].get("id")


def fetch_team_stats(team_name, league_id):
    """Fetch team stats and return simplified stats dictionary"""
    try:
        # Find team ID by name
        team_id = get_team_id_from_name(team_name, league_id)
        if not team_id:
            print(f"[SOFASCORE] Could not find team ID for {team_name}")
            return {
                'wins': 0, 'draws': 0, 'losses': 0, 'rank': 'N/A', 'points': 0,
                'goals_for': 0, 'goals_against': 0, 'goal_diff': 0
            }
        
        stats_data = get_or_fetch_team_stats(team_id, league_id, get_season_id(league_id))
        logo_url = get_cached_team_logo(team_id)
        
        # Get rank and results from standings
        rank = 'N/A'
        standings_wins = None
        standings_draws = None
        standings_losses = None
        standings_data = get_or_fetch_standings(league_id, get_season_id(league_id))
        if standings_data and 'standings' in standings_data:
            try:
                rows = standings_data['standings'][0]['rows']
                for row in rows:
                    if row.get('team', {}).get('id') == team_id:
                        rank = row.get('position', 'N/A')
                        logo_url = logo_url or row.get('team', {}).get('imageUrl')
                        standings_wins = row.get('wins')
                        standings_draws = row.get('draws')
                        standings_losses = row.get('losses')
                        break
            except (KeyError, IndexError, TypeError):
                pass
        
        if stats_data and 'statistics' in stats_data:
            stats = stats_data['statistics']
            wins = safe_float(stats.get('wins', standings_wins or 0))
            draws = safe_float(stats.get('draws', standings_draws or 0))
            losses = safe_float(stats.get('losses', standings_losses or 0))
            goals_for = safe_float(stats.get('goalsScored', 0))
            goals_against = safe_float(stats.get('goalsConceded', 0))
            
            # Parse Sofascore response
            return {
                'wins': int(wins),
                'draws': int(draws),
                'losses': int(losses),
                'rank': rank,
                'points': int(wins * 3 + draws),
                'goals_for': int(goals_for),
                'goals_against': int(goals_against),
                'goal_diff': int(goals_for - goals_against),
                'logo_url': logo_url
            }
        
        return {
            'wins': 0, 'draws': 0, 'losses': 0, 'rank': 'N/A', 'points': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_diff': 0
        }
    except Exception as e:
        print(f"[SOFASCORE] Error fetching team stats for {team_name}: {e}")
        return {
            'wins': 0, 'draws': 0, 'losses': 0, 'rank': 'N/A', 'points': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_diff': 0
        }
