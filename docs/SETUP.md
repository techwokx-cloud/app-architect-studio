# Setup

The project is prepared so code can be deployed first and API keys can be added later.

## Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Fill `backend/.env` with only the keys you need.

Minimum for IBM Granite:

```env
WATSONX_API_KEY=your-watsonx-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_URL=https://ca-tor.ml.cloud.ibm.com
```

## Frontend

```powershell
cd frontend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Minimum frontend `.env`:

```env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=120
```

## Smoke Test

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/status
```

The frontend should open at:

```text
http://localhost:8501
```

## Streamlit Cloud

App path:

```text
frontend/app.py
```

Secrets:

```toml
[app]
api_base_url = "https://your-backend-url"
```

## Vultr Backend

Use `backend/Dockerfile` or run `python main.py` behind Nginx. The backend listens on:

```text
0.0.0.0:8000
```
