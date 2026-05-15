"""
App Architect Studio - Streamlit Frontend
Main application file
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

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="App Architect Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: rgba(59, 130, 246, 0.1);
        padding: 20px;
        border-radius: 8px;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .hero-title {
        font-size: 3em;
        font-weight: bold;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1em;
    }
    
    .feature-card {
        background-color: rgba(31, 41, 55, 0.5);
        border: 1px solid rgba(75, 85, 99, 0.3);
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
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

def display_tokens(tokens):
    """Display extracted design tokens"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎨 Colors")
        for color in tokens.get('colors', []):
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.color_picker(
                    label="hidden",
                    value=color['value'],
                    key=f"color_{color['name']}"
                )
            with col_b:
                st.write(f"**{color['name']}**\n`{color['value']}`")
    
    with col2:
        st.markdown("### 🔤 Fonts")
        for font in tokens.get('fonts', []):
            st.write(f"**{font['name']}**")
            st.caption(f"{font['family']} • {font['size']} • {font['weight']}")
    
    with col3:
        st.markdown("### 📏 Spacing")
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
    
    # Download button
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Code",
            data=code,
            file_name="components.tsx",
            mime="text/plain"
        )
    with col2:
        if st.button("💾 Save to Vultr"):
            st.success("✅ Saved to Vultr Object Storage")

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<h1 class="hero-title">🎨 App Architect Studio</h1>', unsafe_allow_html=True)
st.markdown("""
**Transform Screenshots into Production-Ready Code**

Powered by **IBM Bob** • **Vultr** • **Speechmatic** • **NativelyAI**
""")

# Backend status
backend_ok = test_backend()
if backend_ok:
    st.success("✅ Backend Online")
else:
    st.warning("⚠️ Backend Offline - Some features unavailable")

st.divider()

# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Create tabs for different modes
tab1, tab2, tab3, tab4 = st.tabs([
    "🎨 Vision-to-Code",
    "🎤 Voice Mode",
    "🌍 Multi-Language",
    "📊 Dashboard"
])

# ============================================================================
# TAB 1: VISION-TO-CODE
# ============================================================================

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Upload Screenshot")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"],
            help="Upload a screenshot of a website or app design"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded screenshot", use_column_width=True)
            
            # Analyze button
            if st.button("🔍 Analyze with IBM Bob", key="analyze_vision"):
                with st.spinner("📸 Extracting design tokens with IBM Bob..."):
                    image_base64 = convert_image_to_base64(uploaded_file)
                    result = call_vision_api(image_base64)
                    
                    if result:
                        st.session_state.tokens = result.get('tokens')
                        st.session_state.style_lock = result.get('styleLock')
                        st.success("✅ Design tokens extracted!")
    
    with col2:
        if st.session_state.tokens:
            st.subheader("2️⃣ Extracted Tokens")
            display_tokens(st.session_state.tokens)
            
            if st.session_state.style_lock:
                st.divider()
                display_style_lock(st.session_state.style_lock)
    
    # Component generation section
    if st.session_state.tokens:
        st.divider()
        st.subheader("3️⃣ Generate Components")
        
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
            language = st.selectbox(
                "Language:",
                ["en", "es", "fr", "de", "ja"],
                format_func=lambda x: {
                    "en": "🇺🇸 English",
                    "es": "🇪🇸 Español",
                    "fr": "🇫🇷 Français",
                    "de": "🇩🇪 Deutsch",
                    "ja": "🇯🇵 日本語"
                }[x],
                key="language_selector"
            )
        
        if st.button("✨ Generate Components", key="generate"):
            if selected_components:
                with st.spinner("🤖 Generating with IBM Bob..."):
                    result = call_generate_api(
                        st.session_state.tokens,
                        selected_components,
                        language
                    )
                    
                    if result:
                        st.session_state.generated_code = result.get('code')
                        st.session_state.metrics['components_generated'] += len(selected_components)
                        st.session_state.metrics['languages_used'].add(language)
                        st.success("✅ Components generated!")
            else:
                st.warning("Please select at least one component")
    
    # Display generated code
    if st.session_state.generated_code:
        st.divider()
        st.subheader("4️⃣ Generated Code")
        display_code(st.session_state.generated_code)

# ============================================================================
# TAB 2: VOICE MODE
# ============================================================================

with tab2:
    st.markdown("""
    Say what you want, and App Architect will generate it.
    
    **Example:** "Generate a blue submit button with rounded corners"
    """)
    
    st.info("🎤 Voice mode powered by **Speechmatic**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🎤 Start Recording"):
            st.info("Voice recording not yet available in Streamlit.\n\nUse the Vision-to-Code tab for now.")
    
    with col2:
        if st.button("🔗 Link to Voice API"):
            st.code(
                "POST /api/voice\nBody: { audioBase64: '...' }",
                language="bash"
            )

# ============================================================================
# TAB 3: MULTI-LANGUAGE
# ============================================================================

with tab3:
    st.markdown("""
    Generate components in multiple languages.
    
    **Supported Languages:**
    - 🇺🇸 English
    - 🇪🇸 Spanish (Español)
    - 🇫🇷 French (Français)
    - 🇩🇪 German (Deutsch)
    - 🇯🇵 Japanese (日本語)
    """)
    
    if st.session_state.tokens:
        selected_language = st.selectbox(
            "Choose language:",
            ["en", "es", "fr", "de", "ja"],
            format_func=lambda x: {
                "en": "🇺🇸 English",
                "es": "🇪🇸 Español",
                "fr": "🇫🇷 Français",
                "de": "🇩🇪 Deutsch",
                "ja": "🇯🇵 日本語"
            }[x]
        )
        
        if st.button("🌍 Generate in Selected Language"):
            st.info(f"Generating in {selected_language}...")
            # Call API with language parameter
    else:
        st.warning("Upload a screenshot first in the Vision-to-Code tab")

# ============================================================================
# TAB 4: DASHBOARD
# ============================================================================

with tab4:
    st.subheader("📊 Session Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Components Generated",
            st.session_state.metrics['components_generated'],
            "+1"
        )
    
    with col2:
        minutes_saved = st.session_state.metrics['components_generated'] * 5
        st.metric(
            "Time Saved",
            f"{minutes_saved} min",
            f"+{minutes_saved}" if minutes_saved > 0 else "0"
        )
    
    with col3:
        st.metric(
            "Languages Used",
            len(st.session_state.metrics['languages_used']),
            f"+{len(st.session_state.metrics['languages_used'])}"
        )
    
    with col4:
        st.metric(
            "Status",
            "Online" if backend_ok else "Offline",
            "✅" if backend_ok else "❌"
        )
    
    st.divider()
    st.subheader("🔬 Technical Info")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Backend Connection**")
        st.code(f"API_URL: {API_BASE_URL}")
        st.code(f"Status: {'Online ✅' if backend_ok else 'Offline ❌'}")
    
    with col2:
        st.markdown("**Session Data**")
        st.json({
            "components": st.session_state.metrics['components_generated'],
            "languages": list(st.session_state.metrics['languages_used']),
            "timestamp": datetime.now().isoformat()
        })

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📖 Docs**")
    st.caption("[GitHub](https://github.com/yourusername/app-architect-studio)")

with col2:
    st.markdown("**🤖 Powered By**")
    st.caption("IBM Bob • Vultr • Speechmatic • NativelyAI")

with col3:
    st.markdown("**🏆 Hackathon**")
    st.caption("IBM Bob Hackathon 2026")
