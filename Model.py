#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, PoissonRegressor, LinearRegression
from sklearn.svm import SVC
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import normalize, StandardScaler
import joblib

# --- Load dữ liệu ---
def load_data():
    print("Đang load dữ liệu từ database...")
    with sqlite3.connect('database.sqlite') as con:
        countries = pd.read_sql_query("SELECT * from Country", con)
        matches = pd.read_sql_query("SELECT * from Match", con)
        leagues = pd.read_sql_query("SELECT * from League", con)
        teams = pd.read_sql_query("SELECT * from Team", con)
    print(f"Đã load xong dữ liệu: {len(matches)} trận đấu, {len(leagues)} giải đấu")
    # Đổi tên cột id thành match_id
    matches = matches.rename(columns={'id': 'match_id'})
    return countries, matches, leagues, teams

# --- Lọc giải đấu lớn ---
def filter_main_leagues(countries, leagues, matches):
    main_leagues = [
        'England Premier League',
        'Spain LIGA BBVA',
        'Germany 1. Bundesliga',
        'Italy Serie A',
        'France Ligue 1',
        'Netherlands Eredivisie',
        'Portugal Liga ZON Sagres',
        'Belgium Jupiler League',
        'Scotland Premier League',
        'Switzerland Super League'
    ]
    leagues = leagues[leagues['name'].isin(main_leagues)]
    matches = matches[matches['league_id'].isin(leagues['id'])]
    return leagues, matches

# --- Tạo cột tổng số bàn thắng ---
def add_total_goal(matches):
    matches['total_goal'] = matches['home_team_goal'] + matches['away_team_goal']
    return matches

# --- Tạo nhãn kết quả trận đấu ---
def add_result_label(df):
    def res(row):
        if row['home_team_goal'] == row['away_team_goal']:
            return 0
        elif row['home_team_goal'] > row['away_team_goal']:
            return 1
        else:
            return -1
    df['result'] = df.apply(res, axis=1)
    return df

# --- Tính toán lịch sử đối đầu (H2H) ---
def calculate_h2h_features(matches, n_previous_matches=5):
    """
    Tính toán các feature dựa trên lịch sử đối đầu giữa 2 đội
    """
    matches = matches.sort_values('date')
    h2h_features = []
    
    for idx, match in matches.iterrows():
        home_team = match['home_team_api_id']
        away_team = match['away_team_api_id']
        match_date = match['date']
        
        # Lấy các trận đấu trước đó giữa 2 đội
        previous_matches = matches[
            (matches['date'] < match_date) &
            ((matches['home_team_api_id'] == home_team) & (matches['away_team_api_id'] == away_team) |
             (matches['home_team_api_id'] == away_team) & (matches['away_team_api_id'] == home_team))
        ].tail(n_previous_matches)
        
        if len(previous_matches) > 0:
            # Tính số trận thắng của đội chủ nhà
            home_wins = len(previous_matches[
                ((previous_matches['home_team_api_id'] == home_team) & 
                 (previous_matches['home_team_goal'] > previous_matches['away_team_goal'])) |
                ((previous_matches['away_team_api_id'] == home_team) & 
                 (previous_matches['away_team_goal'] > previous_matches['home_team_goal']))
            ])
            
            # Tính số bàn thắng trung bình của đội chủ nhà
            home_goals = []
            for _, prev_match in previous_matches.iterrows():
                if prev_match['home_team_api_id'] == home_team:
                    home_goals.append(prev_match['home_team_goal'])
                else:
                    home_goals.append(prev_match['away_team_goal'])
            avg_home_goals = np.mean(home_goals) if home_goals else 0
            
            # Tính số bàn thắng trung bình của đội khách
            away_goals = []
            for _, prev_match in previous_matches.iterrows():
                if prev_match['home_team_api_id'] == away_team:
                    away_goals.append(prev_match['home_team_goal'])
                else:
                    away_goals.append(prev_match['away_team_goal'])
            avg_away_goals = np.mean(away_goals) if away_goals else 0
            
            h2h_features.append({
                'match_id': match['match_id'],
                'h2h_home_wins': home_wins,
                'h2h_avg_home_goals': avg_home_goals,
                'h2h_avg_away_goals': avg_away_goals
            })
        else:
            h2h_features.append({
                'match_id': match['match_id'],
                'h2h_home_wins': 0,
                'h2h_avg_home_goals': 0,
                'h2h_avg_away_goals': 0
            })
    
    return pd.DataFrame(h2h_features)

# --- Tính toán bảng xếp hạng ---
def calculate_league_standings(matches, n_previous_matches=5):
    """
    Tính toán vị trí xếp hạng của các đội trước mỗi trận đấu
    """
    matches = matches.sort_values('date')
    standings_features = []
    
    for idx, match in matches.iterrows():
        league_id = match['league_id']
        match_date = match['date']
        home_team = match['home_team_api_id']
        away_team = match['away_team_api_id']
        
        # Lấy các trận đấu trước đó trong cùng giải đấu
        previous_matches = matches[
            (matches['league_id'] == league_id) &
            (matches['date'] < match_date)
        ].tail(n_previous_matches * 10)  # Lấy nhiều trận hơn để tính điểm
        
        if len(previous_matches) > 0:
            # Tính điểm cho tất cả các đội
            team_points = {}
            for _, prev_match in previous_matches.iterrows():
                home = prev_match['home_team_api_id']
                away = prev_match['away_team_api_id']
                home_goals = prev_match['home_team_goal']
                away_goals = prev_match['away_team_goal']
                
                if home not in team_points:
                    team_points[home] = 0
                if away not in team_points:
                    team_points[away] = 0
                
                if home_goals > away_goals:
                    team_points[home] += 3
                elif home_goals == away_goals:
                    team_points[home] += 1
                    team_points[away] += 1
                else:
                    team_points[away] += 3
            
            # Tính vị trí xếp hạng
            sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)
            home_rank = next((i+1 for i, (team, _) in enumerate(sorted_teams) if team == home_team), len(sorted_teams)+1)
            away_rank = next((i+1 for i, (team, _) in enumerate(sorted_teams) if team == away_team), len(sorted_teams)+1)
            
            standings_features.append({
                'match_id': match['match_id'],
                'home_team_rank': home_rank,
                'away_team_rank': away_rank,
                'rank_diff': home_rank - away_rank
            })
        else:
            standings_features.append({
                'match_id': match['match_id'],
                'home_team_rank': 0,
                'away_team_rank': 0,
                'rank_diff': 0
            })
    
    return pd.DataFrame(standings_features)

# --- Xử lý tỷ lệ cược ---
def process_odds_features(matches):
    """
    Xử lý các feature liên quan đến tỷ lệ cược
    """
    odds_columns = ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'IWH', 'IWD', 'IWA']
    
    # Kiểm tra xem các cột odds có tồn tại không
    available_odds = [col for col in odds_columns if col in matches.columns]
    
    if not available_odds:
        return pd.DataFrame({'match_id': matches['match_id']})
    
    odds_features = []
    for idx, match in matches.iterrows():
        odds_dict = {'match_id': match['match_id']}
        
        # Tính trung bình tỷ lệ cược từ các nhà cái khác nhau
        if 'B365H' in available_odds:
            odds_dict['avg_home_win_odds'] = np.mean([match[col] for col in available_odds if col.endswith('H')])
            odds_dict['avg_draw_odds'] = np.mean([match[col] for col in available_odds if col.endswith('D')])
            odds_dict['avg_away_win_odds'] = np.mean([match[col] for col in available_odds if col.endswith('A')])
            
            # Tính implied probability
            total_prob = (1/odds_dict['avg_home_win_odds'] + 
                         1/odds_dict['avg_draw_odds'] + 
                         1/odds_dict['avg_away_win_odds'])
            
            odds_dict['home_win_prob'] = (1/odds_dict['avg_home_win_odds']) / total_prob
            odds_dict['draw_prob'] = (1/odds_dict['avg_draw_odds']) / total_prob
            odds_dict['away_win_prob'] = (1/odds_dict['avg_away_win_odds']) / total_prob
        
        odds_features.append(odds_dict)
    
    return pd.DataFrame(odds_features)

# --- Tính toán form gần đây của đội ---
def calculate_team_form(matches, n_previous_matches=5):
    """
    Tính toán form gần đây của các đội dựa trên n trận đấu gần nhất
    """
    matches = matches.sort_values('date')
    form_features = []
    
    for idx, match in matches.iterrows():
        home_team = match['home_team_api_id']
        away_team = match['away_team_api_id']
        match_date = match['date']
        
        # Tính form cho đội chủ nhà
        home_previous_matches = matches[
            (matches['date'] < match_date) &
            ((matches['home_team_api_id'] == home_team) | (matches['away_team_api_id'] == home_team))
        ].tail(n_previous_matches)
        
        home_form = {
            'match_id': match['match_id'],
            'home_team_points': 0,
            'home_team_goals_scored': 0,
            'home_team_goals_conceded': 0,
            'home_team_wins': 0,
            'home_team_draws': 0,
            'home_team_losses': 0
        }
        
        for _, prev_match in home_previous_matches.iterrows():
            if prev_match['home_team_api_id'] == home_team:
                home_form['home_team_goals_scored'] += prev_match['home_team_goal']
                home_form['home_team_goals_conceded'] += prev_match['away_team_goal']
                if prev_match['home_team_goal'] > prev_match['away_team_goal']:
                    home_form['home_team_points'] += 3
                    home_form['home_team_wins'] += 1
                elif prev_match['home_team_goal'] == prev_match['away_team_goal']:
                    home_form['home_team_points'] += 1
                    home_form['home_team_draws'] += 1
                else:
                    home_form['home_team_losses'] += 1
            else:
                home_form['home_team_goals_scored'] += prev_match['away_team_goal']
                home_form['home_team_goals_conceded'] += prev_match['home_team_goal']
                if prev_match['away_team_goal'] > prev_match['home_team_goal']:
                    home_form['home_team_points'] += 3
                    home_form['home_team_wins'] += 1
                elif prev_match['away_team_goal'] == prev_match['home_team_goal']:
                    home_form['home_team_points'] += 1
                    home_form['home_team_draws'] += 1
                else:
                    home_form['home_team_losses'] += 1
        
        # Tính form cho đội khách
        away_previous_matches = matches[
            (matches['date'] < match_date) &
            ((matches['home_team_api_id'] == away_team) | (matches['away_team_api_id'] == away_team))
        ].tail(n_previous_matches)
        
        away_form = {
            'away_team_points': 0,
            'away_team_goals_scored': 0,
            'away_team_goals_conceded': 0,
            'away_team_wins': 0,
            'away_team_draws': 0,
            'away_team_losses': 0
        }
        
        for _, prev_match in away_previous_matches.iterrows():
            if prev_match['home_team_api_id'] == away_team:
                away_form['away_team_goals_scored'] += prev_match['home_team_goal']
                away_form['away_team_goals_conceded'] += prev_match['away_team_goal']
                if prev_match['home_team_goal'] > prev_match['away_team_goal']:
                    away_form['away_team_points'] += 3
                    away_form['away_team_wins'] += 1
                elif prev_match['home_team_goal'] == prev_match['away_team_goal']:
                    away_form['away_team_points'] += 1
                    away_form['away_team_draws'] += 1
                else:
                    away_form['away_team_losses'] += 1
            else:
                away_form['away_team_goals_scored'] += prev_match['away_team_goal']
                away_form['away_team_goals_conceded'] += prev_match['home_team_goal']
                if prev_match['away_team_goal'] > prev_match['home_team_goal']:
                    away_form['away_team_points'] += 3
                    away_form['away_team_wins'] += 1
                elif prev_match['away_team_goal'] == prev_match['home_team_goal']:
                    away_form['away_team_points'] += 1
                    away_form['away_team_draws'] += 1
                else:
                    away_form['away_team_losses'] += 1
        
        # Tính trung bình
        n_home = len(home_previous_matches)
        n_away = len(away_previous_matches)
        
        if n_home > 0:
            home_form['home_team_avg_points'] = home_form['home_team_points'] / n_home
            home_form['home_team_avg_goals_scored'] = home_form['home_team_goals_scored'] / n_home
            home_form['home_team_avg_goals_conceded'] = home_form['home_team_goals_conceded'] / n_home
        else:
            home_form['home_team_avg_points'] = 0
            home_form['home_team_avg_goals_scored'] = 0
            home_form['home_team_avg_goals_conceded'] = 0
            
        if n_away > 0:
            away_form['away_team_avg_points'] = away_form['away_team_points'] / n_away
            away_form['away_team_avg_goals_scored'] = away_form['away_team_goals_scored'] / n_away
            away_form['away_team_avg_goals_conceded'] = away_form['away_team_goals_conceded'] / n_away
        else:
            away_form['away_team_avg_points'] = 0
            away_form['away_team_avg_goals_scored'] = 0
            away_form['away_team_avg_goals_conceded'] = 0
        
        form_features.append({**home_form, **away_form})
    
    return pd.DataFrame(form_features)

# --- Chuẩn bị dữ liệu cho model dự đoán tỉ số ---
def prepare_score_data(matches):
    feature_columns = [
        'h2h_home_wins', 'h2h_avg_home_goals', 'h2h_avg_away_goals',
        'home_team_rank', 'away_team_rank', 'rank_diff',
        'home_win_prob', 'draw_prob', 'away_win_prob',
        'home_team_avg_points', 'away_team_avg_points',
        'home_team_avg_goals_scored', 'home_team_avg_goals_conceded',
        'away_team_avg_goals_scored', 'away_team_avg_goals_conceded'
    ]
    available_features = [col for col in feature_columns if col in matches.columns]
    X = matches[available_features]
    y_home = matches['home_team_goal']
    y_away = matches['away_team_goal']
    imputer = SimpleImputer(strategy='mean')
    X = pd.DataFrame(imputer.fit_transform(X), columns=available_features)
    scaler = StandardScaler()
    X = pd.DataFrame(scaler.fit_transform(X), columns=available_features)
    return X, y_home, y_away

# --- Train và đánh giá model dự đoán tỉ số ---
def train_and_evaluate_score_model(X, y_home, y_away):
    X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
        X, y_home, y_away, test_size=0.2, random_state=42)

    # Dùng PoissonRegressor nếu dữ liệu không có giá trị âm, nếu không thì dùng LinearRegression
    try:
        home_model = PoissonRegressor(max_iter=300).fit(X_train, y_home_train)
        away_model = PoissonRegressor(max_iter=300).fit(X_train, y_away_train)
    except Exception:
        home_model = LinearRegression().fit(X_train, y_home_train)
        away_model = LinearRegression().fit(X_train, y_away_train)

    y_home_pred = home_model.predict(X_test)
    y_away_pred = away_model.predict(X_test)

    print("\nKết quả dự đoán số bàn thắng:")
    print(f"Home goals - MAE: {mean_absolute_error(y_home_test, y_home_pred):.4f}, RMSE: {np.sqrt(mean_squared_error(y_home_test, y_home_pred)):.4f}")
    print(f"Away goals - MAE: {mean_absolute_error(y_away_test, y_away_pred):.4f}, RMSE: {np.sqrt(mean_squared_error(y_away_test, y_away_pred)):.4f}")

    return home_model, away_model

# --- Hàm chính ---
def main():
    try:
        print("Bắt đầu chạy model...")
        countries, matches, leagues, teams = load_data()
        print("Đang lọc giải đấu lớn...")
        leagues, matches = filter_main_leagues(countries, leagues, matches)
        print(f"Số trận sau khi lọc: {len(matches)}")
        print("Đang tính toán các feature...")
        matches = add_total_goal(matches)
        matches = add_result_label(matches)
        print("Đang tính toán H2H features...")
        h2h_features = calculate_h2h_features(matches)
        print("Đang tính toán standings features...")
        standings_features = calculate_league_standings(matches)
        print("Đang tính toán odds features...")
        odds_features = process_odds_features(matches)
        print("Đang tính toán form features...")
        form_features = calculate_team_form(matches)
        print("Đang merge các feature...")
        matches = matches.merge(h2h_features, on='match_id', how='left')
        matches = matches.merge(standings_features, on='match_id', how='left')
        matches = matches.merge(odds_features, on='match_id', how='left')
        matches = matches.merge(form_features, on='match_id', how='left')
        print("\nCác feature mới đã được thêm vào:")
        print(matches[['h2h_home_wins', 'home_team_rank', 'away_team_rank', 
                      'home_win_prob', 'home_team_avg_points', 'away_team_avg_points']].head())
        print("\nĐang chuẩn bị dữ liệu cho model dự đoán tỉ số...")
        X, y_home, y_away = prepare_score_data(matches)
        print(f"Shape của dữ liệu: X={X.shape}, y_home={y_home.shape}, y_away={y_away.shape}")
        print("\nĐang train và đánh giá model dự đoán tỉ số...")
        home_model, away_model = train_and_evaluate_score_model(X, y_home, y_away)
        print("\nĐang lưu model...")
        joblib.dump(home_model, 'poisson_home_model.pkl')
        joblib.dump(away_model, 'poisson_away_model.pkl')
        print("Hoàn thành!")
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")
        raise e

if __name__ == "__main__":
    main()
 