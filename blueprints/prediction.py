"""
Prediction Blueprint - Dự đoán kết quả trận đấu.
"""
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
import traceback
from sklearn.preprocessing import normalize

from config import POPULAR_LEAGUES, FIXTURES_LEAGUES, APP_TZ
from api_client import get_match_by_id, sofascore_get_binary
from cache_utils import (
    cache_team_logo, get_cached_team_logo, save_prediction_history, load_prediction_history,
    _fallback_sofascore_team_logo_url
)
from models.prediction_models import logistic_model
from models.feature_preparation import prepare_logistic_features
from utils import normalize_status

bp = Blueprint('prediction', __name__)


def _cache_team_logo(team_id, logo_url=None):
    """Cache team logo using api_client binary fetcher."""
    cache_team_logo(team_id, logo_url, sofascore_get_binary_func=sofascore_get_binary)


@bp.route('/prediction')
def prediction_page():
    """Trang dự đoán."""
    allowed = {lid: POPULAR_LEAGUES[lid] for lid in FIXTURES_LEAGUES if lid in POPULAR_LEAGUES}
    return render_template('prediction.html', leagues=allowed, active_tab='prediction')


@bp.route('/predict', methods=['POST'])
def predict():
    """API dự đoán kết quả trận đấu."""
    try:
        data = request.json
        fixture_id = data.get('fixture_id') or data.get('match', {}).get('id')
        match = data.get('match')

        if not match:
            if not fixture_id:
                return jsonify({'error': 'Either fixture_id or match object is required'}), 400

            history = load_prediction_history()
            for record in history:
                if str(record.get('fixture_id')) == str(fixture_id):
                    ui_match = {
                        "fixture": {
                            "id": record.get("fixture_id"),
                            "date": datetime.fromtimestamp(
                                int(record.get("date", 0) or 0), APP_TZ
                            ).isoformat() if record.get("date") else None,
                        },
                        "teams": {
                            "home": {"name": record.get("home_team"), "logo": record.get("home_team_logo")},
                            "away": {"name": record.get("away_team"), "logo": record.get("away_team_logo")},
                        },
                        "league": {"name": record.get("league_name")},
                    }
                    return jsonify({
                        'home_win_prob': record['home_win_prob'],
                        'draw_prob': record['draw_prob'],
                        'away_win_prob': record['away_win_prob'],
                        'real_home_goals': record.get('real_home_goals'),
                        'real_away_goals': record.get('real_away_goals'),
                        'status': record.get('status'),
                        'home_team': record.get('home_team'),
                        'away_team': record.get('away_team'),
                        'home_team_logo': record.get('home_team_logo'),
                        'away_team_logo': record.get('away_team_logo'),
                        'date': record.get('date'),
                        'league_name': record.get('league_name'),
                        'match': ui_match
                    })

            match = get_match_by_id(fixture_id)
            if not match:
                return jsonify({'error': 'Match not found'}), 404
        else:
            fixture_id = match.get('id')

        logistic_features = prepare_logistic_features(match)
        if logistic_features is None:
            return jsonify({'error': 'Không thể lấy đủ dữ liệu thống kê để dự đoán. Vui lòng thử lại sau.'}), 500

        # CRITICAL: Normalize features (L2 norm) - model was trained on normalized data
        # Without this, predictions are completely wrong (home team always loses)
        logistic_features_normalized = normalize([logistic_features], norm='l2', axis=1)[0]
        print(f"[PREDICT] Normalized features: {logistic_features_normalized}")

        pred_proba = logistic_model.predict_proba([logistic_features_normalized])[0]
        classes = logistic_model.classes_
        prob_by_class = {int(c): float(p) for c, p in zip(classes, pred_proba)}
        home_win_prob = prob_by_class.get(1, 0.0)
        draw_prob = prob_by_class.get(0, 0.0)
        away_win_prob = prob_by_class.get(-1, 0.0)
        pred_proba = [home_win_prob, draw_prob, away_win_prob]

        home_score = match.get('homeScore', {})
        away_score = match.get('awayScore', {})
        status_obj = match.get('status', {})
        real_home_goals = home_score.get('normaltime') if isinstance(home_score, dict) else home_score
        real_away_goals = away_score.get('normaltime') if isinstance(away_score, dict) else away_score
        status = status_obj.get('type', 'NS') if isinstance(status_obj, dict) else status_obj
        status = normalize_status(status)

        if real_home_goals is None or real_away_goals is None:
            real_home_goals = None
            real_away_goals = None
            status = 'NS'

        home_team = match.get('homeTeam', {}) or {}
        away_team = match.get('awayTeam', {}) or {}
        home_team_name = home_team.get('name', 'Unknown')
        away_team_name = away_team.get('name', 'Unknown')
        home_team_id = home_team.get("id")
        away_team_id = away_team.get("id")

        home_logo = None
        away_logo = None
        if home_team_id:
            _cache_team_logo(home_team_id, home_team.get("imageUrl"))
            home_logo = get_cached_team_logo(home_team_id) or home_team.get("imageUrl") or _fallback_sofascore_team_logo_url(home_team_id)
        if away_team_id:
            _cache_team_logo(away_team_id, away_team.get("imageUrl"))
            away_logo = get_cached_team_logo(away_team_id) or away_team.get("imageUrl") or _fallback_sofascore_team_logo_url(away_team_id)

        match_for_ui = {
            "fixture": {
                "id": fixture_id,
                "date": datetime.fromtimestamp(match.get("startTimestamp", 0) or 0, APP_TZ).isoformat()
                if match.get("startTimestamp") else None,
            },
            "teams": {
                "home": {"id": home_team_id, "name": home_team_name, "logo": home_logo},
                "away": {"id": away_team_id, "name": away_team_name, "logo": away_logo},
            },
            "league": {
                "id": match.get("tournament", {}).get("uniqueTournament", {}).get("id"),
                "name": match.get("tournament", {}).get("uniqueTournament", {}).get("name", ""),
            },
        }

        save_prediction_history({
            'fixture_id': fixture_id,
            'home_team': home_team_name,
            'away_team': away_team_name,
            'home_team_logo': home_logo or '',
            'away_team_logo': away_logo or '',
            'home_team_id': home_team_id,
            'away_team_id': away_team_id,
            'date': match.get('startTimestamp', ''),
            'league_name': match.get('tournament', {}).get('uniqueTournament', {}).get('name', ''),
            'home_win_prob': float(pred_proba[0]),
            'draw_prob': float(pred_proba[1]),
            'away_win_prob': float(pred_proba[2]),
            'real_home_goals': real_home_goals,
            'real_away_goals': real_away_goals,
            'status': status,
        })

        return jsonify({
            'home_win_prob': float(pred_proba[0]),
            'draw_prob': float(pred_proba[1]),
            'away_win_prob': float(pred_proba[2]),
            'real_home_goals': real_home_goals,
            'real_away_goals': real_away_goals,
            'status': status,
            'home_team': home_team_name,
            'away_team': away_team_name,
            'home_team_logo': home_logo or '',
            'away_team_logo': away_logo or '',
            'home_team_id': home_team_id,
            'away_team_id': away_team_id,
            'date': match.get('startTimestamp', ''),
            'league_name': match.get('tournament', {}).get('uniqueTournament', {}).get('name', ''),
            'match': match_for_ui
        })
    except Exception as e:
        print("Lỗi khi dự đoán:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
