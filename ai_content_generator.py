import os
import re
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict

# Optional .env loader
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
_PLACEHOLDER_VALUES = {"", "your_gemini_api_key_here", "your_key_here", "YOUR_API_KEY"}

DEFAULT_CONFIG = {
    "model": "models/gemini-2.5-flash",
    "temperature": 0.7,
    "max_output_tokens": 1024,
}

PROMPTS = {
    "expand_article": """Bạn là phóng viên thể thao chuyên viết bài bóng đá bằng tiếng Việt.
Dựa vào thông tin ngắn gọn bên dưới, hãy viết một bài báo hoàn chỉnh bằng tiếng Việt.

Tiêu đề gốc: {title}
Mô tả ngắn: {description}
Giải đấu: {league}

Yêu cầu:
- Viết khoảng 200-350 từ
- Dùng ngôn ngữ báo chí thể thao, sinh động, hấp dẫn
- Bao gồm: diễn biến chính, điểm nhấn, nhận định ngắn
- KHÔNG bịa đặt số liệu cụ thể nếu không có trong mô tả gốc
- Kết thúc bằng 1 câu nhận định/dự đoán

Chỉ trả về nội dung bài viết, không thêm tiêu đề hay chú thích.""",
    "summarize_article": """Là biên tập viên thể thao, hãy tóm tắt bài viết sau thành đoạn mô tả ngắn gọn bằng tiếng Việt (khoảng 80-120 từ):

Nội dung gốc:
{content}

Chỉ trả về đoạn tóm tắt, không thêm tiêu đề.""",
    "generate_vi_title": """Bạn là biên tập viên thể thao. Dịch và viết lại tiêu đề sau thành tiếng Việt cho hấp dẫn, đúng ngữ pháp, phù hợp phong cách báo thể thao Việt Nam:

Tiêu đề gốc (tiếng Anh): {title}

Chỉ trả về 1 tiêu đề tiếng Việt duy nhất, không giải thích.""",
    "match_preview": """Bạn là chuyên gia phân tích bóng đá. Viết bài nhận định trận đấu sắp diễn ra bằng tiếng Việt.

Thông tin trận đấu: {match_info}
Giải đấu: {league}

Yêu cầu:
- Viết khoảng 150-250 từ
- Phân tích phong độ, lịch sử đối đầu (ngắn gọn)
- Đưa ra dự đoán kết quả có lý lẽ
- Ngôn ngữ tự nhiên, chuyên nghiệp, tiếng Việt

Chỉ trả về nội dung nhận định.""",
}


CACHE_DIR = Path(__file__).resolve().parent / "permanent_cache"
CACHE_FILE = CACHE_DIR / "ai_cache.json"


class AIContentCache:
    """Persistent cache nội dung AI để giảm số lần gọi API."""

    def __init__(self):
        CACHE_DIR.mkdir(exist_ok=True)
        self._data: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception:
            self._data = {}

    def _save(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def _make_key(prompt_type: str, **kwargs) -> str:
        raw = prompt_type + "|" + "|".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]

    def get(self, prompt_type: str, **kwargs) -> Optional[str]:
        key = self._make_key(prompt_type, **kwargs)
        entry = self._data.get(key)
        return entry.get("content") if entry else None

    def set(self, content: str, prompt_type: str, **kwargs):
        key = self._make_key(prompt_type, **kwargs)
        self._data[key] = {"content": content, "prompt_type": prompt_type, "params": kwargs}
        self._save()


_ai_cache = AIContentCache()


class AIContentGenerator:
    """Sinh nội dung bóng đá tiếng Việt bằng Gemini (nếu có cấu hình)."""

    def __init__(self):
        self._client = None
        self._model_old = None
        self._sdk = None
        self._initialized = False
        self._init_gemini()

    def _init_gemini(self):
        if GEMINI_API_KEY in _PLACEHOLDER_VALUES:
            return

        # SDK mới: google-genai
        try:
            from google import genai as google_genai

            self._client = google_genai.Client(api_key=GEMINI_API_KEY)
            self._sdk = "new"
            self._initialized = True
            return
        except Exception:
            pass

        # Fallback SDK cũ: google-generativeai
        try:
            import warnings
            import google.generativeai as genai

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                genai.configure(api_key=GEMINI_API_KEY)
                self._model_old = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={
                        "temperature": DEFAULT_CONFIG["temperature"],
                        "max_output_tokens": DEFAULT_CONFIG["max_output_tokens"],
                    },
                )
            self._sdk = "old"
            self._initialized = True
        except Exception:
            self._initialized = False

    @property
    def is_available(self) -> bool:
        return bool(self._initialized)

    def _call_ai(self, prompt: str) -> Optional[str]:
        if not self.is_available:
            return None
        try:
            if self._sdk == "new":
                response = self._client.models.generate_content(
                    model=DEFAULT_CONFIG["model"],
                    contents=prompt,
                )
                return response.text.strip() if getattr(response, "text", None) else None
            if self._sdk == "old":
                import warnings

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    response = self._model_old.generate_content(prompt)
                return response.text.strip() if getattr(response, "text", None) else None
        except Exception:
            return None
        return None

    @staticmethod
    def _clean_ai_output(text: str) -> str:
        if not text:
            return text
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def expand_article(self, title: str, description: str = "", league: str = "Football") -> Optional[str]:
        if not title:
            return None
        cached = _ai_cache.get("expand_article", title=title[:80], league=league)
        if cached:
            return cached
        prompt = PROMPTS["expand_article"].format(
            title=title,
            description=description or "Không có mô tả bổ sung.",
            league=league,
        )
        out = self._call_ai(prompt)
        if not out:
            return None
        out = self._clean_ai_output(out)
        _ai_cache.set(out, "expand_article", title=title[:80], league=league)
        return out

    def summarize_article(self, content: str) -> Optional[str]:
        if not content:
            return None
        cached = _ai_cache.get("summarize_article", content=content[:120])
        if cached:
            return cached
        prompt = PROMPTS["summarize_article"].format(content=content)
        out = self._call_ai(prompt)
        if not out:
            return None
        out = self._clean_ai_output(out)
        _ai_cache.set(out, "summarize_article", content=content[:120])
        return out

    def generate_vi_title(self, title: str) -> Optional[str]:
        if not title:
            return None
        cached = _ai_cache.get("generate_vi_title", title=title[:120])
        if cached:
            return cached
        prompt = PROMPTS["generate_vi_title"].format(title=title)
        out = self._call_ai(prompt)
        if not out:
            return None
        out = self._clean_ai_output(out)
        _ai_cache.set(out, "generate_vi_title", title=title[:120])
        return out

    def generate_match_preview(self, match_info: str, league: str = "Football") -> Optional[str]:
        if not match_info:
            return None
        cached = _ai_cache.get("match_preview", match_info=match_info[:120], league=league)
        if cached:
            return cached
        prompt = PROMPTS["match_preview"].format(match_info=match_info, league=league)
        out = self._call_ai(prompt)
        if not out:
            return None
        out = self._clean_ai_output(out)
        _ai_cache.set(out, "match_preview", match_info=match_info[:120], league=league)
        return out


ai_generator = AIContentGenerator()

