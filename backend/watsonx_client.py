"""
IBM watsonx.ai client (Granite models — same stack as IBM Bob).
"""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Any, Optional, Tuple

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

TEXT_MODEL = os.getenv("WATSONX_TEXT_MODEL", "ibm/granite-3-8b-instruct")
VISION_MODEL = os.getenv("WATSONX_VISION_MODEL", "ibm/granite-vision-3-2-2b")

VISION_TOKEN_PROMPT = """Analyze this UI screenshot and extract design tokens.

Return ONLY valid JSON. Do not include markdown, explanations, comments, or code fences.
The JSON must match this schema exactly:
{
  "colors": [{"name": "primary", "value": "#3B82F6"}],
  "fonts": [{"name": "body", "family": "Inter", "size": "1rem", "weight": "400"}],
  "spacing": [{"name": "md", "value": "1rem"}],
  "components": [{"name": "Button", "description": "Primary action button"}]
}"""


def get_watsonx_config() -> dict[str, Optional[str]]:
    return {
        "api_key": os.getenv("WATSONX_API_KEY") or os.getenv("IBM_BOB_API_KEY"),
        "project_id": os.getenv("WATSONX_PROJECT_ID"),
        "url": os.getenv("WATSONX_URL", "https://ca-tor.ml.cloud.ibm.com"),
    }


def credentials_configured() -> bool:
    cfg = get_watsonx_config()
    return bool(cfg["api_key"] and cfg["project_id"])


def _require_credentials() -> Tuple[Credentials, str, str]:
    cfg = get_watsonx_config()
    if not cfg["api_key"] or not cfg["project_id"]:
        raise ValueError(
            "Set WATSONX_API_KEY and WATSONX_PROJECT_ID in backend/.env"
        )
    url = (cfg["url"] or "https://ca-tor.ml.cloud.ibm.com").rstrip("/")
    return Credentials(api_key=cfg["api_key"], url=url), cfg["project_id"], url


@lru_cache(maxsize=1)
def _text_model() -> ModelInference:
    credentials, project_id, _ = _require_credentials()
    return ModelInference(
        model_id=TEXT_MODEL,
        credentials=credentials,
        project_id=project_id,
        params={
            GenParams.MAX_NEW_TOKENS: 4000,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.TEMPERATURE: 0.2,
        },
    )


@lru_cache(maxsize=1)
def _vision_model() -> ModelInference:
    credentials, project_id, _ = _require_credentials()
    return ModelInference(
        model_id=VISION_MODEL,
        credentials=credentials,
        project_id=project_id,
        params={
            GenParams.MAX_NEW_TOKENS: 2000,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.TEMPERATURE: 0,
        },
    )


def clear_model_cache() -> None:
    _text_model.cache_clear()
    _vision_model.cache_clear()


def _chat_content(response: dict) -> str:
    content = response["choices"][0]["message"]["content"]
    if isinstance(content, list):
        return "\n".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict)
        )
    return str(content)


def _usage_from_response(response: dict) -> dict[str, Any]:
    usage = response.get("usage") or {}
    return {
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }


def extract_json_from_text(text: str) -> dict:
    cleaned = text.strip()
    if not cleaned:
        raise json.JSONDecodeError("Empty model response", cleaned, 0)

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return json.loads(fenced.group(1))

    start = cleaned.find("{")
    if start == -1:
        raise json.JSONDecodeError("No JSON object found", cleaned, 0)

    depth = 0
    in_string = False
    escape = False
    for idx, char in enumerate(cleaned[start:], start=start):
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(cleaned[start : idx + 1])

    raise json.JSONDecodeError("Unterminated JSON object", cleaned, start)


def _normalize_tokens(tokens: dict) -> dict:
    return {
        "colors": tokens.get("colors") or [],
        "fonts": tokens.get("fonts") or [],
        "spacing": tokens.get("spacing") or [],
        "components": tokens.get("components") or [],
    }


def _repair_tokens_response(raw_text: str) -> dict:
    system = (
        "You convert model output into strict JSON design tokens. "
        "Return only valid JSON with keys: colors, fonts, spacing, components."
    )
    user = f"""Convert this output into valid JSON using this exact schema:
{{
  "colors": [{{"name": "primary", "value": "#3B82F6"}}],
  "fonts": [{{"name": "body", "family": "Inter", "size": "1rem", "weight": "400"}}],
  "spacing": [{{"name": "md", "value": "1rem"}}],
  "components": [{{"name": "Button", "description": "Primary action button"}}]
}}

Model output:
{raw_text}
"""
    response = _text_model().chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        params={GenParams.MAX_NEW_TOKENS: 1500, GenParams.TEMPERATURE: 0},
    )
    return extract_json_from_text(_chat_content(response))


def analyze_screenshot(
    image_base64: str,
    media_type: str = "image/png",
) -> Tuple[dict, dict]:
    """Screenshot → design tokens via Granite Vision."""
    if image_base64.startswith("data:image"):
        image_base64 = image_base64.split(",", 1)[1]

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": VISION_TOKEN_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_base64}",
                    },
                },
            ],
        }
    ]

    response = _vision_model().chat(messages=messages)
    text = _chat_content(response)
    try:
        tokens = extract_json_from_text(text)
    except json.JSONDecodeError:
        tokens = _repair_tokens_response(text)
    return _normalize_tokens(tokens), _usage_from_response(response)


def generate_text(system: str, user: str) -> Tuple[str, dict]:
    """Text prompt → code via Granite 3 8B Instruct."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    response = _text_model().chat(messages=messages)
    return _chat_content(response), _usage_from_response(response)
