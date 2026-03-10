"""
Prediction History Blueprint - Lịch sử dự đoán.
"""
from flask import Blueprint, render_template, jsonify
from datetime import datetime

from config import POPULAR_LEAGUES, APP_TZ
from api_client import get_match_by_id, sofascore_get_binary
from cache_utils import (
    load_prediction_history, save_prediction_history_list,
    cache_team_logo, get_cached_team_logo, _fallback_sofascore_team_logo_url
)
from utils import normalize_status

bp = Blueprint('prediction_history', __name__)

# Số trận tối đa cập nhật kết quả thực tế mỗi lần gọi API (tránh timeout)
MAX_UPDATE_PER_REQUEST = 20


def _cache_team_logo(team_id, logo_url=None):
    cache_team_logo(team_id, logo_url, sofascore_get_binary_func=sofascore_get_binary)


def _needs_result_update(record, now_ts):
    """True nếu trận đã tới/sau giờ đá và chưa có kết quả thực tế."""
    match_ts = record.get("date")
    if match_ts is None or match_ts == "":
        return False
    try:
        match_ts = int(match_ts)
    except (TypeError, ValueError):
        return False
    if now_ts < match_ts:
        return False
    if record.get("real_home_goals") is not None and record.get("status") not in (None, "NS", "inprogress"):
        return False
    return True


@bp.route('/prediction_history')
def prediction_history_page():
    """Trang lịch sử dự đoán."""
    return render_template('prediction_history.html', active_tab='prediction_history', leagues=POPULAR_LEAGUES)


@bp.route('/get_prediction_history', methods=['GET'])
def get_prediction_history():
    """API lấy lịch sử dự đoán. Tự động cập nhật kết quả thực tế khi thời gian >= giờ trận."""
    history = load_prediction_history()
    updated = False
    now_ts = int(datetime.now(APP_TZ).timestamp())

    # 1) Cập nhật kết quả thực tế cho các trận đã tới/sau giờ đá mà chưa có kết quả
    to_update = [r for r in history if _needs_result_update(r, now_ts)]
    for record in to_update[:MAX_UPDATE_PER_REQUEST]:
        match = get_match_by_id(record.get("fixture_id"))
        if match:
            home_score = match.get("homeScore", {})
            away_score = match.get("awayScore", {})
            status_obj = match.get("status", {})
            record["real_home_goals"] = home_score.get("normaltime") if isinstance(home_score, dict) else home_score
            record["real_away_goals"] = away_score.get("normaltime") if isinstance(away_score, dict) else away_score
            record["status"] = normalize_status(status_obj.get("type") if isinstance(status_obj, dict) else status_obj)
            updated = True

    # 2) Bổ sung logo cho 10 bản ghi đầu (nếu thiếu)
    for record in history[:10]:
        try:
            home_id = record.get("home_team_id")
            away_id = record.get("away_team_id")
            if home_id and (not record.get("home_team_logo") or str(record.get("home_team_logo")).strip() == ""):
                _cache_team_logo(home_id)
                record["home_team_logo"] = get_cached_team_logo(home_id) or _fallback_sofascore_team_logo_url(home_id)
                updated = True
            if away_id and (not record.get("away_team_logo") or str(record.get("away_team_logo")).strip() == ""):
                _cache_team_logo(away_id)
                record["away_team_logo"] = get_cached_team_logo(away_id) or _fallback_sofascore_team_logo_url(away_id)
                updated = True
        except Exception:
            pass

    if updated:
        save_prediction_history_list(history)
    return jsonify(history)
