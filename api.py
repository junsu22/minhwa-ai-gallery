import base64
import io
import json
import os
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)
GALLERY_INFO = GALLERY_DIR / "gallery_info.json"
API_KEY = os.getenv("GEMINI_API_KEY", "")


def _load_gallery_info() -> dict:
    if GALLERY_INFO.exists():
        try:
            return json.loads(GALLERY_INFO.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def expand_prompt(user_input: str) -> tuple[bool, str]:
    """
    한글 간단 입력 → 민화 스타일 영어 프롬프트 자동 생성 (gemini-3-flash)
    """
    try:
        genai.configure(api_key=API_KEY)
        text_model = genai.GenerativeModel("gemini-2.5-flash")

        instruction = f"""
You are a Korean minhwa art prompt specialist.
Convert the user's Korean description into a detailed English image generation prompt.

Strict style rules — always include ALL of these:
- Korean minhwa traditional folk art composition
- Colorful psychedelic neon art style
- Vibrant neon colors on dark purple/navy background
- Decorative patterns, pine trees, lotus flowers, clouds, mountains
- Glowing ornate details, masterpiece quality
- No text, no graffiti, no watermark

For human figures — always specify:
- Joseon dynasty clothing (jeogori, dopo robe)
- Traditional Korean hairstyle (daenggi braided hair for children, gat hat for scholars)
- NOT bald, NOT modern hairstyle, NOT Chinese style

User input: {user_input}

Return ONLY the English prompt in one paragraph. No explanation.
"""
        response = text_model.generate_content(instruction)
        return True, response.text.strip()
    except Exception as e:
        return False, f"프롬프트 생성 오류: {str(e)}"


def generate_image(
    prompt: str,
    title: str = "",
    negative_prompt: str = "",
) -> tuple[bool, str]:
    """
    영어 프롬프트 → 이미지 생성 (gemini-3-flash-image)
    """
    try:
        genai.configure(api_key=API_KEY)
        image_model = genai.GenerativeModel("gemini-3.1-flash-image-preview")

        full_prompt = prompt
        if negative_prompt:
            full_prompt += f". Avoid: {negative_prompt}"

        response = image_model.generate_content(full_prompt)
    except Exception as e:
        return False, f"이미지 생성 오류: {str(e)}"

    image_bytes = None
    for part in response.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            image_bytes = part.inline_data.data  # SDK가 이미 raw bytes로 디코딩
            break

    if not image_bytes:
        return False, "이미지가 생성되지 않았습니다. 다시 시도해 주세요."

    # Gemini가 WEBP/JPEG를 반환할 수 있으므로 Pillow로 PNG 변환
    try:
        img = Image.open(io.BytesIO(image_bytes))
        png_buf = io.BytesIO()
        img.save(png_buf, format="PNG")
        image_bytes = png_buf.getvalue()
    except Exception:
        pass  # 변환 실패 시 원본 바이트 그대로 사용

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    img_path = GALLERY_DIR / f"{timestamp}.png"
    img_path.write_bytes(image_bytes)

    meta = {
        "title": title or prompt[:30],
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "style": "Korean Minhwa",
        "created": datetime.now().isoformat(),
    }
    img_path.with_suffix(".json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return True, str(img_path)


def load_gallery_images() -> list[dict]:
    gallery_info = _load_gallery_info()
    images = sorted(GALLERY_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
    result = []
    for path in images:
        stat = path.stat()
        meta = {}

        json_path = path.with_suffix(".json")
        if json_path.exists():
            try:
                meta = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        if not meta and path.name in gallery_info:
            info = gallery_info[path.name]
            meta = {
                "title": info.get("title", "Untitled"),
                "prompt": info.get("prompt", ""),
                "style":  info.get("style", "Korean Minhwa"),
            }

        result.append({
            "path":    str(path),
            "title":   meta.get("title", "Untitled"),
            "prompt":  meta.get("prompt", ""),
            "style":   meta.get("style", "Korean Minhwa"),
            "size_kb": round(stat.st_size / 1024, 1),
            "created": meta.get("created", datetime.fromtimestamp(stat.st_mtime).isoformat())[:10],
        })
    return result


def delete_image(path: str) -> bool:
    try:
        p = Path(path)
        p.unlink()
        json_path = p.with_suffix(".json")
        if json_path.exists():
            json_path.unlink()
        return True
    except Exception:
        return False


def image_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
