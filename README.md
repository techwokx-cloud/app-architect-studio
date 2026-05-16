markdown
# 🏗️ App Architect Studio

> **IBM Bob Hackathon 2026 — Official Competition Entry**  
> *Transform Screenshots into Production-Ready Code — Instantly*

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![IBM Bob](https://img.shields.io/badge/IBM%20Bob-Powered-purple.svg)](https://www.ibm.com/watsonx)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Judges Criteria](#-judges-criteria)
- [Quick Start](#-quick-start)
- [Deployment](#-deployment)
- [Environment Variables](#-environment-variables)
- [Team](#-team)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview

**App Architect Studio** is an autonomous agentic ecosystem that converts UI screenshots and voice-driven business briefs into secure, audited, production-ready code. Powered by **IBM Bob (Granite 3.3 on watsonx.ai)** , our platform extracts design tokens (colors, fonts, spacing, components) from any screenshot and generates pixel-perfect React/TypeScript components with **Style-Lock enforcement** — all in seconds, not hours.

### The Problem We Solve

| Problem | Our Solution |
|---------|--------------|
| 🐌 Manual UI development takes days | ⚡ Generate code in seconds |
| 🎨 Design inconsistency across teams | 🔒 Style-Lock enforces design tokens |
| 🌍 Language barriers in global teams | 🗣️ Multi-language i18n support |
| 📸 Design to code translation errors | 👁️ IBM Bob vision analysis |
| 🎤 Slow requirement documentation | 💬 Voice-to-code with Speechmatic |

---

## ✨ Key Features

### 1. 👁️ Vision-to-Code
Upload any UI screenshot — IBM Bob analyzes it with repository context awareness and generates React components that match your existing codebase.

### 2. 🔒 Style-Lock Enforcement
IBM Bob locks design tokens (colors, fonts, spacing) to prevent style drift across your entire application.

### 3. 🎤 Voice-to-Code (Speechmatic Integration)
Describe your UI requirements by voice — Speechmatic transcribes in real-time, and IBM Bob generates the complete component code.

### 4. 🌍 Multi-Language i18n (NativelyAI)
Generate fully internationalized UI components with automatic text translation for 5+ languages.

### 5. ☁️ One-Click Vultr Deployment
Deploy your generated code directly to Vultr Object Storage with a single click.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **AI Engine** | IBM Bob (Granite 3.3 on watsonx.ai) | Vision analysis, code generation, style enforcement |
| **Frontend** | Streamlit | Interactive dashboard UI |
| **Backend API** | FastAPI + Uvicorn | REST API endpoints for IBM Bob |
| **Speech-to-Text** | Speechmatics API | Real-time voice transcription |
| **Translation** | NativelyAI | Multi-language UI generation |
| **Hosting** | Vultr Cloud | Backend API hosting & object storage |
| **Container** | Docker | Portable deployment |

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────┐
│ User Browser │
│ (Streamlit Cloud Frontend) │
└─────────────────────────────┬───────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Vultr VM (Backend API) │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │ FastAPI │ │ IBM Bob │ │ Style-Lock Engine │ │
│ │ (Port 8000)│◄─┤ (watsonx) │──┤ (Design Token Enforcer) │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Vultr Object Storage (Generated Code) │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ External APIs │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Speechmatic │ │ NativelyAI │ │
│ │ (Voice) │ │ (Translate) │ │
│ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘

text

---

## 🏆 Judges Criteria Compliance

| Criteria | How App Architect Studio Addresses It |
|----------|----------------------------------------|
| **Application of IBM Bob** | ✅ Vision API extracts design tokens<br>✅ Generate API creates React components<br>✅ Style-Lock enforces design consistency |
| **Clear Use of IBM Bob** | ✅ Every AI feature explicitly shows "IBM Bob" processing<br>✅ Detailed logging of all Bob API calls |
| **Presentation** | ✅ Professional animated UI<br>✅ All sponsors prominently displayed<br>✅ Team profiles with roles |
| **Business Value** | ✅ Converts screenshots → code in seconds<br>✅ Saves 5+ hours per component<br>✅ Eliminates design drift |
| **Originality** | ✅ Voice-to-code + Style-Lock + Multi-language = unique combination<br>✅ Autonomous agentic ecosystem approach |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (for backend deployment)
- API Keys (see [Environment Variables](#-environment-variables))

### Local Development

```bash
# Clone the repository
git clone https://github.com/techwokx-cloud/app-architect-studio.git
cd app-architect-studio

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the Streamlit frontend
streamlit run streamlit_app.py

# In a separate terminal, run the FastAPI backend
uvicorn fastapi_main:app --host 0.0.0.0 --port 8000 --reload
Using Docker (Production)
bash
# Build and run backend
docker build -t architect-backend .
docker run -d --name architect-backend -p 8000:8000 --env-file .env architect-backend

# Verify backend is running
curl http://localhost:8000/health
📦 Deployment
Backend (Vultr VM)
bash
ssh root@YOUR_VULTR_IP
cd /opt
git clone https://github.com/techwokx-cloud/app-architect-studio.git backend
cd backend

# Build and run
docker build -t architect-backend .
docker run -d --name architect-backend -p 8000:8000 --env-file .env architect-backend

# Open firewall
ufw allow 8000/tcp
Frontend (Streamlit Cloud)
Go to share.streamlit.io

Connect your GitHub account

Select repository: techwokx-cloud/app-architect-studio

Main file: streamlit_app.py

Add secret: API_BASE_URL = "http://YOUR_VULTR_IP:8000"

Click Deploy

🔑 Environment Variables
Create a .env file with the following:

bash
# IBM watsonx.ai (IBM Bob)
IBM_BOB_API_KEY=your_ibm_bob_api_key_here
WATSONX_PROJECT_ID=your_project_id_here

# Speechmatics (Voice-to-Text)
SPEECHMATICS_API_KEY=your_speechmatics_api_key_here

# Vultr (Object Storage)
VULTUR_ACCESS_KEY=your_vultr_access_key_here
VULTUR_SECRET_KEY=your_vultr_secret_key_here

# Optional
API_BASE_URL=http://localhost:8000
Where to Get API Keys
Service	Link	Purpose
IBM watsonx.ai	cloud.ibm.com	IBM Bob AI models
Speechmatics	portal.speechmatics.com	Voice transcription
Vultr	vultr.com	Cloud hosting & storage
📁 Project Structure
text
app-architect-studio/
├── streamlit_app.py          # Main Streamlit frontend UI
├── fastapi_main.py           # FastAPI backend with IBM Bob integration
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
├── .env.example              # Environment variable template
├── .streamlit/
│   └── config.toml           # Streamlit theme & server config
├── icons/                    # UI icons (48px PNG from Icons8)
│   ├── icons8-vision-48.png
│   ├── icons8-chat-bubble-48.png
│   ├── icons8-mic-48.png
│   ├── icons8-language-48.png
│   └── icons8-dashboard-layout-48.png
└── README.md                 # This file
👥 Team
Name	Handle	Role
Sandzhi-Garia Ochirov	@Gary04	Lead AI Engineer
Cyril Nii Teiko Tagoe	@cyril_tagoe794	Backend Developer
George Jabley	@george_jabley451	Frontend & Integration
Team TechWokx — Built for IBM Bob Hackathon 2026

🙏 Acknowledgments
IBM watsonx.ai — Granite Foundation Models & Bob API

Streamlit — Amazing frontend framework

Speechmatics — Real-time speech-to-text

NativelyAI — Multi-language translation

Vultr — Cloud hosting & object storage

Icons8 — Professional UI icons

📜 License
MIT License — See LICENSE for details.

🔗 Links
📂 GitHub Repository

🤖 IBM Bob Documentation

☁️ Vultr Cloud

🎤 Speechmatics

⭐ Show Your Support
If you find this project useful for the hackathon, please give it a star ⭐ on GitHub!

Built with 🤖 by Team TechWokx | IBM Bob Hackathon 2026

text

---

## How to Update Your GitHub Repository:

```bash
# Navigate to your local repo
cd /path/to/app-architect-studio

# Replace README.md with the new content
# (Copy the content above into README.md)

# Commit and push
git add README.md
git commit -m "docs: update README for IBM Bob Hackathon 2026 with judges criteria and deployment guide"
git push origin main
Key Sections for Judges:
Section	Why It Matters
Judges Criteria Compliance	Directly shows how you meet each criterion
Clear Use of IBM Bob	Explicitly documents Bob integration throughout
Business Value	Quantifies time savings (5+ hours per component)
Architecture Diagram	Professional system design documentation
Team Section	Clear attribution and roles
This README will make a strong impression on the judges when they review your GitHub repository!

