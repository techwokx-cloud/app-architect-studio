"""
App Architect Studio - FastAPI Backend
Production-ready API server for Vultr deployment
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import os
import json
from datetime import datetime
from typing import List, Optional

from watsonx_client import (
    TEXT_MODEL,
    VISION_MODEL,
    analyze_screenshot,
    credentials_configured,
    generate_text,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="App Architect Studio API",
    description="Backend API powered by IBM watsonx.ai (Granite)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VisionRequest(BaseModel):
    image: str


class GenerateRequest(BaseModel):
    tokens: dict
    componentNames: List[str]
    language: str = "en"
    styleLock: Optional[dict] = None


class VisionResponse(BaseModel):
    tokens: dict
    styleLock: dict
    usage: dict


class GenerateResponse(BaseModel):
    code: str
    language: str
    tokens: dict


@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "App Architect Studio API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "watsonx_configured": credentials_configured(),
    }


@app.get("/")
async def root():
    return {
        "name": "App Architect Studio API",
        "version": "1.0.0",
        "description": "Backend API powered by IBM watsonx.ai (Granite)",
        "models": {
            "vision": VISION_MODEL,
            "text": TEXT_MODEL,
        },
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "vision": "/api/vision (POST)",
            "generate": "/api/generate (POST)",
            "wordpress": "/api/wordpress (POST)",
            "voice": "/api/voice (POST)",
            "sessions": "/api/sessions (GET, POST)",
        },
    }


@app.post("/api/vision", response_model=VisionResponse)
async def analyze_vision(request: VisionRequest, background_tasks: BackgroundTasks):
    try:
        if not credentials_configured():
            raise HTTPException(
                status_code=503,
                detail="watsonx credentials missing (WATSONX_API_KEY, WATSONX_PROJECT_ID)",
            )

        logger.info("Vision analysis requested")
        tokens, usage = analyze_screenshot(request.image)

        style_lock = {
            "locked": True,
            "tokens": tokens,
            "constraints": [
                f"Colors: {', '.join(c['name'] for c in tokens.get('colors', []))}",
                f"Fonts: {', '.join(f['name'] for f in tokens.get('fonts', []))}",
                f"Spacing: {', '.join(s['name'] for s in tokens.get('spacing', []))}",
            ],
            "generatedAt": datetime.now().isoformat(),
        }

        background_tasks.add_task(log_session, "vision", tokens, "success")
        logger.info(
            "Vision analysis complete: %d colors",
            len(tokens.get("colors", [])),
        )

        return VisionResponse(tokens=tokens, styleLock=style_lock, usage=usage)

    except json.JSONDecodeError as e:
        logger.error("JSON parsing error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to parse design tokens")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Vision error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_components(
    request: GenerateRequest, background_tasks: BackgroundTasks
):
    try:
        if not credentials_configured():
            raise HTTPException(
                status_code=503,
                detail="watsonx credentials missing (WATSONX_API_KEY, WATSONX_PROJECT_ID)",
            )

        logger.info("Generating components: %s", request.componentNames)
        tokens = request.tokens
        language = request.language

        language_instructions = {
            "en": "Use English for class names and comments",
            "es": "Use Spanish for class names and comments",
            "fr": "Use French for class names and comments",
            "de": "Use German for class names and comments",
            "ja": "Use Japanese transliterations in comments",
        }

        color_names = ", ".join(c["name"] for c in tokens.get("colors", []))
        font_names = ", ".join(f["name"] for f in tokens.get("fonts", []))
        spacing_names = ", ".join(s["name"] for s in tokens.get("spacing", []))

        system_prompt = f"""You are a React component architect for App Architect Studio.

STYLE-LOCK CONSTRAINTS (CRITICAL):
- Colors: {color_names}
- Fonts: {font_names}
- Spacing: {spacing_names}

RULES:
1. Use className with Tailwind utilities
2. Reference design tokens by name ONLY
3. Do NOT create new color/font/spacing names
4. {language_instructions.get(language, language_instructions['en'])}
5. Export a 'locked' property per component"""

        user_prompt = f"""Generate TypeScript React components for: {', '.join(request.componentNames)}

Language: {language}

Design Tokens:
{json.dumps(tokens, indent=2)}

Generate production-ready components with proper TypeScript interfaces."""

        code, _ = generate_text(system_prompt, user_prompt)

        background_tasks.add_task(
            log_session,
            "generate",
            {"components": request.componentNames, "language": language},
            "success",
        )

        return GenerateResponse(code=code, language=language, tokens=tokens)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Generate error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wordpress")
async def fix_wordpress(request: dict, background_tasks: BackgroundTasks):
    try:
        if not credentials_configured():
            raise HTTPException(status_code=503, detail="watsonx credentials missing")

        php_code = request.get("phpCode", "")
        theme_json = request.get("themeJson", "{}")
        problem = request.get("problem", "")

        system_prompt = """You are a WordPress theme specialist.

RULES:
1. Read theme.json and extract CSS variables
2. ONLY modify PHP logic, NOT HTML structure
3. ONLY use colors/spacing from theme.json
4. Do NOT create new .css files or <style> tags
5. Keep all existing class names
6. Output fixed PHP code + CHANGELOG.md"""

        user_prompt = f"""Fix this WordPress issue: {problem}

theme.json:
{theme_json}

Current PHP:
{php_code}

Output:
1. Fixed PHP code
2. CHANGELOG.md explaining changes"""

        code, _ = generate_text(system_prompt, user_prompt)
        background_tasks.add_task(
            log_session, "wordpress", {"problem": problem}, "success"
        )

        return {
            "success": True,
            "fixedCode": code,
            "message": "WordPress site fixed while respecting theme.json",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("WordPress error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice")
async def process_voice(request: dict, background_tasks: BackgroundTasks):
    try:
        audio_base64 = request.get("audioBase64", "")
        background_tasks.add_task(
            log_session, "voice", {"audioLength": len(audio_base64)}, "success"
        )
        return {
            "success": True,
            "message": "Voice processing - coming soon with Speechmatic integration",
        }
    except Exception as e:
        logger.error("Voice error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def get_sessions(action: Optional[str] = None):
    try:
        sessions = []
        sessions_dir = "sessions"
        if os.path.exists(sessions_dir):
            for filename in os.listdir(sessions_dir):
                if filename.endswith("_sessions.json"):
                    with open(os.path.join(sessions_dir, filename), "r") as f:
                        data = json.load(f)
                        if action:
                            data = [s for s in data if s.get("action") == action]
                        sessions.extend(data)

        return {
            "total_sessions": len(sessions),
            "sessions": sessions,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error("Sessions error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


async def log_session(action: str, data: dict, status: str = "success"):
    try:
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "data": data,
        }
        os.makedirs("sessions", exist_ok=True)
        filename = f"sessions/{action}_sessions.json"
        sessions = []
        if os.path.exists(filename):
            with open(filename, "r") as f:
                sessions = json.load(f)
        sessions.append(session_data)
        with open(filename, "w") as f:
            json.dump(sessions, f, indent=2)
        logger.info("Session logged: %s", action)
    except Exception as e:
        logger.error("Failed to log session: %s", e)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now().isoformat()},
    )


@app.on_event("startup")
async def startup_event():
    logger.info("App Architect Studio API starting...")
    logger.info("watsonx credentials: %s", credentials_configured())
    logger.info("vision model: %s", VISION_MODEL)
    logger.info("text model: %s", TEXT_MODEL)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("App Architect Studio API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
