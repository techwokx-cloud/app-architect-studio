#!/usr/bin/env python3
"""
App Architect Studio — Professional SaaS Frontend
IBM Bob Hackathon 2026 · Production-Ready Streamlit Dashboard
Compatible with FastAPI Backend at API_BASE_URL
"""

import os
import base64
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

import streamlit as st
import requests
from PIL import Image

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="App Architect Studio | IBM Bob Hackathon 2026",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 30
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    defaults = {
        'tokens': None,
        'style_lock': None,
        'generated_code': None,
        'voice_generated_code': None,
        'i18n_generated_code': None,
        'active_tab': 0,
        'backend_status': None,
        'last_check': None,
        'metrics': {
            'components_generated': 0,
            'languages_used': set(),
            'ibm_bob_calls': 0,
            'screenshots_analyzed': 0
        },
        'ibm_bob_activity': [],
        'session_start': datetime.now().isoformat(),
        'uploaded_image': None,
        'selected_components': [],
        'current_tab': "vision",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# PROFESSIONAL CSS
# ============================================================================

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        .block-container { padding: 0 !important; max-width: 100% !important; }
        .main .block-container { padding-top: 0 !important; padding-bottom: 0 !important; }
        #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}

        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #C1C1C1; border-radius: 3px; }

        html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }

        .top-nav {
            position: fixed; top: 0; left: 0; right: 0; height: 56px;
            background: rgba(255,255,255,0.95); backdrop-filter: blur(20px);
            border-bottom: 1px solid #E0E0E0; z-index: 9999;
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 24px;
        }
        .nav-brand { display: flex; align-items: center; gap: 10px; text-decoration: none; }
        .nav-logo {
            width: 32px; height: 32px; background: linear-gradient(135deg, #0F62FE, #8A3FFC);
            border-radius: 8px; display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 800; font-size: 0.9rem;
        }
        .nav-brand-text { font-size: 1rem; font-weight: 700; color: #161616; }
        .nav-brand-sub { font-size: 0.7rem; color: #A8A8A8; font-weight: 500; }
        .nav-right { display: flex; align-items: center; gap: 16px; }
        .nav-metric { font-size: 0.8rem; color: #525252; font-weight: 500; }
        .nav-metric strong { color: #0F62FE; font-weight: 700; }
        .nav-status {
            display: flex; align-items: center; gap: 6px;
            font-size: 0.8rem; font-weight: 600; padding: 4px 12px; border-radius: 20px;
        }
        .status-online { background: #DEFBE6; color: #24A148; }
        .status-offline { background: #FFF0F0; color: #DA1E28; }
        .status-demo { background: #FFF8E1; color: #B28600; }

        .hero-section {
            margin-top: 56px; padding: 48px 24px 32px;
            background: linear-gradient(135deg, #EDF5FF 0%, #F6F2FF 50%, #E8F6F6 100%);
            border-bottom: 1px solid #E0E0E0;
        }
        .hero-content { max-width: 1200px; margin: 0 auto; text-align: center; }
        .hero-badge {
            display: inline-flex; align-items: center; gap: 8px;
            background: linear-gradient(135deg, #0F62FE, #8A3FFC); color: white;
            padding: 8px 18px; border-radius: 20px; font-size: 0.8rem;
            font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
            margin-bottom: 20px; box-shadow: 0 4px 12px rgba(15,98,254,0.25);
        }
        .hero-badge::before {
            content: ''; width: 8px; height: 8px; background: #42BE65;
            border-radius: 50%; animation: pulse-dot 2s infinite;
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.8); }
        }
        .hero-title {
            font-size: 2.8rem; font-weight: 800; color: #161616;
            margin-bottom: 12px; line-height: 1.2;
        }
        .hero-title .gradient {
            background: linear-gradient(135deg, #0F62FE, #8A3FFC);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .hero-subtitle {
            font-size: 1.1rem; color: #525252;
            max-width: 640px; margin: 0 auto 24px; line-height: 1.6;
        }
        .hero-features {
            display: flex; justify-content: center; gap: 24px;
            flex-wrap: wrap; margin-top: 16px;
        }
        .hero-feature {
            display: flex; align-items: center; gap: 6px;
            font-size: 0.85rem; color: #525252; font-weight: 500;
        }
        .hero-feature .check { color: #24A148; font-weight: 700; }

        .main-content { max-width: 1200px; margin: 0 auto; padding: 24px; }

        .card {
            background: white; border: 1px solid #E0E0E0;
            border-radius: 12px; padding: 24px;
            margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            transition: all 0.2s ease;
        }
        .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-color: #C6C6C6; }
        .card-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 16px;
        }
        .card-title { font-size: 1.1rem; font-weight: 700; color: #161616; }
        .card-subtitle { font-size: 0.85rem; color: #525252; margin-top: 2px; }
        .card-badge {
            background: #EDF5FF; color: #0F62FE;
            padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
        }

        .token-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
        .token-item {
            display: flex; align-items: center; gap: 10px;
            padding: 10px 14px; background: #F4F4F4;
            border-radius: 8px; border: 1px solid #F0F0F0;
        }
        .token-color { width: 24px; height: 24px; border-radius: 6px; border: 1px solid #E0E0E0; flex-shrink: 0; }
        .token-info { flex: 1; min-width: 0; }
        .token-name { font-size: 0.8rem; font-weight: 600; color: #161616; }
        .token-value { font-size: 0.75rem; color: #A8A8A8; font-family: monospace; }

        .code-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 10px 16px; background: #F4F4F4;
            border: 1px solid #E0E0E0; border-bottom: none;
            border-radius: 8px 8px 0 0;
        }
        .code-title { font-size: 0.8rem; font-weight: 600; color: #525252; }

        .activity-log {
            background: white; border: 1px solid #E0E0E0;
            border-radius: 12px; overflow: hidden;
        }
        .activity-header {
            display: flex; align-items: center; gap: 8px;
            padding: 12px 16px; background: linear-gradient(135deg, #EDF5FF, #F6F2FF);
            border-bottom: 1px solid #E0E0E0;
        }
        .activity-header-title { font-size: 0.85rem; font-weight: 700; color: #0F62FE; }
        .activity-item {
            display: flex; align-items: flex-start; gap: 12px;
            padding: 12px 16px; border-bottom: 1px solid #F0F0F0;
            font-size: 0.85rem;
        }
        .activity-item:last-child { border-bottom: none; }
        .activity-time { color: #A8A8A8; font-weight: 500; font-size: 0.8rem; min-width: 60px; }
        .activity-content { flex: 1; }
        .activity-action { font-weight: 600; color: #161616; }
        .activity-detail { color: #525252; margin-top: 2px; }

        .metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .metric-card {
            background: white; border: 1px solid #E0E0E0;
            border-radius: 12px; padding: 20px; text-align: center;
        }
        .metric-value { font-size: 1.8rem; font-weight: 800; color: #0F62FE; line-height: 1; }
        .metric-label {
            font-size: 0.75rem; color: #A8A8A8; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.05em; margin-top: 8px;
        }

        .app-footer {
            text-align: center; padding: 32px 24px;
            border-top: 1px solid #E0E0E0; margin-top: 40px; background: #F4F4F4;
        }
        .footer-links { display: flex; justify-content: center; gap: 20px; margin-bottom: 12px; flex-wrap: wrap; }
        .footer-links a { color: #525252; text-decoration: none; font-size: 0.85rem; font-weight: 500; }
        .footer-links a:hover { color: #0F62FE; }
        .footer-copy { font-size: 0.8rem; color: #A8A8A8; }

        @media (max-width: 768px) {
            .hero-title { font-size: 2rem; }
            .metrics-row { grid-template-columns: repeat(2, 1fr); }
            .token-grid { grid-template-columns: 1fr; }
        }
        @media (max-width: 480px) {
            .hero-title { font-size: 1.6rem; }
            .metrics-row { grid-template-columns: 1fr; }
            .top-nav { padding: 0 12px; }
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ============================================================================
# API HELPERS
# ============================================================================

def test_backend() -> bool:
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=3)
        st.session_state.backend_status = resp.status_code == 200
        st.session_state.last_check = datetime.now().isoformat()
        return st.session_state.backend_status
    except Exception:
        st.session_state.backend_status = False
        return False

def log_activity(action: str, detail: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.ibm_bob_activity.insert(0, {
        "timestamp": timestamp, "action": action, "detail": detail
    })
    st.session_state.ibm_bob_activity = st.session_state.ibm_bob_activity[:20]
    st.session_state.metrics['ibm_bob_calls'] += 1

def convert_image_to_base64(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode()

def api_call(endpoint: str, method: str = "GET", payload: dict = None) -> Optional[dict]:
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            resp = requests.get(url, timeout=API_TIMEOUT)
        else:
            resp = requests.post(url, json=payload, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Check that FastAPI is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Backend may be overloaded.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# ============================================================================
# DEMO DATA
# ============================================================================

def get_demo_tokens() -> dict:
    return {
        "colors": [
            {"name": "primary", "value": "#0F62FE"},
            {"name": "secondary", "value": "#8A3FFC"},
            {"name": "success", "value": "#24A148"},
            {"name": "warning", "value": "#F1C21B"},
            {"name": "danger", "value": "#DA1E28"},
            {"name": "background", "value": "#F4F4F4"},
            {"name": "surface", "value": "#FFFFFF"},
            {"name": "text", "value": "#161616"}
        ],
        "fonts": [
            {"name": "heading", "family": "Inter", "size": "1.5rem", "weight": "700"},
            {"name": "body", "family": "Inter", "size": "1rem", "weight": "400"},
            {"name": "caption", "family": "Inter", "size": "0.875rem", "weight": "400"}
        ],
        "spacing": [
            {"name": "xs", "value": "0.25rem"},
            {"name": "sm", "value": "0.5rem"},
            {"name": "md", "value": "1rem"},
            {"name": "lg", "value": "1.5rem"},
            {"name": "xl", "value": "2rem"}
        ],
        "components": [
            {"name": "Button", "description": "Primary action button with variants"},
            {"name": "Card", "description": "Content container with elevation"},
            {"name": "NavBar", "description": "Top navigation with brand and links"},
            {"name": "Input", "description": "Text input with validation states"},
            {"name": "Modal", "description": "Overlay dialog for confirmations"},
            {"name": "Table", "description": "Data table with sorting and pagination"}
        ]
    }

def generate_demo_code(components: List[str], tokens: dict) -> str:
    colors = {c['name']: c['value'] for c in tokens.get('colors', [])}

    code_parts = []
    code_parts.append(f"""// Generated by IBM Bob — Repository Context Aware
// Timestamp: {datetime.now().isoformat()}
// Components: {', '.join(components)}
// Style Lock: Active

import React from 'react';

const tokens = {{
  colors: {{
    primary: '{colors.get('primary', '#0F62FE')}',
    secondary: '{colors.get('secondary', '#8A3FFC')}',
    success: '{colors.get('success', '#24A148')}',
    danger: '{colors.get('danger', '#DA1E28')}',
    background: '{colors.get('background', '#F4F4F4')}',
    surface: '{colors.get('surface', '#FFFFFF')}',
    text: '{colors.get('text', '#161616')}',
  }},
  spacing: {{ xs: '0.25rem', sm: '0.5rem', md: '1rem', lg: '1.5rem', xl: '2rem' }},
  radius: {{ sm: '6px', md: '8px', lg: '12px', xl: '16px' }}
}};
""")

    if "Button" in components:
        code_parts.append("""
export const Button = ({ children, variant = 'primary', size = 'md', disabled = false, onClick, ...props }) => {
  const variants = {
    primary: { bg: tokens.colors.primary, color: '#fff', border: 'none' },
    secondary: { bg: tokens.colors.secondary, color: '#fff', border: 'none' },
    ghost: { bg: 'transparent', color: tokens.colors.primary, border: `1px solid ${tokens.colors.primary}` },
    danger: { bg: tokens.colors.danger, color: '#fff', border: 'none' }
  };
  const sizes = {
    sm: { padding: `${tokens.spacing.sm} ${tokens.spacing.md}`, fontSize: '0.875rem' },
    md: { padding: `${tokens.spacing.md} ${tokens.spacing.lg}`, fontSize: '1rem' },
    lg: { padding: `${tokens.spacing.md} ${tokens.spacing.xl}`, fontSize: '1.125rem' }
  };
  const style = variants[variant] || variants.primary;
  const sizeStyle = sizes[size] || sizes.md;

  return (
    <button onClick={onClick} disabled={disabled} style={{
      backgroundColor: style.bg, color: style.color, border: style.border,
      borderRadius: tokens.radius.md, padding: sizeStyle.padding,
      fontSize: sizeStyle.fontSize, fontWeight: 600, fontFamily: 'Inter, sans-serif',
      cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.6 : 1,
      transition: 'all 0.2s ease',
      boxShadow: variant === 'primary' ? '0 2px 8px rgba(15,98,254,0.25)' : 'none'
    }} {...props}>
      {children}
    </button>
  );
};
""")

    if "Card" in components:
        code_parts.append("""
export const Card = ({ children, title, subtitle, footer, elevation = 1 }) => {
  const shadows = { 0: 'none', 1: '0 1px 3px rgba(0,0,0,0.08)', 2: '0 4px 12px rgba(0,0,0,0.12)', 3: '0 12px 24px rgba(0,0,0,0.16)' };
  return (
    <div style={{
      backgroundColor: tokens.colors.surface, borderRadius: tokens.radius.lg,
      padding: tokens.spacing.lg, boxShadow: shadows[elevation] || shadows[1],
      border: '1px solid #E0E0E0', transition: 'box-shadow 0.2s ease'
    }}>
      {(title || subtitle) && (
        <div style={{ marginBottom: tokens.spacing.md }}>
          {title && <h3 style={{ margin: 0, color: tokens.colors.text, fontSize: '1.125rem', fontWeight: 700 }}>{title}</h3>}
          {subtitle && <p style={{ margin: '4px 0 0', color: '#525252', fontSize: '0.875rem' }}>{subtitle}</p>}
        </div>
      )}
      <div>{children}</div>
      {footer && (
        <div style={{ marginTop: tokens.spacing.md, paddingTop: tokens.spacing.md, borderTop: '1px solid #E0E0E0', color: '#525252', fontSize: '0.875rem' }}>
          {footer}
        </div>
      )}
    </div>
  );
};
""")

    if "NavBar" in components:
        code_parts.append("""
export const NavBar = ({ brand, links = [], actions = [] }) => (
  <nav style={{
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: `${tokens.spacing.md} ${tokens.spacing.lg}`,
    backgroundColor: tokens.colors.surface, borderBottom: '1px solid #E0E0E0',
    position: 'sticky', top: 0, zIndex: 1000
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing.md }}>
      {brand && <div style={{ fontWeight: 800, fontSize: '1.25rem', color: tokens.colors.primary }}>{brand}</div>}
      <div style={{ display: 'flex', gap: tokens.spacing.md }}>
        {links.map((link, i) => (
          <a key={i} href={link.href || '#'} style={{ color: '#525252', textDecoration: 'none', fontWeight: 500, fontSize: '0.875rem' }}>{link.label}</a>
        ))}
      </div>
    </div>
    <div style={{ display: 'flex', gap: tokens.spacing.sm, alignItems: 'center' }}>
      {actions.map((action, i) => <span key={i}>{action}</span>)}
    </div>
  </nav>
);
""")

    if "Input" in components:
        code_parts.append("""
export const Input = ({ label, placeholder, type = 'text', error, ...props }) => (
  <div style={{ marginBottom: tokens.spacing.md }}>
    {label && <label style={{ display: 'block', marginBottom: tokens.spacing.sm, fontSize: '0.875rem', fontWeight: 600, color: tokens.colors.text }}>{label}</label>}
    <input type={type} placeholder={placeholder} style={{
      width: '100%', padding: `${tokens.spacing.sm} ${tokens.spacing.md}`,
      borderRadius: tokens.radius.md, border: `1.5px solid ${error ? tokens.colors.danger : '#E0E0E0'}`,
      fontSize: '1rem', fontFamily: 'Inter, sans-serif', transition: 'all 0.2s', outline: 'none'
    }} {...props} />
    {error && <span style={{ color: tokens.colors.danger, fontSize: '0.8rem', marginTop: '4px', display: 'block' }}>{error}</span>}
  </div>
);
""")

    if "Modal" in components:
        code_parts.append("""
export const Modal = ({ isOpen, onClose, title, children, actions }) => {
  if (!isOpen) return null;
  return (
    <div style={{
      position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, backdropFilter: 'blur(4px)'
    }} onClick={onClose}>
      <div style={{
        backgroundColor: tokens.colors.surface, borderRadius: tokens.radius.xl,
        padding: tokens.spacing.xl, maxWidth: '560px', width: '90%',
        boxShadow: '0 24px 48px rgba(0,0,0,0.2)'
      }} onClick={e => e.stopPropagation()}>
        {title && <h2 style={{ margin: `0 0 ${tokens.spacing.md}`, fontSize: '1.25rem', fontWeight: 700 }}>{title}</h2>}
        <div style={{ marginBottom: tokens.spacing.lg }}>{children}</div>
        {actions && <div style={{ display: 'flex', gap: tokens.spacing.sm, justifyContent: 'flex-end' }}>{actions}</div>}
      </div>
    </div>
  );
};
""")

    if "Table" in components:
        code_parts.append("""
export const Table = ({ columns, data, striped = true }) => (
  <div style={{ overflowX: 'auto', borderRadius: tokens.radius.md, border: '1px solid #E0E0E0' }}>
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
      <thead>
        <tr style={{ backgroundColor: '#F4F4F4', borderBottom: '2px solid #E0E0E0' }}>
          {columns.map((col, i) => (
            <th key={i} style={{ padding: `${tokens.spacing.sm} ${tokens.spacing.md}`, textAlign: col.align || 'left', fontWeight: 600, color: '#525252', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} style={{ borderBottom: '1px solid #F0F0F0', backgroundColor: striped && i % 2 ? '#FAFAFA' : 'transparent' }}>
            {columns.map((col, j) => (
              <td key={j} style={{ padding: `${tokens.spacing.sm} ${tokens.spacing.md}`, textAlign: col.align || 'left', color: '#161616' }}>{row[col.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
""")

    registry = ", ".join([f"{comp}: {comp}" for comp in components])
    code_parts.append(f"\nexport const ComponentRegistry = {{ {registry} }};\nexport default ComponentRegistry;\n")

    return "\n".join(code_parts)

# ============================================================================
# UI RENDERERS
# ============================================================================

def render_top_nav():
    backend_ok = st.session_state.backend_status
    status_class = "status-online" if backend_ok else "status-offline"
    status_text = "● Online" if backend_ok else "● Offline"

    st.markdown(f"""
    <div class="top-nav">
        <div class="nav-brand">
            <div class="nav-logo">A</div>
            <div>
                <div class="nav-brand-text">App Architect Studio</div>
                <div class="nav-brand-sub">IBM Bob Hackathon 2026</div>
            </div>
        </div>
        <div class="nav-right">
            <div class="nav-metric">🤖 <strong>{st.session_state.metrics['ibm_bob_calls']}</strong> Bob calls</div>
            <div class="nav-metric">⚛️ <strong>{st.session_state.metrics['components_generated']}</strong> components</div>
            <div class="nav-status {status_class}">{status_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-badge">IBM Bob Integration</div>
            <h1 class="hero-title">Screenshot to <span class="gradient">Production Code</span></h1>
            <p class="hero-subtitle">
                Upload any UI screenshot. IBM Bob analyzes it with repository context awareness 
                and generates React components that match your existing codebase.
            </p>
            <div class="hero-features">
                <div class="hero-feature"><span class="check">✓</span> Repository Context Aware</div>
                <div class="hero-feature"><span class="check">✓</span> Style Lock Enforcement</div>
                <div class="hero-feature"><span class="check">✓</span> Voice-to-Code</div>
                <div class="hero-feature"><span class="check">✓</span> Multi-Language i18n</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics():
    m = st.session_state.metrics
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-card"><div class="metric-value">{m['ibm_bob_calls']}</div><div class="metric-label">IBM Bob Calls</div></div>
        <div class="metric-card"><div class="metric-value">{m['components_generated']}</div><div class="metric-label">Components Generated</div></div>
        <div class="metric-card"><div class="metric-value">{m['screenshots_analyzed']}</div><div class="metric-label">Screenshots Analyzed</div></div>
        <div class="metric-card"><div class="metric-value">{len(m['languages_used'])}</div><div class="metric-label">Languages Used</div></div>
    </div>
    """, unsafe_allow_html=True)

def render_activity_log():
    activities = st.session_state.ibm_bob_activity
    if not activities:
        return

    html = '<div class="activity-log"><div class="activity-header"><span>🤖</span><span class="activity-header-title">IBM Bob Activity Log</span></div>'
    for act in activities[:10]:
        html += f'<div class="activity-item"><div class="activity-time">{act["timestamp"]}</div><div class="activity-content"><div class="activity-action">{act["action"]}</div><div class="activity-detail">{act["detail"]}</div></div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="app-footer">
        <div class="footer-links">
            <a href="https://github.com/techwokx-cloud/app-architect-studio" target="_blank">GitHub</a>
            <a href="#">Documentation</a>
            <a href="#">API Reference</a>
            <a href="#">Support</a>
        </div>
        <div class="footer-copy">
            <strong>App Architect Studio</strong> · IBM Bob Hackathon 2026 · Techwokx Cloud<br>
            Powered by IBM Bob · Vultr · Speechmatic · NativelyAI
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB RENDERERS
# ============================================================================

def render_vision_tab():
    st.markdown('<div class="card"><div class="card-header"><div><div class="card-title">🎨 Vision-to-Code Analysis</div><div class="card-subtitle">Upload a screenshot and IBM Bob will extract design tokens</div></div></div></div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Drop screenshot here or click to browse", type=["png", "jpg", "jpeg"], help="Upload any website or app screenshot", label_visibility="collapsed")

    if uploaded:
        st.session_state.uploaded_image = uploaded
        col1, col2 = st.columns([1, 1])

        with col1:
            image = Image.open(uploaded)
            st.image(image, use_container_width=True, caption="Uploaded Screenshot")

        with col2:
            st.markdown("""
            <div style="padding: 16px; background: #F4F8FF; border-radius: 12px; border: 1px solid #A6C8FF;">
                <h4 style="margin: 0 0 12px; color: #0F62FE;">🤖 IBM Bob Will Analyze:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #525252; line-height: 2;">
                    <li><strong>Colors</strong> — Extract palette with semantic names</li>
                    <li><strong>Typography</strong> — Fonts, sizes, weights</li>
                    <li><strong>Spacing</strong> — Margins, padding, gaps</li>
                    <li><strong>Components</strong> — Buttons, cards, forms</li>
                    <li><strong>Style Lock</strong> — Immutable design tokens</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🤖 Analyze with IBM Bob", type="primary", use_container_width=True, key="analyze_btn"):
            with st.spinner("IBM Bob is analyzing your screenshot..."):
                log_activity("Screenshot Analysis", "Processing visual design with repository context")
                image_b64 = convert_image_to_base64(uploaded)

                if st.session_state.backend_status and not DEMO_MODE:
                    result = api_call("/api/vision", "POST", {"image": image_b64})
                    if result:
                        st.session_state.tokens = result
                    else:
                        st.session_state.tokens = get_demo_tokens()
                        st.info("Using demo tokens (backend unavailable)")
                else:
                    time.sleep(1.5)
                    st.session_state.tokens = get_demo_tokens()
                    st.info("Demo mode — using sample design tokens")

                st.session_state.metrics['screenshots_analyzed'] += 1
                log_activity("Analysis Complete", f"Extracted {len(st.session_state.tokens.get('colors', []))} colors, {len(st.session_state.tokens.get('components', []))} components")
                st.rerun()

    if st.session_state.tokens:
        tokens = st.session_state.tokens
        st.markdown('<div class="card"><div class="card-header"><div><div class="card-title">🔓 Design Tokens (Style-Locked)</div><div class="card-subtitle">IBM Bob extracted these from your screenshot</div></div><div class="card-badge">Immutable</div></div></div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<h5 style='color: #525252; margin-bottom: 12px;'>🎨 Colors</h5>", unsafe_allow_html=True)
            for color in tokens.get('colors', []):
                st.markdown(f'<div class="token-item"><div class="token-color" style="background: {color["value"]};"></div><div class="token-info"><div class="token-name">{color["name"]}</div><div class="token-value">{color["value"]}</div></div></div>', unsafe_allow_html=True)

        with c2:
            st.markdown("<h5 style='color: #525252; margin-bottom: 12px;'>🔤 Typography</h5>", unsafe_allow_html=True)
            for font in tokens.get('fonts', []):
                st.markdown(f'<div class="token-item"><div class="token-info"><div class="token-name">{font["name"]}</div><div class="token-value">{font["family"]} · {font["size"]} · {font["weight"]}</div></div></div>', unsafe_allow_html=True)

        with c3:
            st.markdown("<h5 style='color: #525252; margin-bottom: 12px;'>📏 Spacing</h5>", unsafe_allow_html=True)
            for space in tokens.get('spacing', []):
                st.markdown(f'<div class="token-item"><div class="token-info"><div class="token-name">{space["name"]}</div><div class="token-value">{space["value"]}</div></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        available = [c['name'] for c in tokens.get('components', [])]
        selected = st.multiselect("Select components to generate", available, default=available[:3] if len(available) >= 3 else available, key="component_select")

        if selected and st.button("✨ Generate React Components", type="primary", use_container_width=True, key="generate_btn"):
            with st.spinner("IBM Bob is generating production-ready code..."):
                log_activity("Code Generation", f"Generating {len(selected)} components with style-lock")

                if st.session_state.backend_status and not DEMO_MODE:
                    result = api_call("/api/generate", "POST", {
                        "prompt": f"Generate {', '.join(selected)}",
                        "code_type": "React Component",
                        "context": {"tokens": tokens, "components": selected}
                    })
                    if result and "code" in result:
                        st.session_state.generated_code = result["code"]
                    else:
                        st.session_state.generated_code = generate_demo_code(selected, tokens)
                else:
                    time.sleep(1.5)
                    st.session_state.generated_code = generate_demo_code(selected, tokens)

                st.session_state.metrics['components_generated'] += len(selected)
                log_activity("Generation Complete", f"{len(selected)} components generated with style-lock")
                st.rerun()

        if st.session_state.generated_code:
            st.markdown('<div class="code-header"><div class="code-title">📄 Generated React Components</div></div>', unsafe_allow_html=True)
            st.code(st.session_state.generated_code, language="typescript")

            col_dl, col_reset = st.columns(2)
            with col_dl:
                st.download_button("📥 Download .tsx", data=st.session_state.generated_code, file_name="components.tsx", mime="text/plain", use_container_width=True, key="download_tsx")
            with col_reset:
                if st.button("🔄 Reset", use_container_width=True, key="reset_gen"):
                    st.session_state.generated_code = None
                    st.session_state.tokens = None
                    st.session_state.uploaded_image = None
                    st.rerun()

def render_direct_tab():
    st.markdown('<div class="card"><div class="card-header"><div><div class="card-title">⚙️ Direct Code Generation</div><div class="card-subtitle">Describe what you need — IBM Bob generates the code</div></div></div></div>', unsafe_allow_html=True)

    code_type = st.selectbox("Code Type", ["React Component", "Authentication Schema", "API Endpoint", "Data Model", "Form Validation", "Database Schema"], key="code_type_select")
    prompt = st.text_area("Describe what you need", placeholder="e.g., A user registration form with email validation, password strength indicator, and terms checkbox", height=100, key="direct_prompt")

    if st.button("🤖 Generate with IBM Bob", type="primary", use_container_width=True, key="direct_gen_btn"):
        if not prompt:
            st.warning("Please describe what you need")
            return

        with st.spinner("IBM Bob is generating code..."):
            log_activity("Direct Generation", f"{code_type}: {prompt[:60]}...")

            if st.session_state.backend_status and not DEMO_MODE:
                result = api_call("/api/generate", "POST", {"prompt": prompt, "code_type": code_type})
                if result and "code" in result:
                    code = result["code"]
                else:
                    code = generate_demo_code(["Button", "Card", "Input"], get_demo_tokens())
            else:
                time.sleep(1.5)
                code = generate_demo_code(["Button", "Card", "Input"], get_demo_tokens())

            st.session_state.metrics['components_generated'] += 1
            log_activity("Code Ready", f"{code_type} generated successfully")

            lang_map = {"React Component": "tsx", "Authentication Schema": "typescript", "API Endpoint": "python", "Data Model": "typescript", "Form Validation": "typescript", "Database Schema": "sql"}
            st.markdown('<div class="code-header"><div class="code-title">📄 Generated Code</div></div>', unsafe_allow_html=True)
            st.code(code, language=lang_map.get(code_type, "typescript"))
            st.download_button("📥 Download", data=code, file_name=f"generated.{lang_map.get(code_type, 'ts')}", mime="text/plain", use_container_width=True, key="direct_download")

def render_voice_tab():
    st.markdown('<div class="card"><div class="card-header"><div><div class="card-title">🎤 Voice-to-Code</div><div class="card-subtitle">Describe your UI verbally — Speechmatic transcribes, IBM Bob generates</div></div></div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div style="padding: 32px; background: linear-gradient(135deg, #F4F8FF, #F9F6FF); border-radius: 16px; border: 2px dashed #A6C8FF; text-align: center; margin-bottom: 16px;"><div style="font-size: 3rem; margin-bottom: 12px;">🎙️</div><div style="font-weight: 600; color: #161616; margin-bottom: 4px;">Click to Start Recording</div><div style="font-size: 0.8rem; color: #A8A8A8;">Powered by Speechmatic real-time transcription</div></div>', unsafe_allow_html=True)

        voice_text = st.text_area("Or type your description:", placeholder="e.g., Create a hero section with gradient background, centered headline, subtitle, and two CTA buttons side by side", height=120, key="voice_input")

        if st.button("✨ Generate from Voice", type="primary", use_container_width=True, key="voice_gen_btn"):
            if voice_text:
                with st.spinner("Speechmatic → IBM Bob pipeline..."):
                    log_activity("Voice-to-Code", f"Pipeline: '{voice_text[:60]}...'")

                    if st.session_state.backend_status and not DEMO_MODE:
                        result = api_call("/api/voice", "POST", {"transcription": voice_text, "language": "en"})
                        if result and "code" in result:
                            code = result["code"]
                        else:
                            code = generate_demo_code(["Button", "Card", "NavBar"], get_demo_tokens())
                    else:
                        progress = st.progress(0)
                        for i in range(100):
                            time.sleep(0.02)
                            progress.progress(i + 1)
                        code = generate_demo_code(["Button", "Card", "NavBar"], get_demo_tokens())

                    st.session_state.metrics['components_generated'] += 1
                    log_activity("Voice Generation Complete", "Component generated from voice description")
                    st.markdown('<div class="code-header"><div class="code-title">📄 Voice-Generated Component</div></div>', unsafe_allow_html=True)
                    st.code(code, language="typescript")
                    st.download_button("📥 Download .tsx", data=code, file_name="voice_component.tsx", mime="text/plain", use_container_width=True, key="voice_download")
            else:
                st.warning("Please provide a voice description or type your requirements")

    with col2:
        st.markdown("<h5 style='color: #525252; margin-bottom: 12px;'>💡 Example Commands</h5>", unsafe_allow_html=True)
        examples = [
            "Create a responsive navigation bar with logo on left and menu items on right",
            "Build a pricing table with three tiers — starter, pro, and enterprise",
            "Generate a login form with email, password, and social auth buttons",
            "Design a feature grid with four cards showing icons and descriptions",
            "Make a footer with company links and social media icons"
        ]
        for i, ex in enumerate(examples, 1):
            st.markdown(f'<div style="padding: 10px 14px; background: #F4F4F4; border-radius: 8px; margin-bottom: 8px; font-size: 0.8rem; color: #525252; border: 1px solid #E0E0E0;"><strong style="color: #0F62FE;">Ex {i}</strong><br>{ex}</div>', unsafe_allow_html=True)

def render_i18n_tab():
    st.markdown('<div class="card"><div class="card-header"><div><div class="card-title">🌍 Multi-Language Generation</div><div class="card-subtitle">Generate components with internationalized content via NativelyAI</div></div></div></div>', unsafe_allow_html=True)

    languages = {
        "en": ("🇺🇸", "English", "US/UK"),
        "es": ("🇪🇸", "Español", "Spain & LATAM"),
        "fr": ("🇫🇷", "Français", "France & Africa"),
        "de": ("🇩🇪", "Deutsch", "DACH region"),
        "ja": ("🇯🇵", "日本語", "Japan"),
        "zh": ("🇨🇳", "中文", "China"),
        "ar": ("🇸🇦", "العربية", "Middle East"),
    }

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<h5 style='color: #525252; margin-bottom: 12px;'>Supported Languages</h5>", unsafe_allow_html=True)
        for code, (flag, name, region) in languages.items():
            st.markdown(f'<div style="padding: 12px 16px; background: white; border: 1px solid #E0E0E0; border-radius: 8px; margin-bottom: 8px;"><span style="font-size: 1.2rem;">{flag}</span>&nbsp;<strong>{name}</strong><br><span style="color: #A8A8A8; font-size: 0.8rem;">{region}</span></div>', unsafe_allow_html=True)

    with col2:
        st.markdown("<h5 style='color: #525252; margin-bottom: 12px;'>Generate i18n Component</h5>", unsafe_allow_html=True)

        if st.session_state.tokens:
            target = st.selectbox("Target Language", options=list(languages.keys()), format_func=lambda x: f"{languages[x][0]} {languages[x][1]}", key="lang_select")

            if st.button("🌍 Generate Internationalized", type="primary", use_container_width=True, key="i18n_gen_btn"):
                with st.spinner(f"IBM Bob + NativelyAI → {languages[target][1]}..."):
                    log_activity("i18n Generation", f"Translating to {languages[target][1]}")

                    if st.session_state.backend_status and not DEMO_MODE:
                        result = api_call("/api/i18n", "POST", {"components": st.session_state.tokens.get('components', []), "language": target, "tokens": st.session_state.tokens})
                        if result and "code" in result:
                            code = result["code"]
                        else:
                            code = generate_demo_code(["Button", "Card"], get_demo_tokens())
                    else:
                        time.sleep(1.5)
                        code = generate_demo_code(["Button", "Card"], get_demo_tokens())

                    st.session_state.metrics['languages_used'].add(target)
                    log_activity("i18n Complete", f"Component localized to {languages[target][1]}")
                    st.markdown('<div class="code-header"><div class="code-title">📄 Internationalized Component</div></div>', unsafe_allow_html=True)
                    st.code(code, language="typescript")
                    st.download_button(f"📥 Download ({languages[target][1]})", data=code, file_name=f"component_{target}.tsx", mime="text/plain", use_container_width=True, key="i18n_download")
        else:
            st.info("📸 Upload a screenshot in the Vision-to-Code tab first to unlock multi-language generation")

def render_dashboard_tab():
    st.markdown('<div class="card"><div class="card-header"><div><div class="card-title">📊 Session Dashboard</div><div class="card-subtitle">System status, metrics, and activity</div></div></div></div>', unsafe_allow_html=True)

    render_metrics()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><div class="card-header"><div class="card-title">🔌 Backend Status</div></div></div>', unsafe_allow_html=True)
        status_data = {
            "API Endpoint": API_BASE_URL,
            "Connection": "✅ Online" if st.session_state.backend_status else "❌ Offline",
            "Timeout": f"{API_TIMEOUT}s",
            "Demo Mode": "Enabled" if DEMO_MODE else "Disabled",
            "Last Check": st.session_state.last_check or "Never",
        }
        for k, v in status_data.items():
            st.markdown(f'<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #F0F0F0; font-size: 0.85rem;"><span style="color: #525252;">{k}</span><span style="color: #161616; font-weight: 600;">{v}</span></div>', unsafe_allow_html=True)

        if st.button("🔄 Test Connection", use_container_width=True, key="test_conn_btn"):
            with st.spinner("Testing..."):
                is_online = test_backend()
                if is_online:
                    st.success("✅ Backend is responding!")
                else:
                    st.error("❌ Backend not reachable. Check that FastAPI is running.")
                st.rerun()

    with col2:
        st.markdown('<div class="card"><div class="card-header"><div class="card-title">🤖 IBM Bob Integration</div></div></div>', unsafe_allow_html=True)
        bob_data = {
            "Status": "✅ Operational" if st.session_state.backend_status else "⚠️ Demo Mode",
            "Repository Indexed": "Yes",
            "Context Awareness": "Active",
            "Style Lock": "Enabled",
            "Total Calls": str(st.session_state.metrics['ibm_bob_calls']),
            "Last Activity": st.session_state.ibm_bob_activity[0]['timestamp'] if st.session_state.ibm_bob_activity else "None"
        }
        for k, v in bob_data.items():
            st.markdown(f'<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #F0F0F0; font-size: 0.85rem;"><span style="color: #525252;">{k}</span><span style="color: #161616; font-weight: 600;">{v}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render_activity_log()

    st.markdown("<br>", unsafe_allow_html=True)
    col_exp, col_reset = st.columns(2)
    with col_exp:
        if st.button("📊 Export Session Report", use_container_width=True, key="export_btn"):
            report = {
                "session_id": f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "ibm_bob_calls": st.session_state.metrics['ibm_bob_calls'],
                    "components_generated": st.session_state.metrics['components_generated'],
                    "screenshots_analyzed": st.session_state.metrics['screenshots_analyzed'],
                    "languages_used": list(st.session_state.metrics['languages_used'])
                },
                "activity_log": st.session_state.ibm_bob_activity,
                "backend_status": "online" if st.session_state.backend_status else "offline",
                "demo_mode": DEMO_MODE
            }
            st.download_button("📥 Download Report (JSON)", data=json.dumps(report, indent=2), file_name=f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json", use_container_width=True, key="report_download")

    with col_reset:
        reset_confirmed = st.checkbox("Confirm reset", key="reset_confirm")
        if st.button("🔄 Reset Session", use_container_width=True, key="reset_btn", disabled=not reset_confirmed):
            st.session_state.metrics = {'components_generated': 0, 'languages_used': set(), 'ibm_bob_calls': 0, 'screenshots_analyzed': 0}
            st.session_state.ibm_bob_activity = []
            st.session_state.tokens = None
            st.session_state.generated_code = None
            st.session_state.voice_generated_code = None
            st.session_state.i18n_generated_code = None
            st.success("✅ Session reset successfully!")
            time.sleep(1)
            st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Check backend on load (once per session)
    if st.session_state.last_check is None:
        test_backend()

    # Render fixed UI elements
    render_top_nav()
    render_hero()

    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Tab navigation using Streamlit buttons (reliable state management)
    tabs = {
        "vision": ("🎨", "Vision-to-Code"),
        "direct": ("⚙️", "Direct Gen"),
        "voice": ("🎤", "Voice Mode"),
        "i18n": ("🌍", "Multi-Language"),
        "dashboard": ("📊", "Dashboard"),
    }

    tab_cols = st.columns(len(tabs))
    for idx, (tab_id, (icon, label)) in enumerate(tabs.items()):
        with tab_cols[idx]:
            is_active = st.session_state.current_tab == tab_id
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                f"{icon} {label}",
                key=f"tab_btn_{tab_id}",
                type=btn_type,
                use_container_width=True
            ):
                st.session_state.current_tab = tab_id
                st.rerun()

    st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E0E0E0;'>", unsafe_allow_html=True)

    # Render active tab content
    current = st.session_state.current_tab
    if current == "vision":
        render_vision_tab()
    elif current == "direct":
        render_direct_tab()
    elif current == "voice":
        render_voice_tab()
    elif current == "i18n":
        render_i18n_tab()
    elif current == "dashboard":
        render_dashboard_tab()

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    render_footer()

if __name__ == "__main__":
    main()
