"""
Cache utilities module for Football Score Prediction application.
Handles all caching operations including team logos, prediction history, and favorites.
"""
import json
import os
import shutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
from config import CACHE_DIR, PERMANENT_CACHE_DIR, LOGO_DIR, SOFASCORE_HEADERS

# Prediction history file paths
HISTORY_FILE_CACHE = CACHE_DIR / "prediction_history.json"
HISTORY_FILE_PERMANENT = PERMANENT_CACHE_DIR / "prediction_history.json"

# Favorites file paths (legacy - dùng khi chưa có user_id)
FAVORITES_FILE_CACHE = CACHE_DIR / "favorites_teams.json"
FAVORITES_FILE_PERMANENT = PERMANENT_CACHE_DIR / "favorites_teams.json"


def _get_user_favorites_file(user_id=None):
    """
    Trả về (cache_file, permanent_file) cho favorites của user.
    - Nếu user_id None: dùng file chung (giữ tương thích cũ).
    - Nếu có user_id: lưu favorites_teams_<user_id>.json.
    """
    if user_id is None:
        return FAVORITES_FILE_CACHE, FAVORITES_FILE_PERMANENT
    user_suffix = f"favorites_teams_{user_id}.json"
    return CACHE_DIR / user_suffix, PERMANENT_CACHE_DIR / user_suffix


def get_cache_file(key, data_type):
    """Get cache file path for a given key and data type"""
    return CACHE_DIR / f"{key}_{data_type}.json"


def get_permanent_cache_file(key, data_type):
    """Get permanent cache file path for a given key and data type"""
    return PERMANENT_CACHE_DIR / f"{key}_{data_type}.json"


def load_from_cache(key, data_type):
    """Load data from cache"""
    cache_file = get_cache_file(key, data_type)
    print(f"[CACHE] Đọc cache: {cache_file}")
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    permanent_file = get_permanent_cache_file(key, data_type)
    if permanent_file.exists():
        print(f"[CACHE] Đọc permanent cache: {permanent_file}")
        with open(permanent_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            save_to_cache(key, data_type, data)
            return data
    print(f"[CACHE] Không có cache cho key: {key}, data_type: {data_type}")
    return None


def save_to_cache(key, data_type, data):
    """Save data to cache"""
    # Tạo thư mục cache nếu chưa có
    CACHE_DIR.mkdir(exist_ok=True)
    PERMANENT_CACHE_DIR.mkdir(exist_ok=True)
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    
    cache_file = get_cache_file(key, data_type)
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    permanent_file = get_permanent_cache_file(key, data_type)
    with open(permanent_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_cache_valid(key, data_type, max_age_hours=24):
    """Check if cache is still valid"""
    cache_file = get_cache_file(key, data_type)
    if cache_file.exists():
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age.total_seconds() < max_age_hours * 3600:
            return True
    permanent_file = get_permanent_cache_file(key, data_type)
    if permanent_file.exists():
        shutil.copy2(permanent_file, cache_file)
        return True
    return False


def invalidate_cache(key, data_type):
    """Xóa cache cho key và data_type để lần sau sẽ gọi API lấy dữ liệu mới."""
    for f in (get_cache_file(key, data_type), get_permanent_cache_file(key, data_type)):
        if f.exists():
            try:
                f.unlink()
                print(f"[CACHE] Đã xóa cache: {f}")
            except OSError as e:
                print(f"[CACHE] Không xóa được {f}: {e}")


def _fallback_sofascore_team_logo_url(team_id):
    """Public Sofascore image endpoint (works without RapidAPI key)"""
    return f"https://api.sofascore.app/api/v1/team/{team_id}/image"


def cache_team_logo(team_id, logo_url=None, sofascore_get_binary_func=None):
    """Cache team logo locally. Bỏ qua nếu đã có file hoặc cache local."""
    if not team_id:
        return
    local_filename = f"{team_id}.png"
    local_path = LOGO_DIR / local_filename
    # Đã có file local → không gọi API, không ghi cache lại
    if local_path.exists():
        return
    # Có cache entry trỏ tới static → coi như đã có, không gọi API
    data = load_from_cache(str(team_id), "team_logo")
    if data and isinstance(data, dict) and str(data.get("logo_url", "")).startswith("/static/"):
        return
    logo_url = logo_url or _fallback_sofascore_team_logo_url(team_id)
    # Download logo chỉ khi chưa có
    try:
        resp = requests.get(
            logo_url,
            timeout=10,
            headers={"User-Agent": SOFASCORE_HEADERS.get("User-Agent", "Mozilla/5.0")},
        )
        if resp.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(resp.content)
        else:
            raise requests.exceptions.RequestException(f"status={resp.status_code}")
    except Exception:
        # Fallback: fetch via RapidAPI binary endpoint (server-side headers)
        if sofascore_get_binary_func:
            try:
                binary = sofascore_get_binary_func("/teams/get-logo", {"teamId": team_id})
                if binary:
                    content, _content_type = binary
                    LOGO_DIR.mkdir(parents=True, exist_ok=True)
                    with open(local_path, "wb") as f:
                        f.write(content)
            except Exception:
                pass
    local_url = f"/static/images/team_logos/{local_filename}" if local_path.exists() else logo_url
    save_to_cache(str(team_id), "team_logo", {"logo_url": local_url})


def get_cached_team_logo(team_id):
    """Get cached team logo URL"""
    if not team_id:
        return None
    # Prefer local static file if present
    local_path = LOGO_DIR / f"{team_id}.png"
    if local_path.exists():
        return f"/static/images/team_logos/{team_id}.png"
    data = load_from_cache(str(team_id), "team_logo")
    if data and isinstance(data, dict):
        logo_url = data.get("logo_url")
        # If cached URL is already local/static, use it
        if logo_url and str(logo_url).startswith("/static/"):
            return logo_url
    # Always provide a browser-loadable fallback (no external hotlink/header issues)
    return f"/teams/get-logo?teamId={team_id}"


def cache_team_logos_from_standings(standings_data, cache_team_logo_func=None):
    """Cache team logos from standings data"""
    if not standings_data or "standings" not in standings_data:
        return
    try:
        rows = standings_data["standings"][0]["rows"]
        for row in rows:
            team = row.get("team", {})
            if cache_team_logo_func:
                cache_team_logo_func(team.get("id"), team.get("imageUrl"))
    except (KeyError, IndexError, TypeError):
        return


def cleanup_old_cache(days_to_keep=30):
    """Clean up old cache files"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    for file in CACHE_DIR.glob("*.json"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
            file.unlink()


# ======================== PREDICTION HISTORY FUNCTIONS ========================
def save_prediction_history(record):
    """Save prediction history record"""
    try:
        if HISTORY_FILE_CACHE.exists():
            with open(HISTORY_FILE_CACHE, "r", encoding="utf-8") as f:
                history = json.load(f)
        elif HISTORY_FILE_PERMANENT.exists():
            with open(HISTORY_FILE_PERMANENT, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
        history = [h for h in history if h['fixture_id'] != record['fixture_id']]
        history.insert(0, record)
        with open(HISTORY_FILE_CACHE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        with open(HISTORY_FILE_PERMANENT, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Lỗi ghi lịch sử dự đoán:", e)


def load_prediction_history():
    """Load prediction history"""
    if HISTORY_FILE_CACHE.exists():
        with open(HISTORY_FILE_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    elif HISTORY_FILE_PERMANENT.exists():
        with open(HISTORY_FILE_PERMANENT, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []


def save_prediction_history_list(history):
    """Save entire prediction history list"""
    try:
        with open(HISTORY_FILE_CACHE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        with open(HISTORY_FILE_PERMANENT, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Lỗi ghi lịch sử dự đoán:", e)


# ======================== FAVORITES FUNCTIONS ========================
def save_favorites_teams(favorites, user_id=None):
    """Save favorites teams (theo user nếu có user_id)."""
    cache_file, permanent_file = _get_user_favorites_file(user_id)
    cache_file.parent.mkdir(exist_ok=True)
    permanent_file.parent.mkdir(exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)
    with open(permanent_file, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


def load_favorites_teams(user_id=None):
    """Load favorites teams (theo user nếu có user_id)."""
    cache_file, permanent_file = _get_user_favorites_file(user_id)
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    if permanent_file.exists():
        with open(permanent_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
