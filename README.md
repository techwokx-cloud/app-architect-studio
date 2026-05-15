# 🏗️ App Architect Studio

> **IBM Bob Hackathon 2026 — Competition Entry**
> Build production-ready apps using natural language, powered by IBM Granite on watsonx.ai

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-architect-studio.streamlit.app)

---

## 🎯 What It Does

App Architect Studio is an AI-powered application builder that transforms natural language descriptions into deployable applications. Users describe what they want, and Granite generates the full tech stack — code, architecture, UI, and deployment configs.

### Key Features

| Feature | Description | IBM Technology |
|---------|-------------|----------------|
| 🗣️ **Voice-to-App** | Describe your app by speaking | Speechmatics STT → Granite |
| 💬 **Chat Builder** | Iterative refinement via chat | IBM Granite (watsonx.ai) |
| 👁️ **Vision Input** | Upload wireframes/sketches | Granite Vision |
| 🌍 **Multilingual** | Build in any language | Granite Translation |
| 📊 **Smart Layout** | AI-optimized responsive UI | Granite Code |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Engine** | IBM Granite 3.3 (watsonx.ai) |
| **Frontend** | Streamlit |
| **Speech** | Speechmatics API |
| **Storage** | Vultr Object Storage |
| **Deployment** | Streamlit Community Cloud |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/app-architect-studio.git
cd app-architect-studio
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run locally
```bash
streamlit run streamlit_app.py
```

---

## 🔑 Required API Keys

| Service | Get It From | Purpose |
|---------|-------------|---------|
| IBM watsonx.ai | [cloud.ibm.com](https://cloud.ibm.com) | Granite AI models |
| Speechmatics | [portal.speechmatics.com](https://portal.speechmatics.com) | Voice transcription |
| Vultr | [vultr.com](https://vultr.com) | Output file storage |

Set these in Streamlit Cloud under **Settings → Secrets** using the same key names from `.env.example`.

---

## 📁 Project Structure

```
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
```

---

## 🏆 Hackathon Details

- **Event:** IBM Bob Hackathon 2026
- **Challenge:** Build innovative applications using IBM Granite models
- **Category:** Developer Tools / AI-Assisted Development
- **Team:** TechWokx

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [IBM watsonx.ai](https://www.ibm.com/watsonx) — Granite Foundation Models
- [Streamlit](https://streamlit.io/) — Frontend framework
- [Speechmatics](https://www.speechmatics.com/) — Speech-to-text
- [Icons8](https://icons8.com/) — UI icons
