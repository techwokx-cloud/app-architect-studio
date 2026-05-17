"""
App Architect Studio - Streamlit Frontend

This frontend talks to the backend through API_BASE_URL only. External service
keys stay on the backend or in Streamlit Cloud secrets.
"""

from __future__ import annotations

import base64
import os
from datetime import datetime
from typing import Any, Optional

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


def _apply_streamlit_secrets() -> None:
    try:
        app_cfg = st.secrets.get("app", {})
        if app_cfg.get("api_base_url"):
            os.environ["API_BASE_URL"] = str(app_cfg["api_base_url"])
    except Exception:
        pass


st.set_page_config(
    page_title="App Architect Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)
_apply_streamlit_secrets()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "120"))


@st.cache_resource
def session() -> requests.Session:
    return requests.Session()


def api_get(path: str, timeout: int = 10) -> Optional[dict[str, Any]]:
    try:
        response = session().get(f"{API_BASE_URL}{path}", timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        st.warning(f"Backend unavailable: {exc}")
        return None


def api_post(path: str, payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    try:
        response = session().post(
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=API_TIMEOUT,
        )
        if response.status_code >= 400:
            detail = response.json().get("detail", response.text)
            st.error(f"API error {response.status_code}: {detail}")
            return None
        return response.json()
    except Exception as exc:
        st.error(f"API error: {exc}")
        return None


def image_to_base64(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


if "tokens" not in st.session_state:
    st.session_state.tokens = None
if "style_lock" not in st.session_state:
    st.session_state.style_lock = None
if "generated_code" not in st.session_state:
    st.session_state.generated_code = None


st.title("🎨 App Architect Studio")
st.caption("Frontend → FastAPI backend → IBM watsonx.ai / external integrations")

status = api_get("/api/status")
if status:
    st.success(f"Backend online: {API_BASE_URL}")
    with st.expander("Integration status", expanded=False):
        st.json(status.get("integrations", {}))
else:
    st.warning(f"Backend not reachable at {API_BASE_URL}")

tab_vision, tab_voice, tab_tools, tab_dashboard = st.tabs(
    ["Vision-to-Code", "Voice", "API Tools", "Dashboard"]
)

with tab_vision:
    left, right = st.columns(2)

    with left:
        st.subheader("1. Upload Screenshot")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"],
        )
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded screenshot", use_column_width=True)

        if uploaded_file and st.button("Analyze with IBM Granite Vision"):
            with st.spinner("Extracting design tokens..."):
                result = api_post("/api/vision", {"image": image_to_base64(uploaded_file)})
            if result:
                st.session_state.tokens = result.get("tokens")
                st.session_state.style_lock = result.get("styleLock")
                st.success("Design tokens extracted")

    with right:
        st.subheader("2. Tokens")
        if st.session_state.tokens:
            st.json(st.session_state.tokens)
        else:
            st.info("Upload and analyze a screenshot first.")

    if st.session_state.tokens:
        st.divider()
        st.subheader("3. Generate Components")
        components = [
            component.get("name")
            for component in st.session_state.tokens.get("components", [])
            if component.get("name")
        ]
        selected_components = st.multiselect(
            "Components",
            components,
            default=components[:3],
        )
        language = st.selectbox(
            "Language",
            ["en", "es", "fr", "de", "ja"],
            index=0,
        )

        if st.button("Generate React Components"):
            if not selected_components:
                st.warning("Select at least one component.")
            else:
                with st.spinner("Generating code..."):
                    result = api_post(
                        "/api/generate",
                        {
                            "tokens": st.session_state.tokens,
                            "componentNames": selected_components,
                            "language": language,
                            "styleLock": st.session_state.style_lock,
                        },
                    )
                if result:
                    st.session_state.generated_code = result.get("code")
                    st.success("Code generated")

    if st.session_state.generated_code:
        st.divider()
        st.subheader("4. Generated Code")
        st.code(st.session_state.generated_code, language="typescript")
        st.download_button(
            "Download components.tsx",
            st.session_state.generated_code,
            file_name="components.tsx",
            mime="text/plain",
        )
        storage_key = st.text_input("Cloudflare R2 object key", "components.tsx")
        if st.button("Save to Cloudflare R2"):
            result = api_post(
                "/api/storage/save",
                {
                    "key": storage_key,
                    "content": st.session_state.generated_code,
                    "contentType": "text/plain",
                },
            )
            if result:
                st.success(f"Saved: {result.get('key')}")

with tab_voice:
    st.subheader("Speechmatics Voice Transcription")
    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])
    language = st.text_input("Language", "en")
    if audio_file and st.button("Transcribe"):
        audio_base64 = base64.b64encode(audio_file.getvalue()).decode("utf-8")
        result = api_post(
            "/api/voice",
            {
                "audioBase64": audio_base64,
                "language": language,
                "format": audio_file.name.split(".")[-1],
            },
        )
        if result:
            st.text_area("Transcript", result.get("transcript", ""), height=200)

with tab_tools:
    st.subheader("Google API Helper")
    prompt = st.text_area("Prompt", "Summarize App Architect Studio in one paragraph.")
    if st.button("Run Google Generate"):
        result = api_post("/api/google/generate", {"prompt": prompt})
        if result:
            st.write(result.get("text", ""))

with tab_dashboard:
    st.subheader("Backend")
    st.code(f"API_BASE_URL={API_BASE_URL}")
    st.json(status or {})
    st.caption(f"Checked at {datetime.now().isoformat()}")
