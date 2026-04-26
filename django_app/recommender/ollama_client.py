"""
Ollama HTTP 클라이언트.
gemma3:4b에게 책 3권을 JSON 배열 형식으로 추천하게 한 뒤,
응답에서 JSON 부분만 안전하게 잘라 파싱합니다.
"""
import json
import re
from typing import List, Tuple

import requests
from django.conf import settings


PROMPT_TEMPLATE = """\
당신은 한국어로 답하는 책 추천 큐레이터입니다.
사용자의 키워드/기분: "{keyword}"

이 키워드/기분에 어울리는 책 정확히 3권을 추천하세요.
출력은 반드시 아래와 같은 **JSON 배열 한 개**만 출력하세요. 다른 텍스트, 코드펜스(```), 설명, 머리말/꼬리말 모두 금지입니다.

[
  {{
    "title": "책 제목",
    "author": "저자",
    "summary": "한 줄 줄거리",
    "reason": "이 키워드에 맞는 추천 이유"
  }},
  {{
    "title": "...",
    "author": "...",
    "summary": "...",
    "reason": "..."
  }},
  {{
    "title": "...",
    "author": "...",
    "summary": "...",
    "reason": "..."
  }}
]
"""


def _extract_json_array(text: str) -> str:
    """모델이 코드펜스나 설명을 섞어 출력해도 첫 JSON 배열만 추출."""
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def recommend_books(keyword: str, timeout: int = 120) -> Tuple[List[dict], str]:
    """
    Returns: (parsed_books, raw_response_text)
    parsed_books는 항상 list. 파싱에 실패하면 빈 리스트로 폴백.
    """
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": PROMPT_TEMPLATE.format(keyword=keyword),
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.7},
    }

    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("response", "")

    # format=json 옵션을 줘도 모델이 객체를 줄 수도 있으니 배열을 끌어내서 파싱
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(_extract_json_array(raw))
        except json.JSONDecodeError:
            parsed = []

    if isinstance(parsed, dict):
        for key in ("books", "results", "items", "recommendations"):
            if key in parsed and isinstance(parsed[key], list):
                parsed = parsed[key]
                break
        else:
            parsed = [parsed]

    if not isinstance(parsed, list):
        parsed = []

    cleaned: List[dict] = []
    for item in parsed[:3]:
        if not isinstance(item, dict):
            continue
        cleaned.append({
            "title": str(item.get("title", "")).strip(),
            "author": str(item.get("author", "")).strip(),
            "summary": str(item.get("summary", "")).strip(),
            "reason": str(item.get("reason", "")).strip(),
        })

    return cleaned, raw
