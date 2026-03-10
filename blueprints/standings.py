"""
Standings Blueprint - Bảng xếp hạng, thống kê đội, logo, H2H, odds.
"""
import json
import traceback
from flask import Blueprint, request, jsonify, send_file, Response, redirect

from config import LOGO_DIR, SOFASCORE_SEASON_IDS, SOFASCORE_TOURNAMENT_IDS
from api_client import (
    get_season_id, get_or_fetch_standings, get_or_fetch_team_stats, get_or_fetch_h2h,
    sofascore_get, sofascore_get_binary
)
from cache_utils import (
    get_cache_file, get_permanent_cache_file, load_from_cache, save_to_cache,
    is_cache_valid, invalidate_cache, cache_team_logo, get_cached_team_logo, _fallback_sofascore_team_logo_url
)

bp = Blueprint('standings', __name__)


def _cache_team_logo(team_id, logo_url=None):
    cache_team_logo(team_id, logo_url, sofascore_get_binary_func=sofascore_get_binary)


@bp.route('/teams/get-logo', methods=['GET'])
def teams_get_logo_proxy():
    """Proxy logo đội bóng. GET /teams/get-logo?teamId=42"""
    team_id = request.args.get("teamId") or request.args.get("team_id") or request.args.get("id")
    if not team_id:
        return jsonify({"error": "teamId is required"}), 400
    local_path = LOGO_DIR / f"{team_id}.png"
    if local_path.exists():
        return send_file(local_path, mimetype="image/png", conditional=True)
    result = sofascore_get_binary("/teams/get-logo", {"teamId": team_id})
    if result:
        content, content_type = result
        try:
            LOGO_DIR.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(content)
            save_to_cache(str(team_id), "team_logo", {"logo_url": f"/static/images/team_logos/{team_id}.png"})
        except Exception:
            pass
        return Response(content, mimetype=content_type or "image/png")
    _cache_team_logo(team_id)
    if local_path.exists():
        return send_file(local_path, mimetype="image/png", conditional=True)
    return redirect(_fallback_sofascore_team_logo_url(team_id), code=302)


@bp.route('/get_team_stats', methods=['POST'])
def get_team_stats():
    """Lấy thống kê đội bóng."""
    team_id = request.json.get('team_id')
    league_id = request.json.get('league_id')
    season = request.json.get('season')
    if not all([team_id, league_id, season]):
        return jsonify({'error': 'Missing required parameters'}), 400
    key = f"{team_id}_{league_id}_{season}"
    data_type = "team_stats"
    if is_cache_valid(key, data_type):
        data = load_from_cache(key, data_type)
        return jsonify(data)
    data = get_or_fetch_team_stats(team_id, league_id, season)
    return jsonify(data if data else {'error': 'Unable to fetch team stats'})


@bp.route('/get_standings', methods=['POST'])
def get_standings():
    """Lấy bảng xếp hạng."""
    league_id = request.json.get('league_id')
    season = request.json.get('season')
    if not all([league_id, season]):
        return jsonify({'error': 'Missing required parameters'}), 400
    key = f"{league_id}_{season}"
    data_type = "standings"
    if is_cache_valid(key, data_type):
        data = load_from_cache(key, data_type)
        return jsonify(data)
    data = get_or_fetch_standings(league_id, season)
    return jsonify(data if data else {'error': 'Unable to fetch standings'})


@bp.route('/get_h2h', methods=['POST'])
def get_h2h():
    """Lấy lịch sử đối đầu."""
    home_id = request.json.get('home_id')
    away_id = request.json.get('away_id')
    if not all([home_id, away_id]):
        return jsonify({'error': 'Missing required parameters'}), 400
    key = f"{home_id}_{away_id}"
    data_type = "h2h"
    if is_cache_valid(key, data_type):
        data = load_from_cache(key, data_type)
        return jsonify(data)
    data = get_or_fetch_h2h(home_id, away_id)
    return jsonify(data if data else {'error': 'Unable to fetch h2h'})


@bp.route('/get_odds', methods=['POST'])
def get_odds():
    """Lấy tỷ lệ cược (placeholder)."""
    fixture_id = request.json.get('fixture_id')
    if not fixture_id:
        return jsonify({'error': 'Missing fixture_id'}), 400
    key = str(fixture_id)
    data_type = "odds"
    if is_cache_valid(key, data_type):
        data = load_from_cache(key, data_type)
        return jsonify(data)
    return jsonify({'response': []})


@bp.route('/api/standings/<int:league_id>')
def api_standings(league_id):
    """API bảng xếp hạng theo league. Query ?refresh=1 để bỏ qua cache và lấy dữ liệu mới từ API."""
    season = get_season_id(league_id)
    key = f"{league_id}_{season}"
    force_refresh = request.args.get("refresh") in ("1", "true", "yes")

    def _inject_team_logos(payload):
        if not payload or "standings" not in payload:
            return payload
        try:
            for row in payload["standings"][0]["rows"]:
                team = row.get("team", {}) or {}
                tid = team.get("id")
                if tid:
                    _cache_team_logo(tid, team.get("imageUrl"))
                    team["imageUrl"] = get_cached_team_logo(tid) or team.get("imageUrl")
        except (KeyError, IndexError, TypeError):
            pass
        return payload

    if force_refresh:
        invalidate_cache(key, "standings")

    cache_file = get_cache_file(key, "standings")
    if not force_refresh and cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached = json.load(f)
            return jsonify(_inject_team_logos(cached))
    data = get_or_fetch_standings(league_id, season)
    data = _inject_team_logos(data)
    return jsonify(data if data else {'error': 'Unable to fetch standings'})


@bp.route('/api/team/<int:team_id>/stats')
def api_team_stats(team_id):
    """API thống kê đội."""
    try:
        league_id = request.args.get('league', 39, type=int)
        season = request.args.get('season', 2025, type=int)
        stats_data = get_or_fetch_team_stats(team_id, league_id, season)
        if stats_data:
            standings_data = get_or_fetch_standings(league_id, season)
            if standings_data and 'standings' in standings_data:
                try:
                    rows = standings_data['standings'][0]['rows']
                    for row in rows:
                        if row.get('team', {}).get('id') == team_id:
                            if 'statistics' in stats_data:
                                stats_data['statistics']['wins'] = row.get('wins', 0)
                                stats_data['statistics']['draws'] = row.get('draws', 0)
                                stats_data['statistics']['losses'] = row.get('losses', 0)
                            break
                except (KeyError, IndexError, TypeError):
                    pass
            return jsonify(stats_data)
        return jsonify({"error": "Team stats not found"}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@bp.route('/api/team/search')
def api_team_search():
    """API tìm kiếm đội bóng."""
    try:
        team_name = request.args.get('name', '')
        if not team_name:
            return jsonify({"error": "Team name is required"}), 400
        data = sofascore_get("/teams/search", {"name": team_name})
        return jsonify(data) if data else (jsonify({"error": "Team not found"}), 404)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
