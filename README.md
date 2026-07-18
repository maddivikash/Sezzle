# Sezzle Support Agent

A deliberately small, LLM-powered support assistant for synthetic Sezzle policy and order data. It uses Gemini’s `generateContent` REST API with a strict system prompt and JSON output. No external Python packages are required.

## Live demo

An optional interactive demo is available at [sezzle-support-agent.vercel.app](https://sezzle-support-agent.vercel.app/). It uses synthetic demo accounts only; the CLI contract below remains the evaluation entry point.

## Run

Use Python 3.10+ and set your key locally (the key is neither committed nor logged). The easiest option is a local `.env` file:

```bash
cd sezzle-support-agent
cp .env.example .env
# Open .env and replace the placeholder with your new Gemini key and supported model.
python3 run_cases.py cases/golden_visible.jsonl artifacts/final_answers.jsonl
python3 evaluate_visible.py cases/golden_visible.jsonl artifacts/final_answers.jsonl
```

`.env` is in `.gitignore`; do not share it. Shell variables remain supported and override `.env` values.

### macOS certificate error

If Python reports `CERTIFICATE_VERIFY_FAILED`, run this once by double-clicking it in Finder (or execute it from Terminal), then rerun the commands above:

```bash
open '/Applications/Python 3.13/Install Certificates.command'
```

This installs Python's trusted certificate bundle. Do **not** work around the error by turning off SSL verification.

The required grader contract is `python3 run_cases.py <cases.jsonl> <answers.jsonl>`. Input records need only `id`, `question`, and `user_id`; extra visible-case labels are ignored.

## Design and safety

The agent retrieves up to three relevant local policy files, then performs a scoped mock-order lookup only for the authenticated `user_id`. It passes sanitized, owned orders—not arbitrary order IDs—to Gemini. A defensive route guardrail forces escalation for fraud, hardship, dispute filing, credit-report corrections, and specific limit/decline override requests. Gemini writes the customer-facing answer, with route/output validation after the call.

Messages that are entirely conversational filler (a bare "hi", "ok", "thanks") are answered from a small stateless map (`route: smalltalk`) without a model call, so greetings and acknowledgements get a natural reply instead of a repeated canned greeting.

## Web interface and deployment

A static chat UI (`index.html`, `styles.css`, `app.js`) talks to a Vercel serverless endpoint at `api/chat.py`, which wraps the same `SupportAgent`. `vercel.json` bundles `agent.py` and `data/**` with the function, and `.vercelignore` keeps `.env`, evaluation scripts, and artifacts out of deployments.

Deployment environment variables: `GEMINI_API_KEY` (required), `GEMINI_MODEL`, and `GEMINI_MAX_RETRY_SECONDS` (bounds the 429 backoff so a rate-limit surfaces as a clean error instead of a serverless timeout; defaults to 60 for the CLI, set low in production).

### Message rate limiting

Because the serverless function is stateless, per-visitor limits use a shared store: **Upstash Redis** (added via the Vercel Marketplace, which injects `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN`). Each request atomically increments a per-IP counter (`ratelimit:msg:<ip>`) with a rolling window; past the cap the endpoint returns `429` with `limit_reached`, and the UI shows a session-limit note and locks the composer. IP is used as the key because the demo account selector is client-chosen and not authenticated. Tunable via `RATE_LIMIT_MAX` (default `30`) and `RATE_LIMIT_WINDOW_SECONDS` (default `86400`). Enforcement **fails open**: with no store configured or on any Redis error, requests are allowed, so a storage outage never blocks support.

## Honest limitations / next steps

This is intentionally a take-home-sized retrieval system: lexical ranking may miss paraphrases, and high-risk keyword detection should become a measured classifier. I would add adversarial tests, structured telemetry, policy versioning, answer caching, retrieval-recall monitoring, and a human escalation integration. `artifacts/ITERATION.md` documents the recorded baseline and final evaluations.
