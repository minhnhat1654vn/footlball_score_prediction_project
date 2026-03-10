"""
Feature preparation module for Football Score Prediction application.
Prepares features for ML models.
"""
import numpy as np
import traceback
from datetime import datetime
from api_client import (
    get_or_fetch_team_stats, get_or_fetch_standings, get_or_fetch_h2h, get_season_id
)
from utils import safe_float


def _league_avg_goals_and_matches(league_id, season):
    """Returns (avg_goals_per_match, total_matches) from standings, or (None, None) if unavailable."""
    try:
        season_id = get_season_id(league_id)
        standings_data = get_or_fetch_standings(league_id, season_id)
        if not standings_data or "standings" not in standings_data:
            return None, None
        rows = standings_data["standings"][0]["rows"]
        n = len(rows)
        if n < 2:
            return None, None
        total_goals = sum(safe_float(r.get("scoresFor") or r.get("goalsFor") or 0) for r in rows)
        total_matches = n * (n - 1)
        if total_matches <= 0:
            return None, None
        return total_goals / total_matches, total_matches
    except Exception:
        return None, None


def prepare_logistic_features(match):
    """
    Prepare 8 features for logistic regression (Win/Draw/Loss).
    Order must match notebook: [HAS, HDS, AAS, ADS, HST, AST, HC, AC].
    When standings exist, HAS/HDS/AAS/ADS are league-relative (giống notebook) để scale gần training data.
    """
    try:
        home_team_id = match['homeTeam']['id']
        away_team_id = match['awayTeam']['id']
        league_id = match.get('tournament', {}).get('uniqueTournament', {}).get('id', 17)
        season = datetime.fromtimestamp(match.get('startTimestamp', 0)).year

        print(f"[FEATURE] Preparing logistic features for {match['homeTeam']['name']} vs {match['awayTeam']['name']}")

        home_stats_data = get_or_fetch_team_stats(home_team_id, league_id, season)
        away_stats_data = get_or_fetch_team_stats(away_team_id, league_id, season)

        if not home_stats_data or not away_stats_data:
            print(f"[FEATURE] ❌ Missing team stats for prediction")
            return None

        home_stats = home_stats_data.get('statistics', {})
        away_stats = away_stats_data.get('statistics', {})

        home_matches = max(safe_float(home_stats.get('matches', 1)), 1)
        away_matches = max(safe_float(away_stats.get('matches', 1)), 1)

        league_avg, _ = _league_avg_goals_and_matches(league_id, season)
        if league_avg is not None and league_avg > 0:
            # Chuẩn hóa gần notebook: HAS = (goals/matches) / league_avg (league-relative strength)
            HAS = (safe_float(home_stats.get('goalsScored', 0)) / home_matches) / league_avg
            HDS = (safe_float(home_stats.get('goalsConceded', 0)) / home_matches) / league_avg
            AAS = (safe_float(away_stats.get('goalsScored', 0)) / away_matches) / league_avg
            ADS = (safe_float(away_stats.get('goalsConceded', 0)) / away_matches) / league_avg
        else:
            HAS = safe_float(home_stats.get('goalsScored', 0)) / home_matches
            HDS = safe_float(home_stats.get('goalsConceded', 0)) / home_matches
            AAS = safe_float(away_stats.get('goalsScored', 0)) / away_matches
            ADS = safe_float(away_stats.get('goalsConceded', 0)) / away_matches

        HST = safe_float(home_stats.get('wins', 0)) / home_matches
        AST = safe_float(away_stats.get('wins', 0)) / away_matches
        HC = safe_float(home_stats.get('cleanSheets', 0)) / home_matches
        AC = safe_float(away_stats.get('cleanSheets', 0)) / away_matches

        features = np.array([HAS, HDS, AAS, ADS, HST, AST, HC, AC], dtype=float)
        print(f"[FEATURE] Logistic features: {features}")
        return features
    except Exception as e:
        print(f"[FEATURE] Error preparing logistic features: {e}")
        traceback.print_exc()
        return None


def prepare_poisson_features(match):
    """Prepare features for Poisson regression (Score prediction)"""
    try:
        home_team_id = match['homeTeam']['id']
        away_team_id = match['awayTeam']['id']
        league_id = match.get('tournament', {}).get('uniqueId', 1)
        season = datetime.fromtimestamp(match.get('startTimestamp', 0)).year
        fixture_id = match['id']
        
        print(f"[FEATURE] Preparing Poisson features for {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
        
        # 1. H2H
        h2h_data = get_or_fetch_h2h(home_team_id, away_team_id)
        h2h_home_wins = 0
        h2h_avg_home_goals = 0
        h2h_avg_away_goals = 0
        
        if h2h_data and 'events' in h2h_data:
            # Parse h2h events from Sofascore
            events = h2h_data['events']
            home_goals_list = []
            away_goals_list = []
            
            for event in events[:10]:  # Last 10 h2h matches
                event_home_id = event.get('homeTeam', {}).get('id')
                event_away_id = event.get('awayTeam', {}).get('id')
                home_score = event.get('homeScore', {}).get('normaltime')
                away_score = event.get('awayScore', {}).get('normaltime')
                
                if home_score is not None and away_score is not None:
                    # If home_team_id was home in this match
                    if event_home_id == home_team_id:
                        home_goals_list.append(home_score)
                        away_goals_list.append(away_score)
                        if home_score > away_score:
                            h2h_home_wins += 1
                    # If home_team_id was away in this match
                    elif event_away_id == home_team_id:
                        home_goals_list.append(away_score)
                        away_goals_list.append(home_score)
                        if away_score > home_score:
                            h2h_home_wins += 1
            
            h2h_avg_home_goals = np.mean(home_goals_list) if home_goals_list else 0
            h2h_avg_away_goals = np.mean(away_goals_list) if away_goals_list else 0
        
        # 2. Standings
        standings_data = get_or_fetch_standings(league_id, season)
        home_team_rank = 0
        away_team_rank = 0
        rank_diff = 0
        
        if standings_data and 'standings' in standings_data:
            # Sofascore format: standings[0].rows[]
            try:
                rows = standings_data['standings'][0]['rows']
                for row in rows:
                    team_id = row.get('team', {}).get('id')
                    if team_id == home_team_id:
                        home_team_rank = row.get('position', 0)
                    if team_id == away_team_id:
                        away_team_rank = row.get('position', 0)
                rank_diff = home_team_rank - away_team_rank
            except (KeyError, IndexError, TypeError) as e:
                print(f"[FEATURE] Error parsing standings: {e}")
        
        # 3. Odds (Sofascore includes odds)
        home_win_prob = 0.33
        draw_prob = 0.33
        away_win_prob = 0.34
        
        # 4. Team form
        home_stats_data = get_or_fetch_team_stats(home_team_id, league_id, season)
        away_stats_data = get_or_fetch_team_stats(away_team_id, league_id, season)
        
        home_team_avg_points = 0
        home_team_avg_goals_scored = 0
        home_team_avg_goals_conceded = 0
        away_team_avg_points = 0
        away_team_avg_goals_scored = 0
        away_team_avg_goals_conceded = 0
        
        if home_stats_data and 'statistics' in home_stats_data:
            home_stats = home_stats_data['statistics']
            played = max(safe_float(home_stats.get('matches', 1)), 1)
            wins = safe_float(home_stats.get('wins', 0))
            draws = safe_float(home_stats.get('draws', 0))
            
            home_team_avg_points = (wins * 3 + draws) / played
            home_team_avg_goals_scored = safe_float(home_stats.get('goalsScored', 0)) / played
            home_team_avg_goals_conceded = safe_float(home_stats.get('goalsConceded', 0)) / played
        
        if away_stats_data and 'statistics' in away_stats_data:
            away_stats = away_stats_data['statistics']
            played = max(safe_float(away_stats.get('matches', 1)), 1)
            wins = safe_float(away_stats.get('wins', 0))
            draws = safe_float(away_stats.get('draws', 0))
            
            away_team_avg_points = (wins * 3 + draws) / played
            away_team_avg_goals_scored = safe_float(away_stats.get('goalsScored', 0)) / played
            away_team_avg_goals_conceded = safe_float(away_stats.get('goalsConceded', 0)) / played
        
        # Check if we have enough data
        if (home_team_avg_goals_scored == 0 and home_team_avg_goals_conceded == 0 and 
            away_team_avg_goals_scored == 0 and away_team_avg_goals_conceded == 0):
            print(f"[FEATURE] ❌ Missing team stats for Poisson")
            return None
        
        features = np.array([
            h2h_home_wins, h2h_avg_home_goals, h2h_avg_away_goals,
            home_team_rank, away_team_rank, rank_diff,
            home_win_prob, draw_prob, away_win_prob,
            home_team_avg_points, away_team_avg_points,
            home_team_avg_goals_scored, home_team_avg_goals_conceded,
            away_team_avg_goals_scored, away_team_avg_goals_conceded
        ])
        print(f"[FEATURE] Poisson features: {features}")
        return features
    except Exception as e:
        print(f"[FEATURE] Error preparing Poisson features: {e}")
        traceback.print_exc()
        return None
