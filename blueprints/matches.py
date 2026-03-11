"""
Matches Blueprint - Danh sách trận đấu, fixtures, chi tiết trận.
"""
import json
import traceback
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Blueprint, request, jsonify, render_template

from config import FIXTURES_LEAGUES, SOFASCORE_TOURNAMENT_IDS, POPULAR_LEAGUES, LEAGUE_LOGOS, APP_TZ, SOFASCORE_SEASON_IDS
from api_client import sofascore_get, get_season_id, get_match_incidents, sofascore_get_binary
from cache_utils import (
    load_from_cache, save_to_cache, is_cache_valid,
    get_cache_file, get_permanent_cache_file,
    cache_team_logo, get_cached_team_logo
)

bp = Blueprint('matches', __name__)


def _cache_team_logo(team_id, logo_url=None):
    cache_team_logo(team_id, logo_url, sofascore_get_binary_func=sofascore_get_binary)


@bp.route('/get_fixtures', methods=['POST'])
def get_fixtures():
    """Lấy danh sách trận đấu theo ngày."""
    date = request.json.get('date')
    if not date:
        return jsonify({'error': 'Date is required'}), 400

    key = f"{date}_fast"
    data_type = "fixtures"
    if is_cache_valid(key, data_type):
        data = load_from_cache(key, data_type)
        if data and data.get("response"):
            return jsonify(data)

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.now(APP_TZ).date()
        delta_days = abs((target_date - today).days)
        is_future = target_date > today
        is_today = target_date == today
        max_pages = min(15, max(3, 3 + delta_days))

        def fetch_league_events(league_id):
            tournament_id = SOFASCORE_TOURNAMENT_IDS.get(league_id, league_id)
            season_id = get_season_id(league_id)
            # Với "hôm nay": ưu tiên lấy scheduled/upcoming events thay vì last-matches
            # để tránh kéo quá nhiều trận quá khứ và dễ dính rate limit.
            if is_today:
                endpoint = "/tournaments/get-scheduled-events"
                params = {"tournamentId": tournament_id, "seasonId": season_id}
            elif is_future:
                endpoint = "/tournaments/get-next-matches"
                params = {"tournamentId": tournament_id, "seasonId": season_id}
            else:
                endpoint = "/tournaments/get-last-matches"
                params = {"tournamentId": tournament_id, "seasonId": season_id}

            all_events = []
            for page_index in range(0, max_pages):
                page_params = {**params, "pageIndex": page_index}
                data = sofascore_get(endpoint, page_params)
                if data and "events" in data and data["events"]:
                    page_events = data["events"]
                    all_events.extend(page_events)
                    found_count = sum(1 for e in page_events
                                      if e.get("startTimestamp") and
                                      datetime.fromtimestamp(e.get("startTimestamp", 0), APP_TZ).date() == target_date)
                    if not page_events or (found_count > 0 and page_index >= 2):
                        break
                else:
                    break

            # Fallback: nếu "hôm nay" mà không có data từ scheduled-events, thử next-matches
            # (một số giải có thể không trả scheduled-events đầy đủ).
            if is_today and not all_events:
                fb_endpoint = "/tournaments/get-next-matches"
                fb_params = {"tournamentId": tournament_id, "seasonId": season_id}
                for page_index in range(0, min(5, max_pages)):
                    page_params = {**fb_params, "pageIndex": page_index}
                    data = sofascore_get(fb_endpoint, page_params)
                    if data and "events" in data and data["events"]:
                        page_events = data["events"]
                        all_events.extend(page_events)
                        found_count = sum(
                            1
                            for e in page_events
                            if e.get("startTimestamp")
                            and datetime.fromtimestamp(e.get("startTimestamp", 0), APP_TZ).date()
                            == target_date
                        )
                        if not page_events or (found_count > 0 and page_index >= 1):
                            break
                    else:
                        break
            return league_id, all_events

        converted_matches = []
        with ThreadPoolExecutor(max_workers=len(FIXTURES_LEAGUES)) as ex:
            futures = [ex.submit(fetch_league_events, lid) for lid in FIXTURES_LEAGUES]
            for fut in as_completed(futures):
                league_id, all_events = fut.result()
                if not all_events:
                    continue
                for event in all_events:
                    ts = event.get("startTimestamp", 0) or 0
                    if not ts:
                        continue
                    # Sofascore startTimestamp là UTC-based. Nếu chỉ dùng APP_TZ (VN) sẽ
                    # dễ miss các trận đá buổi tối châu Âu (UTC date khác VN date).
                    event_date_local = datetime.fromtimestamp(ts, APP_TZ).date()
                    event_date_utc = datetime.fromtimestamp(ts, timezone.utc).date()
                    if event_date_local != target_date and event_date_utc != target_date:
                        continue
                    home_team = event.get("homeTeam", {})
                    away_team = event.get("awayTeam", {})
                    h_id, a_id = home_team.get("id"), away_team.get("id")
                    # Chỉ gọi API logo khi chưa có trong cache/static (tránh request trùng)
                    for tid, img_url in ((h_id, home_team.get("imageUrl")), (a_id, away_team.get("imageUrl"))):
                        if not tid:
                            continue
                        cur = get_cached_team_logo(tid)
                        if not cur or not cur.startswith("/static/"):
                            _cache_team_logo(tid, img_url)
                    home_logo = get_cached_team_logo(h_id) or home_team.get("imageUrl")
                    away_logo = get_cached_team_logo(a_id) or away_team.get("imageUrl")
                    converted_match = {
                        "fixture": {
                            "id": event.get("id"),
                            "date": datetime.fromtimestamp(event.get("startTimestamp", 0)).isoformat(),
                            "status": {
                                "short": event.get("status", {}).get("code", "NS"),
                                "long": event.get("status", {}).get("description", "Not Started")
                            }
                        },
                        "teams": {
                            "home": {"id": home_team.get("id"), "name": home_team.get("name", "Home"), "logo": home_logo or "/static/images/teams/default.png"},
                            "away": {"id": away_team.get("id"), "name": away_team.get("name", "Away"), "logo": away_logo or "/static/images/teams/default.png"}
                        },
                        "goals": {
                            "home": event.get("homeScore", {}).get("normaltime") or event.get("homeScore", {}).get("current"),
                            "away": event.get("awayScore", {}).get("normaltime") or event.get("awayScore", {}).get("current")
                        },
                        "league": {"id": league_id, "name": POPULAR_LEAGUES.get(league_id, "League"), "logo": LEAGUE_LOGOS.get(league_id, "")}
                    }
                    converted_matches.append(converted_match)

        converted_matches.sort(key=lambda m: m.get("fixture", {}).get("date", ""))
        response_data = {"response": converted_matches}
        if len(converted_matches) > 0 or max_pages >= 10:
            save_to_cache(key, data_type, response_data)
        return jsonify(response_data)
    except Exception as e:
        print(f"[FIXTURES] Error: {e}")
        traceback.print_exc()
        return jsonify({'response': []})


@bp.route('/api/match/<int:match_id>/incidents', methods=['GET'])
def api_match_incidents(match_id):
    """Lấy incidents của trận đấu."""
    incidents = get_match_incidents(match_id)
    return jsonify({"incidents": incidents})


@bp.route('/match/<match_id>')
def match_detail(match_id):
    """Trang chi tiết trận đấu."""
    return render_template(f'matches/{match_id}.html')


@bp.route('/api/fixtures/<int:league_id>')
def api_fixtures(league_id):
    """API fixtures theo league."""
    try:
        sofascore_tournament_id = SOFASCORE_TOURNAMENT_IDS.get(league_id, league_id)
        sofascore_season_id = SOFASCORE_SEASON_IDS.get(league_id, 76986)
        endpoints_to_try = [
            ("/tournaments/get-featured-events", {"tournamentId": sofascore_tournament_id, "seasonId": sofascore_season_id}),
            ("/tournaments/get-next-matches", {"tournamentId": sofascore_tournament_id, "seasonId": sofascore_season_id}),
            ("/tournaments/get-scheduled-events", {"tournamentId": sofascore_tournament_id, "seasonId": sofascore_season_id}),
        ]
        for endpoint, params in endpoints_to_try:
            data = sofascore_get(endpoint, params)
            if data and 'events' in data:
                for e in data['events']:
                    for team_key in ('homeTeam', 'awayTeam'):
                        t = e.get(team_key, {}) or {}
                        tid, img = t.get('id'), t.get('imageUrl')
                        if not tid:
                            continue
                        cur = get_cached_team_logo(tid)
                        if not cur or not cur.startswith("/static/"):
                            _cache_team_logo(tid, img)
                upcoming = [e for e in data['events'] if e.get('status', {}).get('type') not in ['finished', 'ended']]
                if upcoming:
                    for e in upcoming:
                        home, away = e.get('homeTeam', {}), e.get('awayTeam', {})
                        home['imageUrl'] = get_cached_team_logo(home.get('id')) or home.get('imageUrl')
                        away['imageUrl'] = get_cached_team_logo(away.get('id')) or away.get('imageUrl')
                    return jsonify(upcoming)
                elif data['events']:
                    for e in data['events']:
                        home, away = e.get('homeTeam', {}), e.get('awayTeam', {})
                        home['imageUrl'] = get_cached_team_logo(home.get('id')) or home.get('imageUrl')
                        away['imageUrl'] = get_cached_team_logo(away.get('id')) or away.get('imageUrl')
                    return jsonify(data['events'][:10])
        return jsonify([])
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@bp.route('/api/featured_matches')
def api_featured_matches():
    """Featured matches từ cache."""
    cf = get_cache_file('featured_matches', 'featured')
    pf = get_permanent_cache_file('featured_matches', 'featured')
    if cf.exists():
        with open(cf, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    if pf.exists():
        with open(pf, 'r', encoding='utf-8') as f:
            data = json.load(f)
            save_to_cache('featured_matches', 'featured', data)
            return jsonify(data)
    return jsonify({'past': [], 'next_priority': []})


@bp.route('/delete_match/<int:fixture_id>', methods=['POST'])
def delete_match(fixture_id):
    return jsonify({"success": True})
