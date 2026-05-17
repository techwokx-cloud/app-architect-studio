# app-architect-studio

App Architect Studio turns screenshots and business briefs into design tokens and production-ready React code.

## Structure

```text
backend/
  main.py
  watsonx_client.py
  integrations.py
  requirements.txt
  .env.example
  Dockerfile

frontend/
  app.py
  requirements.txt
  .env.example
  .streamlit/config.toml

docs/
  API_CONTRACT.md
  SETUP.md
```

## Integrations

The code is prepared for API keys to be added later:

- IBM watsonx.ai / Granite: screenshot analysis and code generation
- Speechmatics: voice transcription
- Google Gemini: optional text helper endpoint
- Vultr Object Storage: saving generated artifacts

See `docs/SETUP.md` for local run commands and `docs/API_CONTRACT.md` for frontend/backend contracts.
