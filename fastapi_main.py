"""
App Architect Studio - FastAPI Backend
Production-ready API server for Vultr deployment
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import os
import json
import base64
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

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="App Architect Studio API",
    description="Backend API powered by IBM Bob, Vultr, Speechmatic, and NativelyAI",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class VisionRequest(BaseModel):
    image: str  # base64 encoded image

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

class SessionLog(BaseModel):
    timestamp: str
    action: str
    status: str
    input_summary: str
    output_summary: str

# ============================================================================
# WATSONX (IBM Granite / IBM Bob)
# ============================================================================

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "App Architect Studio API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info"""
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
            "sessions": "/api/sessions (GET, POST)"
        }
    }

# ============================================================================
# VISION API - Screenshot Analysis
# ============================================================================

@app.post("/api/vision", response_model=VisionResponse)
async def analyze_vision(request: VisionRequest, background_tasks: BackgroundTasks):
    """
    Analyze screenshot with IBM Bob vision
    Extract design tokens: colors, fonts, spacing, components
    """
    try:
        if not credentials_configured():
            raise HTTPException(
                status_code=503,
                detail="watsonx credentials missing (WATSONX_API_KEY, WATSONX_PROJECT_ID)",
            )

        logger.info("Vision analysis requested")

        image_data = request.image
        tokens, usage = analyze_screenshot(image_data)
        
        # Create style-lock
        style_lock = {
            "locked": True,
            "tokens": tokens,
            "constraints": [
                f"Colors: {', '.join([c['name'] for c in tokens.get('colors', [])])}",
                f"Fonts: {', '.join([f['name'] for f in tokens.get('fonts', [])])}",
                f"Spacing: {', '.join([s['name'] for s in tokens.get('spacing', [])])}"
            ],
            "generatedAt": datetime.now().isoformat()
        }
        
        # Log to sessions
        background_tasks.add_task(
            log_session,
            "vision",
            tokens,
            "success"
        )
        
        logger.info(f"Vision analysis complete: {len(tokens.get('colors', []))} colors extracted")
        
        return VisionResponse(
            tokens=tokens,
            styleLock=style_lock,
            usage=usage,
        )
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse design tokens")
    except Exception as e:
        logger.error(f"Vision error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GENERATE API - Component Generation
# ============================================================================

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_components(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate React components with style-lock constraints
    IBM Bob enforces design token constraints
    """
    try:
        logger.info(f"Generating components: {request.componentNames}")
        
        tokens = request.tokens
        language = request.language
        
        # Build language instruction
        language_instructions = {
            "en": "Use English for class names and comments",
            "es": "Use Spanish for class names and comments",
            "fr": "Use French for class names and comments",
            "de": "Use German for class names and comments",
            "ja": "Use Japanese transliterations in comments"
        }
        
        # Extract token names
        color_names = ", ".join([c['name'] for c in tokens.get('colors', [])])
        font_names = ", ".join([f['name'] for f in tokens.get('fonts', [])])
        spacing_names = ", ".join([s['name'] for s in tokens.get('spacing', [])])
        
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
5. Export a 'locked' property per component

Your code will be validated against the style-lock.
Breaking these constraints will cause rejection."""

        user_prompt = f"""Generate TypeScript React components for: {', '.join(request.componentNames)}

Language: {language}

Design Tokens:
{json.dumps(tokens, indent=2)}

Generate production-ready components with proper TypeScript interfaces."""

        code, _ = generate_text(system_prompt, user_prompt)
        
        # Log to sessions
        background_tasks.add_task(
            log_session,
            "generate",
            {
                "components": request.componentNames,
                "language": language
            },
            "success"
        )
        
        logger.info(f"Component generation complete: {len(request.componentNames)} components")
        
        return GenerateResponse(
            code=code,
            language=language,
            tokens=tokens
        )
    
    except Exception as e:
        logger.error(f"Generate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WORDPRESS API - Fix WordPress Sites
# ============================================================================

@app.post("/api/wordpress")
async def fix_wordpress(request: dict, background_tasks: BackgroundTasks):
    """
    Fix WordPress sites while respecting theme.json constraints
    IBM Bob understands WordPress and prevents CSS bloat
    """
    try:
        logger.info("WordPress fix requested")
        
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
        
        # Log to sessions
        background_tasks.add_task(
            log_session,
            "wordpress",
            {"problem": problem},
            "success"
        )
        
        logger.info("WordPress fix complete")
        
        return {
            "success": True,
            "fixedCode": code,
            "message": "WordPress site fixed while respecting theme.json"
        }
    
    except Exception as e:
        logger.error(f"WordPress error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VOICE API - Speech-to-Code
# ============================================================================

@app.post("/api/voice")
async def process_voice(request: dict, background_tasks: BackgroundTasks):
    """
    Process voice input and generate components
    Powered by Speechmatic for transcription
    """
    try:
        logger.info("Voice request processed")
        
        # Placeholder: Would use Speechmatic API here
        audio_base64 = request.get("audioBase64", "")
        
        # For now, return placeholder
        background_tasks.add_task(
            log_session,
            "voice",
            {"audioLength": len(audio_base64)},
            "success"
        )
        
        return {
            "success": True,
            "message": "Voice processing - coming soon with Speechmatic integration"
        }
    
    except Exception as e:
        logger.error(f"Voice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SESSIONS API - Track IBM Bob Usage
# ============================================================================

@app.get("/api/sessions")
async def get_sessions(action: Optional[str] = None):
    """
    Get IBM Bob session logs
    Use for audit trail and judging
    """
    try:
        sessions = []
        
        # Read from sessions directory
        sessions_dir = "sessions"
        if os.path.exists(sessions_dir):
            for filename in os.listdir(sessions_dir):
                if filename.endswith("_sessions.json"):
                    with open(os.path.join(sessions_dir, filename), 'r') as f:
                        data = json.load(f)
                        if action:
                            data = [s for s in data if s.get('action') == action]
                        sessions.extend(data)
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions")
async def log_session(action: str, data: dict, status: str = "success"):
    """
    Log an IBM Bob session
    Automatically called by other endpoints
    """
    try:
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "data": data
        }
        
        # Create sessions directory if needed
        os.makedirs("sessions", exist_ok=True)
        
        # Append to action-specific file
        filename = f"sessions/{action}_sessions.json"
        sessions = []
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                sessions = json.load(f)
        
        sessions.append(session_data)
        
        with open(filename, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        logger.info(f"Session logged: {action}")
        
        # TODO: Push to ibm-bob-sessions GitHub repo
        
        return {"success": True, "message": "Session logged"}
    
    except Exception as e:
        logger.error(f"Failed to log session: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now().isoformat()},
    )

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 App Architect Studio API starting...")
    logger.info(f"watsonx credentials: {credentials_configured()}")
    logger.info(f"vision model: {VISION_MODEL}")
    logger.info(f"text model: {TEXT_MODEL}")
    logger.info("Ready to receive requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("🛑 App Architect Studio API shutting down...")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run on 0.0.0.0 to accept external connections (Vultr)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
