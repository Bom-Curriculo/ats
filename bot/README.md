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

Non-secret configuration lives in `config.yaml` (provider models/timeouts,
provider chain, RabbitMQ queue names, log level, AI output language). Copy
`.env.example` to `.env` for secrets only:

- `GROQ_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`
- `RABBITMQ_USER`, `RABBITMQ_PASSWORD`

A few legacy operational environment variables still override their
`config.yaml` counterpart for per-deployment flexibility: `IA_PROVIDER`,
`IA_PROVIDER_CHAIN`, `USAR_IA_PADRAO`, `RABBITMQ_HOST`, `RABBITMQ_PORT`,
`RABBITMQ_VHOST`, `LOG_LEVEL`.

## AI providers

Supported providers are Groq, Gemini, DeepSeek, OpenAI, Ollama, and Mock, all
built by `ProviderFactory` from `config.yaml`. Selection defaults to `auto`
(walks `ai.provider_chain` in order, skipping unconfigured providers).
Provider failures are sanitized before logging or returning diagnostics.

The external AI boundary receives only sanitized, compact context. Full resume
text, email addresses, phone numbers, national IDs, tokens, addresses, and sensitive
URLs must never be logged or sent to external providers.

## RabbitMQ worker

Run the worker from `bot/`:

```bash
python -m app.workers.rabbitmq_worker
```

The default queues remain stable for Laravel/front-end compatibility:

- input: `resumes_queue`
- output: `resumes_results_queue`

Clean English JSON is preferred:

```json
{
  "analysis_request_id": "uuid",
  "resume_text": "Python developer",
  "job_text": "Python role",
  "language": "en-US",
  "use_ai": false,
  "callback_queue": "resumes_results_queue"
}
```

Legacy Portuguese payload keys are accepted temporarily by the RabbitMQ parser.
File-only messages return `received_pending_extraction` until document extraction
is available.

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
