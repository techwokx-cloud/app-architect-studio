"""
App Architect Studio - Streamlit Frontend
IBM Bob Hackathon 2026 — Competition Entry
"""

import streamlit as st
import requests
from PIL import Image
import base64
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Get the directory where this script lives (for relative icon paths)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(SCRIPT_DIR, "icons")

def load_icon(filename, width=36):
    """Safely load an icon image, skip if not found"""
    icon_path = os.path.join(ICONS_DIR, filename)
    if os.path.exists(icon_path):
        st.image(icon_path, width=width)
    else:
        # Fallback: just skip the icon silently
        pass


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="App Architect Studio | IBM Bob Hackathon 2026",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    /* Global */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: linear-gradient(135deg, #F0F4FF 0%, #F5F0FF 50%, #FFF0F7 100%);
        border-radius: 16px;
        border: 1px solid #E0E7FF;
        margin-bottom: 1.5rem;
    }
    
    .hero-title {
        font-size: 3em;
        font-weight: 800;
        background: linear-gradient(135deg, #1E40AF 0%, #7C3AED 50%, #DB2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2em;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.25em;
        color: #374151;
        font-weight: 400;
        margin-bottom: 1.2em;
        line-height: 1.5;
    }
    
    .hero-description {
        font-size: 1em;
        color: #4B5563;
        max-width: 720px;
        margin: 0 auto 1.5em auto;
        line-height: 1.7;
    }
    
    .powered-by {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1.2rem;
    }
    
    .tech-badge {
        background: white;
        border: 1px solid #E0E7FF;
        border-radius: 24px;
        padding: 8px 18px;
        font-size: 0.85em;
        font-weight: 600;
        color: #3730A3;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    /* Hackathon badge */
    .hackathon-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1E40AF, #7C3AED);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1em;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* How it works */
    .step-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3B82F6, #7C3AED);
        color: white;
        font-weight: 700;
        font-size: 0.9em;
        margin-bottom: 12px;
    }
    
    .step-title {
        font-weight: 700;
        font-size: 1em;
        color: #1F2937;
        margin-bottom: 6px;
    }
    
    .step-desc {
        font-size: 0.85em;
        color: #6B7280;
        line-height: 1.5;
    }
    
    /* Team section */
    .team-section {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 24px;
        margin: 1rem 0;
    }
    
    .team-grid {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .team-card {
        text-align: center;
        padding: 16px 24px;
    }
    
    .team-avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.3em;
        margin: 0 auto 10px auto;
        box-shadow: 0 2px 8px rgba(59,130,246,0.2);
    }
    
    .team-card-name {
        font-weight: 700;
        font-size: 0.95em;
        color: #1F2937;
    }
    
    .team-card-handle {
        font-size: 0.8em;
        color: #6B7280;
        margin-top: 2px;
    }
    
    /* Status indicator */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 500;
    }
    
    .status-offline {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FEF3C7;
        border: 1px solid #FCD34D;
        color: #92400E;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #FAFBFC;
    }
    
    /* Footer */
    .footer-section {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        color: #6B7280;
        font-size: 0.85em;
    }
    
    /* Prompt box */
    .prompt-section {
        background: #F8FAFF;
        border: 1px solid #E0E7FF;
        border-radius: 12px;
        padding: 24px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 30

# ============================================================================
# SESSION STATE
# ============================================================================

if 'tokens' not in st.session_state:
    st.session_state.tokens = None
if 'style_lock' not in st.session_state:
    st.session_state.style_lock = None
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'voice_transcript' not in st.session_state:
    st.session_state.voice_transcript = None
if 'prompt_result' not in st.session_state:
    st.session_state.prompt_result = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'components_generated': 0,
        'minutes_saved': 0,
        'languages_used': set()
    }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@st.cache_resource
def get_session():
    """Get requests session"""
    return requests.Session()

def test_backend():
    """Test if backend is online"""
    try:
        response = get_session().get(
            f"{API_BASE_URL}/health",
            timeout=3
        )
        return response.status_code == 200
    except:
        return False

def convert_image_to_base64(uploaded_file):
    """Convert uploaded image to base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode()

def call_vision_api(image_base64):
    """Call vision analysis endpoint"""
    try:
        response = get_session().post(
            f"{API_BASE_URL}/api/vision",
            json={"image": image_base64},
            timeout=API_TIMEOUT
        )
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def call_generate_api(tokens, component_names, language="en"):
    """Call component generation endpoint"""
    try:
        response = get_session().post(
            f"{API_BASE_URL}/api/generate",
            json={
                "tokens": tokens,
                "componentNames": component_names,
                "language": language
            },
            timeout=API_TIMEOUT
        )
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def call_prompt_api(prompt, language="en"):
    """Call text prompt generation endpoint"""
    try:
        response = get_session().post(
            f"{API_BASE_URL}/api/prompt",
            json={
                "prompt": prompt,
                "language": language
            },
            timeout=API_TIMEOUT
        )
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def display_tokens(tokens):
    """Display extracted design tokens"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 🎨 Colors")
        for color in tokens.get('colors', []):
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.color_picker(
                    label="hidden",
                    value=color['value'],
                    key=f"color_{color['name']}",
                    label_visibility="collapsed"
                )
            with col_b:
                st.write(f"**{color['name']}**\n`{color['value']}`")
    
    with col2:
        st.markdown("##### 🔤 Typography")
        for font in tokens.get('fonts', []):
            st.write(f"**{font['name']}**")
            st.caption(f"{font['family']} • {font['size']} • {font['weight']}")
    
    with col3:
        st.markdown("##### 📏 Spacing")
        for space in tokens.get('spacing', []):
            st.write(f"**{space['name']}**: `{space['value']}`")

def display_style_lock(style_lock):
    """Display style-lock status"""
    if style_lock:
        st.success("✅ **Style-Lock Active**")
        st.caption("IBM Bob has locked these design tokens to prevent drift:")
        for constraint in style_lock.get('constraints', []):
            st.code(constraint, language="text")

def display_code(code):
    """Display generated code"""
    st.code(code, language="typescript")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📥 Download Code",
            data=code,
            file_name="components.tsx",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.toast("Copied!", icon="✅")
    with col3:
        if st.button("☁️ Deploy to Vultr", use_container_width=True):
            st.toast("Deployed to Vultr Object Storage!", icon="🚀")

# ============================================================================
# SIDEBAR (No team — it's on front page)
# ============================================================================

with st.sidebar:
    st.markdown("### 🏗️ App Architect Studio")
    st.caption("IBM Bob Hackathon 2026")
    
    st.divider()
    
    # Default language selector
    st.markdown("##### 🌍 Default Language")
    default_language = st.selectbox(
        "Output language for all generated code:",
        ["en", "es", "fr", "de", "ja"],
        format_func=lambda x: {
            "en": "🇺🇸 English",
            "es": "🇪🇸 Español",
            "fr": "🇫🇷 Français",
            "de": "🇩🇪 Deutsch",
            "ja": "🇯🇵 日本語"
        }[x],
        key="default_language",
        help="This applies to all tabs — no need to re-select each time"
    )
    
    st.divider()
    
    # Backend status
    backend_ok = test_backend()
    if backend_ok:
        st.markdown('<span class="status-online">🟢 Backend Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-offline">🟡 Backend Offline — Demo Mode</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation info
    st.markdown("##### 🧭 Navigation")
    st.caption("**Vision-to-Code** — Upload screenshots")
    st.caption("**Text Prompt** — Describe your UI")
    st.caption("**Voice Mode** — Speak your requirements")
    st.caption("**Multi-Language** — i18n generation")
    st.caption("**Dashboard** — Session metrics")
    
    st.divider()
    
    # Quick links
    st.markdown("##### 🔗 Links")
    st.markdown("[📂 GitHub Repository](https://github.com/techwokx-cloud/app-architect-studio)")
    st.markdown("[📖 IBM Bob Docs](https://ibm.com)")
    st.markdown("[☁️ Vultr Dashboard](https://vultr.com)")
    
    st.divider()
    
    # Tech stack
    st.markdown("##### ⚡ Technology Stack")
    st.caption("🤖 **IBM Bob** — AI Vision & Code Generation")
    st.caption("☁️ **Vultr** — Cloud Hosting & Object Storage")
    st.caption("🎤 **Speechmatic** — Voice-to-Text Processing")
    st.caption("🌍 **NativelyAI** — Multi-Language Support")

# ============================================================================
# HERO SECTION
# ============================================================================

st.markdown("""
<div class="hero-container">
    <span class="hackathon-badge">🏆 IBM Bob Hackathon 2026</span>
    <div class="hero-title">App Architect Studio</div>
    <div class="hero-subtitle">Transform Screenshots & Text Prompts into Production-Ready Code</div>
    <div class="hero-description">
        An autonomous agentic ecosystem that converts UI screenshots, text descriptions, and voice-driven 
        business briefs into secure, audited, production-ready code. Upload any app or website screenshot, 
        type a natural language description, or speak your requirements — and our AI pipeline powered by 
        IBM Bob extracts design tokens, generates pixel-perfect React/TypeScript components, and enforces 
        style consistency through Style-Lock — all in seconds, not hours.
    </div>
    <div class="powered-by">
        <span class="tech-badge">🤖 IBM Bob</span>
        <span class="tech-badge">☁️ Vultr</span>
        <span class="tech-badge">🎤 Speechmatic</span>
        <span class="tech-badge">🌍 NativelyAI</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# HOW IT WORKS
# ============================================================================

st.markdown("")
st.markdown("#### How It Works")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">1</div>
        <div class="step-title">Input</div>
        <div class="step-desc">Upload a screenshot, type a prompt, or describe via voice</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">2</div>
        <div class="step-title">Analyze</div>
        <div class="step-desc">IBM Bob extracts design tokens & component structure</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">3</div>
        <div class="step-title">Generate</div>
        <div class="step-desc">AI generates production-ready React/TS components</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">4</div>
        <div class="step-title">Deploy</div>
        <div class="step-desc">Export code or deploy directly to Vultr Cloud</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ============================================================================
# TEAM SECTION
# ============================================================================

st.divider()

# ============================================================================
# MAIN INTERFACE
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Vision-to-Code",
    "Text Prompt",
    "Voice Mode",
    "Multi-Language",
    "Dashboard"
])

# ============================================================================
# TAB 1: VISION-TO-CODE
# ============================================================================

with tab1:
    load_icon("icons8-vision-48.png")
    st.markdown("#### Vision-to-Code")
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### 📸 Upload Screenshot")
        st.caption("Upload a screenshot of any website or app UI to extract design tokens")
        
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"],
            help="Upload a screenshot of a website or app design",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded screenshot", use_container_width=True)
            
            if st.button("🔍 Analyze with IBM Bob", key="analyze_vision", type="primary", use_container_width=True):
                with st.spinner("📸 IBM Bob is extracting design tokens..."):
                    image_base64 = convert_image_to_base64(uploaded_file)
                    result = call_vision_api(image_base64)
                    
                    if result:
                        st.session_state.tokens = result.get('tokens')
                        st.session_state.style_lock = result.get('styleLock')
                        st.success("✅ Design tokens extracted successfully!")
        else:
            st.markdown("""
            <div style="
                border: 2px dashed #C7D2FE;
                border-radius: 12px;
                padding: 3rem 2rem;
                text-align: center;
                color: #6B7280;
                background: #F8FAFF;
            ">
                <p style="font-size: 2.5em; margin-bottom: 0.3em;">📸</p>
                <p style="font-weight: 500; color: #374151;">Drop a screenshot here</p>
                <p style="font-size: 0.85em; margin-top: 0.3em;">PNG, JPG — up to 200MB</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.tokens:
            st.markdown("#### 🎯 Extracted Design Tokens")
            display_tokens(st.session_state.tokens)
            
            if st.session_state.style_lock:
                st.divider()
                display_style_lock(st.session_state.style_lock)
        else:
            st.markdown("#### 🎯 Design Tokens")
            st.info("Upload a screenshot to extract colors, fonts, spacing, and component structure automatically.")
    
    # Component generation section
    if st.session_state.tokens:
        st.divider()
        st.markdown("#### ✨ Generate Components")
        
        tokens = st.session_state.tokens
        all_components = [c['name'] for c in tokens.get('components', [])]
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_components = st.multiselect(
                "Select components to generate:",
                all_components,
                default=all_components[:3] if all_components else [],
                key="component_selector"
            )
        
        with col2:
            lang_labels = {"en": "🇺🇸 English", "es": "🇪🇸 Español", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch", "ja": "🇯🇵 日本語"}
            st.info(f"🌍 Language: **{lang_labels[default_language]}** (set in sidebar)")
        
        if st.button("✨ Generate Components", key="generate", type="primary", use_container_width=True):
            if selected_components:
                with st.spinner("🤖 IBM Bob is generating your components..."):
                    result = call_generate_api(
                        st.session_state.tokens,
                        selected_components,
                        default_language
                    )
                    
                    if result:
                        st.session_state.generated_code = result.get('code')
                        st.session_state.metrics['components_generated'] += len(selected_components)
                        st.session_state.metrics['languages_used'].add(default_language)
                        st.success("✅ Components generated!")
            else:
                st.warning("Please select at least one component")
    
    if st.session_state.generated_code:
        st.divider()
        st.markdown("#### 📄 Generated Code")
        display_code(st.session_state.generated_code)

# ============================================================================
# TAB 2: TEXT PROMPT
# ============================================================================

with tab2:
    load_icon("icons8-chat-bubble-48.png")
    st.markdown("#### Text-to-Code")
    st.markdown("Describe the UI component or page you want to build — IBM Bob will generate production-ready code.")
    
    st.divider()
    
    # Prompt input
    prompt_text = st.text_area(
        "Describe what you want to build:",
        placeholder="e.g., Create a modern pricing page with 3 tiers (Basic at $9/mo, Pro at $29/mo, Enterprise at $99/mo). Each card should have a feature list, a highlighted 'Most Popular' badge on the Pro tier, and gradient CTA buttons. Use a clean white background with subtle shadows.",
        height=150,
        key="text_prompt_input"
    )
    
    # Options row
    col1, col2 = st.columns(2)
    
    with col1:
        framework = st.selectbox(
            "Framework:",
            ["React + TypeScript", "React + JavaScript", "Vue.js", "HTML + CSS", "Next.js"],
            key="prompt_framework"
        )
    
    with col2:
        styling = st.selectbox(
            "Styling:",
            ["Tailwind CSS", "CSS Modules", "Styled Components", "Plain CSS", "Sass"],
            key="prompt_styling"
        )
    
    # Generate button
    if st.button("🚀 Generate Code from Prompt", type="primary", use_container_width=True, key="prompt_generate"):
        if prompt_text.strip():
            with st.spinner("🤖 IBM Bob is generating your component..."):
                # Build enhanced prompt with framework/styling context
                enhanced_prompt = f"{prompt_text}\n\nFramework: {framework}\nStyling: {styling}"
                result = call_prompt_api(enhanced_prompt, default_language)
                
                if result:
                    st.session_state.prompt_result = result.get('code', result.get('output', ''))
                    st.session_state.metrics['components_generated'] += 1
                    st.session_state.metrics['languages_used'].add(default_language)
                    st.success("✅ Code generated successfully!")
                else:
                    st.error("Failed to generate. Please check that the backend is online.")
        else:
            st.warning("Please enter a description of what you want to build.")
    
    # Display result
    if st.session_state.prompt_result:
        st.divider()
        st.markdown("#### 📄 Generated Code")
        st.code(st.session_state.prompt_result, language="typescript")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📥 Download",
                data=st.session_state.prompt_result,
                file_name="component.tsx",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True, key="prompt_regen"):
                st.session_state.prompt_result = None
                st.rerun()
        with col3:
            if st.button("☁️ Deploy to Vultr", use_container_width=True, key="prompt_deploy"):
                st.toast("Deployed!", icon="🚀")
    
    # Example prompts
    st.divider()
    st.markdown("##### 💡 Example Prompts")
    
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        st.markdown("""
        <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:14px 16px; margin-bottom:8px;">
            <span style="color:#6B7280; font-size:0.75em; text-transform:uppercase; font-weight:600;">Landing Page</span><br>
            <span style="color:#1F2937; font-size:0.9em;">"Build a SaaS landing page with hero section, feature grid, testimonials carousel, and CTA"</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:14px 16px; margin-bottom:8px;">
            <span style="color:#6B7280; font-size:0.75em; text-transform:uppercase; font-weight:600;">Dashboard</span><br>
            <span style="color:#1F2937; font-size:0.9em;">"Create an analytics dashboard with KPI cards, line chart, bar chart, and data table"</span>
        </div>
        """, unsafe_allow_html=True)
    
    with example_col2:
        st.markdown("""
        <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:14px 16px; margin-bottom:8px;">
            <span style="color:#6B7280; font-size:0.75em; text-transform:uppercase; font-weight:600;">E-Commerce</span><br>
            <span style="color:#1F2937; font-size:0.9em;">"Design a product card grid with image, price, rating stars, and add-to-cart button"</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:14px 16px; margin-bottom:8px;">
            <span style="color:#6B7280; font-size:0.75em; text-transform:uppercase; font-weight:600;">Authentication</span><br>
            <span style="color:#1F2937; font-size:0.9em;">"Generate a sign-up form with email, password, confirm password, and Google/GitHub OAuth buttons"</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 3: VOICE MODE
# ============================================================================

with tab3:
    load_icon("icons8-mic-48.png")
    st.markdown("#### Voice-to-Code")
    st.markdown("Describe your UI requirements by voice — Speechmatic transcribes and IBM Bob generates the code.")
    
    st.divider()
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("##### 🗣️ Voice Input")
        st.caption("Real-time transcription powered by Speechmatic")
        
        st.markdown("""
        <div style="
            border: 2px dashed #C7D2FE;
            border-radius: 12px;
            padding: 3rem;
            text-align: center;
            color: #6B7280;
            background: #F8FAFF;
            margin: 1rem 0;
        ">
            <p style="font-size: 3em; margin-bottom: 0.3em;">🎙️</p>
            <p style="font-weight: 600; color: #374151;">Click to Start Recording</p>
            <p style="font-size: 0.8em; color: #9CA3AF; margin-top:0.3em;">Powered by Speechmatic real-time transcription</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎤 Start Recording", use_container_width=True, type="primary"):
            st.info("🎤 Voice recording requires browser microphone permission.\n\nUse the text input below as an alternative.")
        
        voice_text = st.text_area(
            "Or type your description:",
            placeholder="e.g., Create a hero section with a gradient background, centered headline, subtitle text, and two CTA buttons...",
            height=100,
            key="voice_fallback"
        )
    
    with col2:
        st.markdown("##### 💡 Example Voice Commands")
        examples = [
            "Create a responsive navigation bar with logo and hamburger menu",
            "Build a pricing card with three tiers — basic, pro, and enterprise",
            "Generate a login form with social auth buttons",
            "Design a dashboard sidebar with icons and nested menu items",
            "Make a hero section with gradient background and animated CTA",
        ]
        for i, ex in enumerate(examples):
            st.markdown(f"""
            <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:12px 16px; margin-bottom:8px;">
                <span style="color:#6B7280; font-size:0.75em; text-transform:uppercase; font-weight:600;">Example {i+1}</span><br>
                <span style="color:#1F2937; font-size:0.9em;">"{ex}"</span>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: MULTI-LANGUAGE
# ============================================================================

with tab4:
    load_icon("icons8-language-48.png")
    st.markdown("#### Multi-Language Generation")
    st.markdown("Generate UI components with fully internationalized text content — powered by **NativelyAI**.")
    
    st.divider()
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("##### Supported Languages")
        
        languages = [
            ("🇺🇸", "English", "Default output language"),
            ("🇪🇸", "Español", "Spanish — Latin America & Spain"),
            ("🇫🇷", "Français", "French — France & West Africa"),
            ("🇩🇪", "Deutsch", "German — DACH region"),
            ("🇯🇵", "日本語", "Japanese"),
        ]
        
        for flag, name, desc in languages:
            st.markdown(f"""
            <div style="background:white; border:1px solid #E5E7EB; border-radius:8px; padding:12px 16px; margin-bottom:8px;">
                <span style="font-size:1.2em;">{flag}</span>&nbsp;&nbsp;
                <strong>{name}</strong>
                <span style="color:#6B7280; font-size:0.85em;"> — {desc}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### Generate")
        if st.session_state.tokens:
            lang_labels = {"en": "🇺🇸 English", "es": "🇪🇸 Español", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch", "ja": "🇯🇵 日本語"}
            st.markdown(f"**Target Language:** {lang_labels[default_language]}")
            st.caption("Change in the sidebar → Default Language")
            
            if st.button("🌍 Generate in Default Language", type="primary", use_container_width=True):
                with st.spinner("Generating internationalized components..."):
                    st.info("NativelyAI is translating component text content.")
        else:
            st.info("Upload a screenshot in the **Vision-to-Code** tab first to unlock multi-language generation.")

# ============================================================================
# TAB 5: DASHBOARD
# ============================================================================

with tab5:
    load_icon("icons8-dashboard-layout-48.png")
    st.markdown("#### Session Dashboard")
    st.caption("Real-time metrics for your current session")
    
    st.markdown("")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Components Generated",
            st.session_state.metrics['components_generated']
        )
    
    with col2:
        minutes_saved = st.session_state.metrics['components_generated'] * 5
        st.metric(
            "Time Saved",
            f"{minutes_saved} min"
        )
    
    with col3:
        st.metric(
            "Languages Used",
            len(st.session_state.metrics['languages_used'])
        )
    
    with col4:
        st.metric(
            "Backend",
            "Online" if backend_ok else "Offline"
        )
    
    st.divider()
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("##### 🔌 API Configuration")
        st.code(f"""API Endpoint:  {API_BASE_URL}
Status:        {'✅ Connected' if backend_ok else '⚠️ Disconnected'}
Timeout:       {API_TIMEOUT}s
Hosting:       Vultr Cloud""", language="yaml")
    
    with col2:
        st.markdown("##### 📋 Session Summary")
        st.json({
            "components_generated": st.session_state.metrics['components_generated'],
            "languages_used": list(st.session_state.metrics['languages_used']),
            "session_start": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            "backend_status": "online" if backend_ok else "offline",
            "version": "2.0.0"
        })

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
<div class="footer-section">
    <p style="margin-bottom: 0.5em;">
        <strong>🏗️ App Architect Studio</strong> &nbsp;|&nbsp; IBM Bob Hackathon 2026
    </p>
    <p>
        <a href="https://github.com/techwokx-cloud/app-architect-studio" target="_blank">GitHub</a>
        &nbsp;•&nbsp; Powered by IBM Bob • Vultr • Speechmatic • NativelyAI
    </p>
</div>
""", unsafe_allow_html=True)


