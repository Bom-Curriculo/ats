# ATS Resume Builder Bot

Python service for deterministic ATS analysis with optional AI enrichment.

## Architecture

- **Quart** (async, Flask-compatible API) exposes the HTTP boundary.
- **dependency-injector** wires `Settings`, `ProviderFactory`, and `AIManager`
  into the controllers and the RabbitMQ worker — nothing reaches into
  `os.environ` or imports a concrete service directly.
- **LangChain** (`langchain.chat_models.init_chat_model`) provides the actual
  transport/structured-output plumbing for every AI provider (Groq, Gemini,
  DeepSeek, OpenAI, Ollama) through one generic `LangChainProvider`, instead
  of each provider hand-rolling HTTP requests and JSON parsing.
- **`config.yaml`** holds every non-secret setting (provider models, timeouts,
  the provider fallback chain, RabbitMQ queue names, log level). Secrets
  (API keys, RabbitMQ credentials) are read only from the environment / `.env`
  — see `.env.example`.
- Every service subpackage exposes an `interfaces.py` (ABCs) that its classes
  implement; `app/core/container.py` wires concrete implementations behind
  those interfaces, so consumers depend on the interface, not the concrete
  class.
- **Document reading** (`app/services/parsing/readers/`) uses the
  adapter + aggregator pattern: `PdfDocumentReader` and `DocxDocumentReader`
  both delegate to `markitdown`, which normalizes messy PDF/DOCX extraction
  into clean text — so the adapters themselves stay a few lines each.
  `DocumentReaderAggregator` picks the adapter that supports a given
  filename's extension.

```
app/
  core/          Settings, DI container, logging setup
  models/        Pydantic request/response contracts
  controllers/   Quart blueprints (HTTP boundary only)
  services/
    privacy/       PII/secret sanitization
    normalization/  Text and job-post normalization
    parsing/        Section/entity/inventory/RabbitMQ-payload parsing, PDF/DOCX readers
    matching/       Technology catalog, technical matching, keyword/requirement grouping
    analysis/       Requirement extraction, scoring, suggestions, fact bank, the ATS facade
    ai/             AI context, provider fallback manager, structured pipeline
  providers/     LangChainProvider + mock provider + error-category mapping
  workers/       RabbitMQ worker
  main.py        Quart app factory
```

## Processing flow

1. Normalize resume and job text.
2. Remove personal data and sensitive URLs.
3. Extract resume sections and build a traceable fact bank.
4. Extract and classify job requirements.
5. Match requirements against local evidence.
6. Calculate the deterministic ATS score.
7. Optionally run the structured AI pipeline using sanitized context only.
8. Reconcile AI output against local evidence and return the final result.

Local analysis remains authoritative. AI output cannot promote unsupported claims,
turn education into professional experience, or increase evidence strength beyond
what the deterministic engine found.

The bot's own generated text (suggestions, explanations, the AI's contextual
summary) is written in Portuguese by design — end users are Brazilian job
seekers. That output language is configurable via `ai.output_language` in
`config.yaml`; only the codebase itself (identifiers, comments, architecture)
is English.

## HTTP API

Routes:

- `GET /health`
- `GET /metrics` — Prometheus metrics
- `POST /api/v1/analyze` — primary English endpoint
- `POST /api/v1/analisar` — deprecated legacy compatibility endpoint

Primary payload:

```json
{
  "resume_text": "Junior developer with a React project and FastAPI API.",
  "job_text": "Junior full-stack role requiring React, FastAPI, and SQL.",
  "language": "en-US",
  "job_level": "junior",
  "resume_sources": [],
  "use_ai": false
}
```

During the deprecation window, `AnalysisRequest` also accepts the legacy public
aliases `curriculo_texto`, `vaga_texto`, `idioma`, `nivel_vaga`, and
`fontes_curriculo`. These names must remain at the API boundary only.

Example:

```bash
curl -sS http://127.0.0.1:8000/api/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "resume_text": "Python and FastAPI project experience.",
    "job_text": "Python and FastAPI are required.",
    "language": "en-US",
    "job_level": "junior",
    "resume_sources": [],
    "use_ai": false
  }'
```

Primary response fields include `ats_score`, `matched_keywords`,
`missing_keywords`, `requirement_analysis`, `resume_inventory`, `fact_bank`,
`requirement_groups`, `evidence_source_summary`, and `sanitization_summary`.
The legacy endpoint serializes the deprecated Portuguese aliases (`pontuacao_ats`,
`palavras_chave_encontradas`, ...) for compatibility.

## Configuration

Both config files are git-ignored (so each deployment/developer can tune
them freely) and ship as `.example` templates. Before running the bot:

```bash
cp config.yaml.example config.yaml   # non-secret settings
cp .env.example .env                 # secrets
```

`config.yaml` holds every non-secret setting (provider models/timeouts,
provider chain, RabbitMQ queue names, log level, AI output language) — see
`config.yaml.example` for the full, commented structure. `.env` holds secrets
only:

- `GROQ_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`
- `RABBITMQ_USER`, `RABBITMQ_PASSWORD`

A few legacy operational environment variables still override their
`config.yaml` counterpart for per-deployment flexibility: `IA_PROVIDER`,
`IA_PROVIDER_CHAIN`, `USAR_IA_PADRAO`, `RABBITMQ_HOST`, `RABBITMQ_PORT`,
`RABBITMQ_VHOST`, `LOG_LEVEL`.

If `config.yaml` is missing entirely, `Settings.load()` falls back to empty
non-secret configuration (no provider models/timeouts) rather than failing
to start — the app will boot but every AI provider will be unconfigured, so
don't skip the copy step above.

## AI providers

Supported providers are Groq, Gemini, DeepSeek, OpenAI, Ollama, and Mock, all
built by `ProviderFactory` from `config.yaml`. Selection defaults to `auto`
(walks `ai.provider_chain` in order, skipping unconfigured providers).
Provider failures are sanitized before logging or returning diagnostics.

The external AI boundary receives only sanitized, compact context. Full resume
text, email addresses, phone numbers, national IDs, tokens, addresses, and sensitive
URLs must never be logged or sent to external providers.

## RabbitMQ worker

The worker consumes analysis requests and **publishes the full result back to
RabbitMQ as JSON** — it never returns the result over HTTP. Any service (not
just the Laravel backend) can integrate with it purely through the two
queues described below; nothing about the bot's internals needs to be known
beyond the message shapes on this page.

Run the worker from `bot/`:

```bash
uv run python -m app.workers.rabbitmq_worker
```

### Queues

Configured in `config.yaml` (`rabbitmq.*`), overridable per-deployment with
`RABBITMQ_HOST`/`RABBITMQ_PORT`/`RABBITMQ_VHOST` and the `RABBITMQ_USER` /
`RABBITMQ_PASSWORD` secrets in `.env`:

- **Input** — `resumes_queue` (durable). The worker declares it on startup.
- **Output** — `resumes_results_queue` (durable) by default, or whatever
  queue name the request message sets in `callback_queue` (declared durable
  on the fly, so any queue name a caller wants back is accepted).

Both are plain queues on the default exchange (`exchange=""`), so publishing
to them is a standard `basic_publish` with `routing_key=<queue name>`.

### Request message (what you publish to `resumes_queue`)

Content type `application/json`. English field names are preferred; the
legacy Laravel/Portuguese field names below are still accepted for backward
compatibility (only one set is required, not both):

```json
{
  "analysis_request_id": "a1b2c3d4-0000-0000-0000-000000000000",
  "resume_text": "Desenvolvedor Python com 2 anos de experiência...",
  "job_text": "Vaga para desenvolvedor backend júnior. Requisitos: Python, FastAPI, Docker, SQL.",
  "language": "pt-BR",
  "job_level": "junior",
  "use_ai": true,
  "callback_queue": "resumes_results_queue"
}
```

| Field | Legacy alias | Required | Notes |
|---|---|---|---|
| `analysis_request_id` | — | recommended | Echoed back verbatim in the response so callers can correlate requests. |
| `resume_text` | `curriculo_texto` | yes* | Plain resume text. |
| `job_text` | `vaga_texto` | yes* | Plain job post text. |
| `language` | `idioma` | no | Defaults to `pt-BR`. |
| `job_level` | `nivel_vaga` | no | e.g. `junior`, `pleno`, `senior`, `estagio`. |
| `use_ai` | `usar_ia` | no | Defaults to `ai.enabled_by_default` in `config.yaml` when omitted. |
| `callback_queue` | — | no | Overrides the default output queue for this message only. |
| `resume_cv` / `resume_cv_url`, `resume_linkedin` / `resume_linkedin_url` | — | no | File references. No extractor is wired up yet — see **Pending: file references** below. |

\* Either the plain-text fields above, or a message that only carries a file
reference (see below), must be present — an empty payload is rejected.

The worker also accepts, unchanged, the legacy serialized payload shape the
Laravel queue produces for `App\Jobs\ProcessResumesJobs`
(`{"data": {"command": "..."}}` with PHP-serialized properties) — this is
handled transparently by `app/services/parsing/rabbitmq_payload_parser.py`
and needs no special handling from a new integration; it only matters if
you're publishing from Laravel's own queue serializer.

### Response message (what the worker publishes back)

Always this envelope, JSON, `content_type: application/json`, persistent
(`delivery_mode=2`):

```json
{
  "analysis_request_id": "a1b2c3d4-0000-0000-0000-000000000000",
  "status": "completed",
  "source": "bot-python",
  "result": {
    "ats_score": 65,
    "matched_keywords": ["Python", "FastAPI", "Docker", "SQL"],
    "missing_keywords": [],
    "requirement_analysis": [
      {
        "item": "Python",
        "type": "technology",
        "category": "requirement_obrigatorio",
        "weight": 3,
        "status": "found_without_clear_context",
        "resume_evidence": "Python aparece em competências.",
        "evidence_level": "standalone_skill_evidence",
        "evidence_source": "competências",
        "guidance": "Associe a habilidade a project ou experiência real, se possível."
      }
    ],
    "suggestions": [
      "Provide clear context or project-based evidence for Python and SQL, as they are currently listed only as isolated skills."
    ],
    "ai_provider": "gemini",
    "ai_model": "gemini-3.5-flash",
    "recommended_final_score": 60,
    "final_score_explanation": "Conciliação explicável: local 45%, keywords 20% e IA 35%; confiança 95%, correções 0, etapas com fallback 0, hard filters missing_items 0.",
    "...": "the rest of the fields match the HTTP /api/v1/analyze response — see 'HTTP API' above"
  },
  "error": null
}
```

| `status` value | Meaning |
|---|---|
| `completed` | `result` contains the full analysis (same shape as the `/api/v1/analyze` HTTP response, English field names). |
| `received_pending_extraction` | The message only carried a file reference and no text; `result` is `{}`. See **Pending: file references**. |
| `failed` | An unexpected error occurred; `result` is `{}` and `error` names the exception type (never the raw message, to avoid leaking payload content into logs/queues). |

Messages that are unparsable JSON, or carry neither text nor a file
reference, are `nack`'d without requeueing and **no response is published**
— there's no `analysis_request_id` to correlate a reply to.

### Pending: file references

`resume_cv`, `resume_cv_url`, `resume_linkedin`, `resume_linkedin_url` are
accepted and recognized, but the worker does not fetch or extract them yet —
messages containing only those return `received_pending_extraction`. PDF/DOCX
*content* extraction already exists (`app/services/parsing/readers/`,
covered above), but there's no step yet that downloads a `resume_cv_url` and
feeds its bytes through that reader — send `resume_text`/`job_text` directly
until that's wired up.

### Minimal integration example (Python, any service)

```python
import json
import uuid

import pika

credentials = pika.PlainCredentials("bomcurriculo", "bomcurriculo")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="rabbitmq", port=5672, credentials=credentials)
)
channel = connection.channel()
channel.queue_declare(queue="resumes_queue", durable=True)
channel.queue_declare(queue="resumes_results_queue", durable=True)

request_id = str(uuid.uuid4())
channel.basic_publish(
    exchange="",
    routing_key="resumes_queue",
    body=json.dumps({
        "analysis_request_id": request_id,
        "resume_text": "Python and FastAPI project experience.",
        "job_text": "Python and FastAPI are required.",
        "language": "en-US",
        "use_ai": False,
        "callback_queue": "resumes_results_queue",
    }).encode("utf-8"),
    properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
)

def on_response(ch, method, _properties, body):
    payload = json.loads(body)
    if payload["analysis_request_id"] == request_id:
        print(payload["status"], payload["result"].get("ats_score"))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()

channel.basic_consume(queue="resumes_results_queue", on_message_callback=on_response)
channel.start_consuming()
```

## Main modules

| Module | Responsibility |
|---|---|
| `app/main.py` | Quart app factory, DI container wiring, blueprint registration. |
| `app/core/settings.py` | Loads `config.yaml` + secret env vars into one `Settings` object. |
| `app/core/container.py` | dependency-injector `Container`. |
| `app/controllers/analysis_controller.py` | `/api/v1/analyze` and legacy `/api/v1/analisar`. |
| `app/services/analysis/ats_analysis_service.py` | Deterministic pipeline facade and AI reconciliation. |
| `app/services/analysis/requirement_extractor.py` | Requirement extraction and resume matching. |
| `app/services/analysis/score_calculator.py` | ATS scoring and AI-score reconciliation. |
| `app/services/analysis/suggestion_engine.py` | Local suggestions, blockers, input validation. |
| `app/services/parsing/section_extractor.py` | Bilingual section extraction. |
| `app/services/parsing/resume_entity_parser.py` | Generic project and entity parsing. |
| `app/services/analysis/fact_bank.py` | Traceable evidence source of truth. |
| `app/services/matching/technical_matching.py` | Boundary-aware technical matching. |
| `app/services/matching/requirement_groups.py` | Alternative and grouped requirements. |
| `app/services/matching/evidence_selection.py` | Sanitized evidence selection. |
| `app/services/ai/ai_orchestrator.py` | Structured AI stages and fallbacks. |
| `app/services/ai/ai_manager.py` | Provider selection, fallback chain, safe failures. |
| `app/services/privacy/sanitizer.py` | Conservative PII and secret removal. |
| `app/models/` | Internal English Pydantic contracts. |
| `app/providers/langchain_provider.py` | LangChain-backed provider (all real providers). |
| `tests/` | Deterministic and mocked-provider tests. |

## Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/) via
`pyproject.toml` / `uv.lock` — there is no `requirements.txt`.

```bash
cd bot
cp config.yaml.example config.yaml   # see "Configuration" below
cp .env.example .env
uv sync              # installs runtime + dev (pytest) dependencies into .venv
uv run pytest -q tests
```

The Docker image installs the same way (`uv sync --locked --no-dev`), so a
`docker build` reproduces the exact locked dependency set.

## Validation

```bash
uv run python -m compileall -q bot/app bot/tests
uv run pytest -q bot/tests
git diff --check -- bot
```
