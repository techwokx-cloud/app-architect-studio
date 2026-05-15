README.md
IBM Bob Hackathon 2026 — Competition Entry Build production-ready apps using natural language, powered by IBM Granite on watsonx.ai

App Architect Studio is an AI-powered application builder that transforms natural language descriptions into deployable applications. Users describe what they want, and Granite generates the full tech stack — code, architecture, UI, and deployment configs.

Feature

Description

IBM Technology

🗣️ Voice-to-App

Describe your app by speaking

Speechmatics STT → Granite

💬 Chat Builder

Iterative refinement via chat

IBM Granite (watsonx.ai)

👁️ Vision Input

Upload wireframes/sketches

Granite Vision

🌍 Multilingual

Build in any language

Granite Translation

📊 Smart Layout

AI-optimized responsive UI

Granite Code

Layer

Technology

AI Engine

IBM Granite 3.3 (watsonx.ai)

Frontend

Streamlit

Speech

Speechmatics API

Storage

Vultr Object Storage

Deployment

Streamlit Community Cloud

git clone https://github.com/YOUR_USERNAME/app-architect-studio.git
cd app-architect-studio

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys

streamlit run streamlit_app.py

Service

Get It From

Purpose

IBM watsonx.ai

cloud.ibm.com

Granite AI models

Speechmatics

portal.speechmatics.com

Voice transcription

Vultr

vultr.com

Output file storage

Set these in Streamlit Cloud under Settings → Secrets using the same key names from .env.example.

app-architect-studio/
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme & server config
├── icons/                    # Feature icons (Icons8, 48px PNG)
│   ├── icons8-vision-48.png
│   ├── icons8-chat-bubble-48.png
│   ├── icons8-mic-48.png
│   ├── icons8-language-48.png
│   └── icons8-dashboard-layout-48.png
├── .env.example              # Environment variable template
├── .gitignore
└── README.md

Event: IBM Bob Hackathon 2026

Challenge: Build innovative applications using IBM Granite models

Category: Developer Tools / AI-Assisted Development

Team: TechWokx

MIT License — See LICENSE for details.

IBM watsonx.ai — Granite Foundation Models

Streamlit — Frontend framework

Speechmatics — Speech-to-text

Icons8 — UI icons
