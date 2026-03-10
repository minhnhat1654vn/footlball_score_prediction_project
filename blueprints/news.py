"""
News Blueprint - Tin tức bóng đá từ RSS.
Trang /news và API /api/news dùng news_fetcher.
"""
import json
from pathlib import Path

from flask import Blueprint, render_template, request, jsonify

from ai_content_generator import ai_generator

bp = Blueprint('news', __name__)

ARTICLE_AI_FILE = Path(__file__).resolve().parent.parent / "permanent_cache" / "article_ai.json"
ARTICLE_AI_FILE.parent.mkdir(exist_ok=True)


def _load_article_ai() -> dict:
    """Lấy toàn bộ AI content đã lưu: {url -> {content, mode}}"""
    try:
        if ARTICLE_AI_FILE.exists():
            with open(ARTICLE_AI_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return {}
    return {}


def _save_article_ai(url: str, content: str, mode: str):
    """Lưu AI content của một bài viết vào file."""
    if not url:
        return
    try:
        data = _load_article_ai()
        data[url] = {"content": content, "mode": mode}
        with open(ARTICLE_AI_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


@bp.route('/news')
def news():
    """Render trang tin tức (layout mới: league bar + grid + sidebar)."""
    return render_template('news.html', active_tab='news')


@bp.route('/api/news')
def api_news():
    """
    GET /api/news
    Query:
      - league_id (optional) hoặc league (optional)
      - refresh (optional, true = bỏ cache).
    Trả về JSON: { success, articles: [...], count, league }.
    """
    try:
        from news_fetcher import news_fetcher
    except ImportError:
        return jsonify(success=False, articles=[], error='news_fetcher not available'), 200

    league_id = request.args.get("league_id") or request.args.get("league") or "all"
    league_id = str(league_id).strip().lower().replace(" ", "-")
    force_refresh = request.args.get('refresh', '').lower() in ('1', 'true', 'yes')

    articles = news_fetcher.fetch_news(league_id=league_id, force_refresh=force_refresh)
    ai_store = _load_article_ai()
    if ai_store:
        for article in articles:
            url = article.get("url", "")
            if url and url in ai_store:
                article["ai_content"] = ai_store[url].get("content")
                article["ai_mode"] = ai_store[url].get("mode", "expand")

    return jsonify(success=True, articles=articles, count=len(articles), league=league_id)


@bp.route("/api/ai/generate", methods=["POST"])
def ai_generate_article():
    """
    API sinh nội dung bài viết bằng AI.
    Body JSON:
      - title (bắt buộc)
      - description (tùy chọn)
      - league (tùy chọn)
      - mode: 'expand' | 'preview' | 'summarize' (mặc định: 'expand')
      - url (tùy chọn): dùng để lưu cache theo URL
    """
    if not ai_generator.is_available:
        return jsonify(
            success=False,
            error="AI chưa được cấu hình. Vui lòng thêm GEMINI_API_KEY vào file .env",
        ), 503

    data = request.get_json(force=True, silent=True) or {}
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    league = str(data.get("league", "Football")).strip()
    mode = str(data.get("mode", "expand")).strip()

    if not title:
        return jsonify(success=False, error='Thiếu trường "title"'), 400

    try:
        if mode == "preview":
            content = ai_generator.generate_match_preview(
                match_info=f"{title}. {description}".strip(". "),
                league=league,
            )
        elif mode == "summarize":
            content = ai_generator.summarize_article(description or title)
        else:
            content = ai_generator.expand_article(title=title, description=description, league=league)

        if content:
            article_url = str(data.get("url", "")).strip()
            if article_url:
                _save_article_ai(article_url, content, mode)
            return jsonify(success=True, content=content, mode=mode)

        return jsonify(success=False, error="AI không tạo được nội dung"), 500
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@bp.route("/api/ai/title", methods=["POST"])
def ai_generate_title():
    """API dịch/viết lại tiêu đề sang tiếng Việt."""
    if not ai_generator.is_available:
        return jsonify(success=False, error="AI chưa được cấu hình"), 503

    data = request.get_json(force=True, silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(success=False, error='Thiếu trường "title"'), 400

    try:
        vi_title = ai_generator.generate_vi_title(title)
        if vi_title:
            return jsonify(success=True, title=vi_title)
        return jsonify(success=False, error="Không thể dịch tiêu đề"), 500
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
