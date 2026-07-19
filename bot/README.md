# ATS Resume Builder Bot

Python service that turns raw resume text (or a PDF/DOCX file reference),
plus optional LinkedIn/GitHub/portfolio sources, into either an ATS quality
score or a fully reconstructed, ATS-optimized resume — no job posting
involved.

## Integration guide for the PHP team (start here)

If you're wiring the Laravel backend to this bot, this section is all you
need — the rest of the file is internal implementation detail.

There are two endpoints, sharing the same request shape. Both take the base
CV as inline text or a URL the bot will download and extract itself, plus
the same optional supporting sources (LinkedIn, GitHub, portfolio, reported
skills) — see **Request** below for the full field list.

### `POST /api/v1/analyze` — just the ATS score

Judges the resume exactly as given — no rewriting.

```json
{
  "resume_text": "João Silva - Desenvolvedor Backend Júnior\nCOMPETÊNCIAS: Python, FastAPI..."
}
```

Response:

```json
{
  "score": 72,
  "suggestion": "Adicione métricas de impacto nas experiências profissionais."
}
```

### `POST /api/v1/build` — reconstruct the best possible ATS resume

Same request shape. The AI rewrites and restructures the content (stronger
wording, action verbs, better structure) — but never invents facts (a
company, date, technology, etc.) that aren't in the given sources — and
returns a new score for the resulting resume.

```json
{
  "resume_text": "João Silva - Desenvolvedor Backend Júnior\nCOMPETÊNCIAS: Python, FastAPI...",
  "resume_linkedin_url": "https://backend/storage/linkedin/joao.pdf",
  "github_url": "https://github.com/joaosilva",
  "additional_skills": [{"name": "Docker", "years": 1}]
}
```

Response:

```json
{
  "score": 92,
  "professional_summary": "Desenvolvedor backend júnior com foco em Python...",
  "header": {
    "name": "João Silva",
    "headline": "Desenvolvedor Backend Júnior",
    "email": "joao@example.com",
    "location": "São Paulo/SP",
    "contacts": "(11) 91903-0102",
    "emails": "joao@example.com",
    "links": {"GitHub": "https://github.com/joaosilva", "Portfolio": "https://joaosilva.dev"}
  },
  "experiences": [
    {"company": "Bom Currículo", "role": "Desenvolvedor Backend", "start": "2026-07-01", "end": null, "description": "...", "is_actual": true, "city": "São Paulo", "state": "SP", "country": null}
  ],
  "projects": [{"title": "...", "start": "2025-01", "end": "2025-06", "technologies": "...", "description": "...", "url": null}],
  "qualifications": [{"type": "undergraduate_degree", "institution": "...", "title": "...", "start": "2023-01-01", "end": null, "is_coursing": true}],
  "skills": [{"name": "Python", "years": null}, {"name": "Docker", "years": 1}],
  "languages": [{"level": "native", "language": "português"}],
  "others": {}
}
```

Note `projects` now carries `start`/`end` dates, same shape as `experiences`.

A `4xx`/`5xx` status with a `{"detail": "..."}` body is returned instead if
the request is invalid, the resume content is rejected, or every configured
AI provider failed — see **Errors** below for the full list.

That's the entire contract: one HTTP call in, one JSON response back.
Everything from here on is how the bot works internally.

## Architecture

- **Quart** (async, Flask-compatible API) exposes the HTTP boundary — the
  bot's only interface.
- **dependency-injector** wires `Settings`, `ProviderFactory`, and
  `ResumeAnalysisManager` into both controllers — nothing reaches into
  `os.environ` or imports a concrete service directly.
- **LangChain** (`langchain.chat_models.init_chat_model` +
  `.with_structured_output()`) provides the actual transport/structured-output
  plumbing for every AI provider (Groq, Gemini, DeepSeek, OpenAI, Ollama)
  through one generic `LangChainProvider`, instead of each provider
  hand-rolling HTTP requests and JSON parsing. There is no manual
  section/keyword parsing of the resume — the AI does the whole job.
- **`config.yaml`** holds every non-secret setting (provider models, timeouts,
  the provider fallback chain, log level). Secrets (API keys) are read only
  from the environment / `.env` — see `.env.example`.
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
  controllers/   Quart blueprints (HTTP boundary only) + shared request parsing
  services/
    parsing/       PDF/DOCX readers, resume content validation
    ai/            Score/build prompts + provider fallback manager
  providers/     LangChainProvider + mock provider + error-category mapping
  main.py        Quart app factory
```

## Processing flow

1. Get resume text: inline `resume_text`, or fetched + extracted from a
   PDF/DOCX file reference. Same for `resume_linkedin_url` if given.
2. Reject empty, too-short, or low-effort ("troll") text before it reaches the AI.
3. Send the resume text as-is to the AI (no censoring — the AI is asked to
   return the person's real name, email, and contacts as part of the result).
4. Depending on the endpoint:
   - `/api/v1/analyze`: the AI judges the resume as given — a 0-100 score
     plus one improvement suggestion. Nothing is rewritten.
   - `/api/v1/build`: the AI reconstructs the resume — header, experiences,
     projects (with start/end dates), qualifications, skills, languages —
     rewriting wording where it helps, without fabricating facts, plus a new
     0-100 score for the result.
5. Return that object over HTTP.

## HTTP API

Routes:

- `GET /health`
- `GET /metrics` — Prometheus metrics
- `POST /api/v1/analyze`
- `POST /api/v1/build`

### Request

Content type `application/json`. Same shape for both endpoints.

```json
{
  "resume_text": "Desenvolvedor Python com 2 anos de experiência...",
  "resume_cv_url": "https://backend/storage/cvs/resume.pdf",
  "resume_linkedin_url": "https://backend/storage/linkedin/export.pdf",
  "github_url": "https://github.com/joaosilva",
  "portfolio_url": "https://joaosilva.dev",
  "additional_skills": [{"name": "Docker", "years": 1}]
}
```

| Field | Required | Notes |
|---|---|---|
| `resume_text` | yes* | Plain resume text. |
| `resume_cv_url` | yes* | Absolute `http(s)` URL to a PDF/DOCX; fetched and extracted automatically. |
| `resume_linkedin_url` | no | Same as above — extracted and folded into the same prompt as supporting context. |
| `github_url` / `portfolio_url` | no | Passed to the AI as supporting context, not fetched. |
| `additional_skills` | no | Same shape as the response's `skills` (`name` + `years`). |

\* Exactly one of `resume_text` or `resume_cv_url` is required.

### Response

- `POST /api/v1/analyze` → `200` with `{"score": int, "suggestion": string}`.
- `POST /api/v1/build` → `200` with the full reconstructed-resume shape shown
  above under **Integration guide**.

### Errors

| Status | When |
|---|---|
| `422` | Request body fails validation (neither `resume_text` nor `resume_cv_url` given, unknown field, etc.), a file reference couldn't be downloaded/read, or the resume text (inline or extracted) was empty, too short, or low-effort/repetitive junk. `detail` carries the reason. |
| `503` | Every configured AI provider failed. `detail` carries a sanitized error message. |

### Resume content validation

Whatever text ends up as the resume (sent inline or extracted from a
PDF/DOCX), `ResumeContentValidator`
(`app/services/parsing/resume_content_validator.py`) rejects it before it
reaches the AI if it isn't real resume content — a scanned image with no
extractable text, a one-word placeholder, or a "troll" upload (repeated
junk/gibberish) is rejected with a `422` instead of reaching the AI:

| `detail` value | Trigger |
|---|---|
| `empty` | The text is empty or whitespace-only (e.g. a scanned-image PDF with no extractable text). |
| `too_short` | Under 100 characters or 20 words. |
| `low_content_diversity` | Long enough, but repeats the same handful of words (e.g. `"teste teste teste..."`) — real resumes repeat words too, but not to this degree. |

## Configuration

Both config files are git-ignored (so each deployment/developer can tune
them freely) and ship as `.example` templates. Before running the bot:

```bash
cp config.yaml.example config.yaml   # non-secret settings
cp .env.example .env                 # secrets
```

`config.yaml` holds every non-secret setting (provider models/timeouts,
provider chain, log level, AI output language) — see `config.yaml.example`
for the full, commented structure. `.env` holds secrets only:

- `GROQ_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`

A few legacy operational environment variables still override their
`config.yaml` counterpart for per-deployment flexibility: `IA_PROVIDER`,
`IA_PROVIDER_CHAIN`, `USAR_IA_PADRAO`, `LOG_LEVEL`.

If `config.yaml` is missing entirely, `Settings.load()` falls back to empty
non-secret configuration (no provider models/timeouts) rather than failing
to start — the app will boot but every AI provider will be unconfigured, so
don't skip the copy step above.

## AI providers

Supported providers are Groq, Gemini, DeepSeek, OpenAI, Ollama, and Mock, all
built by `ProviderFactory` from `config.yaml`. Selection defaults to `auto`
(walks `ai.provider_chain` in order, skipping unconfigured providers, trying
the next one on failure or an invalid structured response).
Provider failures are sanitized before logging or returning diagnostics.

Resume text is sent to the configured provider as-is — the bot does not
strip personal data before this call, since the AI is asked to return the
person's actual name/email/contacts as part of the structured result.

## Main modules

| Module | Responsibility |
|---|---|
| `app/main.py` | Quart app factory, DI container wiring, blueprint registration. |
| `app/core/settings.py` | Loads `config.yaml` + secret env vars into one `Settings` object. |
| `app/core/container.py` | dependency-injector `Container`. |
| `app/controllers/analysis_controller.py` | `/api/v1/analyze`. |
| `app/controllers/build_controller.py` | `/api/v1/build`. |
| `app/controllers/resume_input.py` | Request parsing/validation shared by both controllers. |
| `app/services/ai/resume_analysis_manager.py` | Provider selection, fallback chain, safe failures, for both `score_resume` and `build_resume`. |
| `app/services/ai/resume_score_prompt.py` | Builds the ATS-scoring prompt. |
| `app/services/ai/resume_builder_prompt.py` | Builds the resume-reconstruction prompt. |
| `app/services/ai/prompt_sources.py` | Shared supporting-source formatting for both prompts. |
| `app/services/parsing/resume_content_validator.py` | Rejects empty/troll resume text. |
| `app/services/parsing/resume_file_fetcher.py` | Downloads and extracts text from a file reference. |
| `app/services/parsing/readers/` | PDF/DOCX text extraction (adapter + aggregator). |
| `app/models/resume_analysis.py` | The structured request/response contracts (DTOs). |
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

### Running

```bash
uv run hypercorn app.main:app --bind 0.0.0.0:8000
```

## Validation

```bash
uv run python -m compileall -q bot/app bot/tests
uv run pytest -q bot/tests
git diff --check -- bot
```
