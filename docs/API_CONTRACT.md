# App Architect Studio API Contract

Base URL:

```text
http://localhost:8000
```

## Status

### `GET /health`

Returns backend health and integration configuration flags.

### `GET /api/status`

Returns integration status and active model IDs.

## Vision

### `POST /api/vision`

Request:

```json
{
  "image": "base64-image-or-data-url"
}
```

Response:

```json
{
  "tokens": {
    "colors": [],
    "fonts": [],
    "spacing": [],
    "components": []
  },
  "styleLock": {
    "locked": true,
    "tokens": {},
    "constraints": [],
    "generatedAt": "ISO timestamp"
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0
  }
}
```

Requires:

```text
WATSONX_API_KEY
WATSONX_PROJECT_ID
WATSONX_URL
WATSONX_VISION_MODEL
```

If `ibm/granite-vision-3-2-2b` is not available in your watsonx region, use a
supported vision model such as:

```text
WATSONX_VISION_MODEL=meta-llama/llama-3-2-11b-vision-instruct
```

## Code Generation

### `POST /api/generate`

Request:

```json
{
  "tokens": {},
  "componentNames": ["Button"],
  "language": "en",
  "styleLock": {}
}
```

Response:

```json
{
  "code": "string",
  "language": "en",
  "tokens": {}
}
```

Requires watsonx variables. If the default text model is not available in your
region, override it:

```text
WATSONX_TEXT_MODEL=meta-llama/llama-3-3-70b-instruct
```

## Voice

### `POST /api/voice`

Request:

```json
{
  "audioBase64": "base64-audio",
  "language": "en",
  "format": "wav"
}
```

Response:

```json
{
  "success": true,
  "job_id": "speechmatics-job-id",
  "transcript": "text"
}
```

Requires:

```text
SPEECHMATICS_API_KEY
```

## Google Helper

### `POST /api/google/generate`

Request:

```json
{
  "prompt": "string",
  "model": "gemini-1.5-flash"
}
```

Requires:

```text
GOOGLE_API_KEY
GOOGLE_MODEL
```

## Cloudflare R2

### `POST /api/storage/save`

Request:

```json
{
  "key": "components.tsx",
  "content": "file contents",
  "contentType": "text/plain"
}
```

Requires:

```text
CLOUDFLARE_R2_ENDPOINT
CLOUDFLARE_R2_REGION
CLOUDFLARE_R2_ACCESS_KEY_ID
CLOUDFLARE_R2_SECRET_ACCESS_KEY
CLOUDFLARE_R2_BUCKET
```
