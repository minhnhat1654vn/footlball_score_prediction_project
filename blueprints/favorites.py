"""
Favorites Blueprint - Đội bóng yêu thích, featured teams, cache team stats.
"""
import time
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

from config import LEAGUE_TEAMS
from api_client import fetch_team_stats, get_team_id_from_name, sofascore_get_binary
from cache_utils import (
    load_favorites_teams,
    save_favorites_teams,
    save_to_cache,
    cache_team_logo,
    get_cached_team_logo,
    get_cache_file,
    get_permanent_cache_file,
    _fallback_sofascore_team_logo_url,
)

bp = Blueprint("favorites", __name__)


def _cache_team_logo(team_id, logo_url=None):
    cache_team_logo(team_id, logo_url, sofascore_get_binary_func=sofascore_get_binary)


def _require_login():
    """
    Nếu chưa đăng nhập, chuyển sang trang login.
    Dùng cho các POST request cần ghi favorites.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login", next=request.url))
    return None


@bp.route("/favorites", methods=["GET", "POST"])
def favorites():
    """Trang và xử lý đội bóng yêu thích (theo từng user)."""
    user_id = session.get("user_id")
    # Khi chưa đăng nhập: vẫn render trang, nhưng không có danh sách favorites
    favorite_teams = load_favorites_teams(user_id) if user_id else []

    if request.method == "POST":
        # POST luôn yêu cầu login
        redirect_resp = _require_login()
        if redirect_resp:
            return redirect_resp
        user_id = session.get("user_id")
        favorite_teams = load_favorites_teams(user_id)

        action = request.form.get("action")
        if action == "add":
            selected_league = request.form.get("league")
            selected_teams = request.form.getlist("selected_teams")
            if selected_league and selected_teams:
                teams = LEAGUE_TEAMS.get(selected_league, [])
                for team in teams:
                    if team["name"] in selected_teams:
                        if not any(
                            t["name"] == team["name"] and t["league_id"] == team["league_id"]
                            for t in favorite_teams
                        ):
                            team_info = team.copy()
                            team_info["stats"] = fetch_team_stats(team["name"], team["league_id"])
                            team_id = get_team_id_from_name(team["name"], team.get("league_id"))
                            team_info["team_id"] = team_id
                            if team_id:
                                _cache_team_logo(team_id)
                                team_info["logo_url"] = (
                                    get_cached_team_logo(team_id)
                                    or _fallback_sofascore_team_logo_url(team_id)
                                )
                            favorite_teams.append(team_info)
                save_favorites_teams(favorite_teams, user_id)
        elif action == "remove":
            team_name = request.form.get("team_name")
            if team_name:
                favorite_teams = [t for t in favorite_teams if t["name"] != team_name]
                save_favorites_teams(favorite_teams, user_id)

    selected_league = request.form.get("league", "")
    teams = LEAGUE_TEAMS.get(selected_league, [])

    updated = False
    for team in favorite_teams:
        stats = team.get("stats", {})
        if not stats or stats.get("rank") in [None, "N/A"] or stats.get("points", 0) == 0:
            team["stats"] = fetch_team_stats(team["name"], team["league_id"])
            updated = True
        team_id = team.get("team_id") or get_team_id_from_name(
            team.get("name"), team.get("league_id")
        )
        if team_id and not team.get("team_id"):
            team["team_id"] = team_id
            updated = True
        if team_id and (not team.get("logo_url") or str(team.get("logo_url")).strip() == ""):
            _cache_team_logo(team_id)
            team["logo_url"] = get_cached_team_logo(team_id) or _fallback_sofascore_team_logo_url(
                team_id
            )
            updated = True

    if updated and user_id:
        save_favorites_teams(favorite_teams, user_id)

    return render_template(
        "favorites.html",
        selected_league=selected_league,
        teams=teams,
        selected_teams=favorite_teams,
        active_tab="favorites",
    )


def cache_all_teams_stats():
    """Lưu thống kê tất cả đội bóng vào cache."""
    from datetime import datetime
    current_season = datetime.now().year
    for league_key, teams in LEAGUE_TEAMS.items():
        for team in teams:
            try:
                stats = fetch_team_stats(team['name'], team['league_id'])
                cache_key = f"team_stats_{team['name']}_{team['league_id']}_{current_season}"
                save_to_cache(cache_key, "team_stats", stats)
                time.sleep(1)
            except Exception as e:
                print(f"Lỗi khi lưu thống kê cho {team['name']}: {str(e)}")


@bp.route('/cache_team_stats')
def trigger_cache_team_stats():
    """API trigger cache thống kê đội bóng."""
    try:
        cache_all_teams_stats()
        return jsonify({"status": "success", "message": "Đã lưu thống kê đội bóng vào cache"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route('/api/featured_teams')
def api_featured_teams():
    """API featured teams từ cache."""
    cf = get_cache_file('featured_teams', 'featured')
    pf = get_permanent_cache_file('featured_teams', 'featured')
    if cf.exists():
        import json
        with open(cf, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    if pf.exists():
        import json
        with open(pf, 'r', encoding='utf-8') as f:
            data = json.load(f)
            save_to_cache('featured_teams', 'featured', data)
            return jsonify(data)
    return jsonify([])
