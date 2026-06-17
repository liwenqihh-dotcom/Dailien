# APIMart Image Generation Notes

Use these notes when maintaining `scripts/generate_article_illustrations.py`.

## Endpoints

APIMart's Gemini 3 Pro image generation flow uses:

- `POST https://api.apimart.ai/v1/images/generations`
- `GET https://api.apimart.ai/v1/tasks/{task_id}`

The generation endpoint returns a `task_id`; poll the task endpoint until the task reaches a terminal state, then download returned image URLs. APIMart documentation notes that generated image URLs are temporary, so download results to local files immediately.

## Required Request Shape

Send JSON with at least:

```json
{
  "model": "gemini-3-pro-image-preview",
  "prompt": "Chinese prompt...",
  "n": 1,
  "response_format": "url"
}
```

Use the API key via bearer auth:

```http
Authorization: Bearer ${APIMART_API_KEY}
Content-Type: application/json
```

## Operational Rules

- Do not store API keys in the skill.
- Keep `n` at `1` because the workflow needs exactly three images total.
- Submit three separate tasks so each article segment receives its own prompt and manifest entry.
- Poll with a clear timeout and preserve raw status payloads in `manifest.json` for troubleshooting.
- Save downloaded images under deterministic names: `01-opening`, `02-middle`, and `03-ending`.
