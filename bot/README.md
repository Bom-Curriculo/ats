# ATS Resume Builder Bot

Python service that turns raw resume text (or a PDF/DOCX file reference) into
structured resume data plus an AI-judged quality score and suggestion — no
job posting involved.

## Integration guide for the PHP team (start here)

If you're wiring the Laravel backend to this bot, this section is all you
need — the rest of the file is internal implementation detail.

**1. Publish a message to the `resumes_laravel_queue` queue** (durable,
default exchange, `content_type: application/json`). Minimal payload — just
a file reference:

```json
{
  "analysis_request_id": "a1b2c3d4-0000-0000-0000-000000000000",
  "user_id": 42,
  "resume_cv_url": "https://backend/storage/cvs/resume.pdf"
}
```

Or send the text directly instead of a file, with `resume_text` in place of
`resume_cv_url`. Both `analysis_request_id` and `user_id` are optional but
recommended — they're echoed back verbatim so you can correlate the
response and attribute it to a user. Full field reference: see **Request
message** further below.

**2. The bot consumes it**, extracts the résumé text (fetching + parsing the
PDF/DOCX if you sent a file reference), sends it to the AI, and publishes
the result back to **`resumes_output`** (durable) — or to whatever queue
name you set in `callback_queue` on the request, if you want a per-request
override.

**3. Consume from `resumes_output`.** You'll receive exactly this shape:

```json
{
  "analysis_request_id": "a1b2c3d4-0000-0000-0000-000000000000",
  "user_id": 42,
  "status": "completed",
  "source": "bot-python",
  "result": {
    "score": 92,
    "suggestion": "Adicione métricas de impacto nas experiências profissionais.",
    "header": {
      "name": "João Silva",
      "headline": "Desenvolvedor Backend Júnior",
      "email": "joao@example.com",
      "location": "São Paulo/SP",
      "contacts": "(11) 91903-0102",
      "emails": "joao@example.com",
      "links": {"Portfolio": "https://joaosilva.dev"}
    },
    "experiences": [
      {"company": "Bom Currículo", "role": "Desenvolvedor Backend", "start": "2026-07-01", "end": null, "description": "...", "is_actual": true, "city": "São Paulo", "state": "SP", "country": null}
    ],
    "projects": [{"title": "...", "date": "...", "technologies": "...", "description": "...", "url": null}],
    "qualifications": [{"type": "undergraduate_degree", "institution": "...", "title": "...", "start": "2023-01-01", "end": null, "is_coursing": true}],
    "skills": [{"name": "Python", "years": null}],
    "languages": [{"level": "native", "language": "português"}],
    "others": {}
  },
  "error": null
}
```

Check `status` first — it's not always `completed`. The other possible
values (`received_pending_extraction`, `invalid_resume_content`, `failed`)
are documented in the **Response message** section further below, along
with what `result` and `error` look like for each.

That's the entire contract: one queue in, one queue out, one JSON shape
back. Everything from here on is how the bot works internally.

## Architecture

- **Quart** (async, Flask-compatible API) exposes the HTTP boundary.
- **dependency-injector** wires `Settings`, `ProviderFactory`, and
  `ResumeAnalysisManager` into the controller and the RabbitMQ worker —
  nothing reaches into `os.environ` or imports a concrete service directly.
- **LangChain** (`langchain.chat_models.init_chat_model` +
  `.with_structured_output()`) provides the actual transport/structured-output
  plumbing for every AI provider (Groq, Gemini, DeepSeek, OpenAI, Ollama)
  through one generic `LangChainProvider`, instead of each provider
  hand-rolling HTTP requests and JSON parsing. The AI does the entire
  extraction — there is no manual section/keyword parsing of the resume.
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
    parsing/       RabbitMQ-payload parsing, PDF/DOCX readers, resume content validation
    ai/            Resume-extraction prompt + provider fallback manager
  providers/     LangChainProvider + mock provider + error-category mapping
  workers/       RabbitMQ worker
  main.py        Quart app factory
```

## Processing flow

1. Get resume text: inline `resume_text`, or fetched + extracted from a
   PDF/DOCX file reference.
2. Reject empty, too-short, or low-effort ("troll") text before it reaches the AI.
3. Send the resume text as-is to the AI (no censoring — the AI is asked to
   return the person's real name, email, and contacts as part of the result).
4. The AI returns one structured object: a 0-100 score, one improvement
   suggestion, and the resume broken down into header, experiences, projects,
   qualifications, skills, and languages.
5. Publish that object back to RabbitMQ (or return it over HTTP).

## HTTP API

Routes:

- `GET /health`
- `GET /metrics` — Prometheus metrics
- `POST /api/v1/analyze`

Request:

```json
{
  "resume_text": "João Silva - Desenvolvedor Backend Júnior\nCOMPETÊNCIAS: Python, FastAPI..."
}
```

Response: the same `result` shape documented under **Response message** below.

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
(walks `ai.provider_chain` in order, skipping unconfigured providers, trying
the next one on failure or an invalid structured response).
Provider failures are sanitized before logging or returning diagnostics.

Resume text is sent to the configured provider as-is — the bot does not
strip personal data before this call, since the AI is asked to return the
person's actual name/email/contacts as part of the structured result.

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

- **Input** — `resumes_laravel_queue` (durable). The worker declares it on startup.
- **Output** — `resumes_output` (durable) by default, or whatever
  queue name the request message sets in `callback_queue` (declared durable
  on the fly, so any queue name a caller wants back is accepted).

Both are plain queues on the default exchange (`exchange=""`), so publishing
to them is a standard `basic_publish` with `routing_key=<queue name>`.

### Request message (what you publish to `resumes_laravel_queue`)

Content type `application/json`. The legacy Portuguese field name
`curriculo_texto` is still accepted as an alias for `resume_text`.

The minimal real integration (the Laravel producer) sends only `user_id` and a
file reference:

```json
{
  "analysis_request_id": "a1b2c3d4-0000-0000-0000-000000000000",
  "user_id": 42,
  "resume_cv_url": "https://backend/storage/cvs/resume.docx",
  "callback_queue": "resumes_output"
}
```

Or with inline text:

```json
{
  "analysis_request_id": "a1b2c3d4-0000-0000-0000-000000000000",
  "user_id": 42,
  "resume_text": "Desenvolvedor Python com 2 anos de experiência...",
  "callback_queue": "resumes_output"
}
```

| Field | Legacy alias | Required | Notes |
|---|---|---|---|
| `analysis_request_id` | — | recommended | Echoed back verbatim in the response so callers can correlate requests. |
| `user_id` | — | no | Echoed back verbatim in the response so the caller knows which user the result belongs to. Never used internally beyond that — the bot has no user store. |
| `resume_text` | `curriculo_texto` | yes* | Plain resume text. |
| `callback_queue` | — | no | Overrides the default output queue for this message only. |
| `resume_cv` / `resume_cv_url`, `resume_linkedin` / `resume_linkedin_url` | — | no | File references (PDF/DOCX). Fetched and extracted automatically when the value is an absolute `http(s)` URL — see **File references** below. |

\* `resume_text`, or a message that only carries a file reference (see
below), must be present — an empty payload is rejected.

The worker also accepts, unchanged, the legacy serialized payload shape the
Laravel queue produces for `App\Jobs\ResumeProcessingPublisher`
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
  "user_id": 42,
  "status": "completed",
  "source": "bot-python",
  "result": {
    "score": 72,
    "suggestion": "Adicione métricas de impacto nas experiências profissionais.",
    "header": {
      "name": "João Silva",
      "headline": "Desenvolvedor Backend Júnior",
      "email": "joao@example.com",
      "location": "São Paulo/SP",
      "contacts": "(11) 91903-0102",
      "emails": "joao@example.com",
      "links": {"Portfolio": "https://joaosilva.dev"}
    },
    "experiences": [
      {
        "company": "Bom Currículo",
        "role": "Desenvolvedor Backend",
        "start": "2026-07-01",
        "end": null,
        "description": "Desenvolvimento do backend em Python.",
        "is_actual": true,
        "city": "São Paulo",
        "state": "SP",
        "country": null
      }
    ],
    "projects": [
      {"title": "Sistema de tarefas", "date": "2026", "technologies": "Python, Flask", "description": null, "url": null}
    ],
    "qualifications": [
      {"type": "undergraduate_degree", "institution": "Universidade Federal", "title": "Ciência da Computação", "start": "2023-01-01", "end": null, "is_coursing": true}
    ],
    "skills": [{"name": "Python", "years": null}],
    "languages": [{"level": "native", "language": "português"}],
    "others": {}
  },
  "error": null
}
```

| `status` value | Meaning |
|---|---|
| `completed` | `result` contains the full structured extraction (same shape as the `/api/v1/analyze` HTTP response). |
| `received_pending_extraction` | The message only carried a file reference and no text; `result` is `{}`. See **Pending: file references**. |
| `invalid_resume_content` | Resume text (inline or extracted from a file) was empty, too short, or low-effort/repetitive junk — `result` is `{}` and `error` is one of `empty`, `too_short`, `low_content_diversity`. See **Resume content validation**. |
| `failed` | An unexpected error occurred (including every configured AI provider failing); `result` is `{}` and `error` names the exception type (never the raw message, to avoid leaking payload content into logs/queues). |

`user_id` is echoed back for every status above (whatever the request carried,
including `null` if it was absent) so the caller can attribute the result to
the right user without the bot needing any user store of its own.

Messages that are unparsable JSON, or carry neither text nor a file
reference, are `nack`'d without requeueing and **no response is published**
— there's no `analysis_request_id` to correlate a reply to.

### File references

When no inline `resume_text`/`curriculo_texto` is present, the worker looks at
`resume_cv_url`, `resume_cv`, `resume_linkedin_url`, `resume_linkedin` (in that
order) and downloads the first one that is an absolute `http(s)` URL, then
extracts its text with the PDF/DOCX readers (`app/services/parsing/readers/`).
The extracted text is used as `resume_text` for the rest of the pipeline, same
as if it had been sent inline.

A bare storage path with no scheme (e.g. `uploads/resumes/cvs/foo.docx`, as
produced by the legacy Laravel serialized payload for `resume_cv`) has no
known host to fetch from, so it is left alone — send a full URL
(`resume_cv_url`) if you want the bot to fetch it. The same applies if the
download or extraction fails for any reason (network error, unsupported
format, oversized file): the worker falls back to `received_pending_extraction`
instead of failing the whole message.

Download limits: 15s timeout, 10 MiB max response size, `http`/`https` only.

### Resume content validation

Whatever text ends up as the resume (sent inline or extracted from a
PDF/DOCX), `ResumeContentValidator`
(`app/services/parsing/resume_content_validator.py`) rejects it before it
reaches the AI if it isn't real resume content — a scanned image with no
extractable text, a one-word placeholder, or a "troll" upload (repeated
junk/gibberish) never gets a `completed` response:

| `error` value | Trigger |
|---|---|
| `empty` | The text is empty or whitespace-only (e.g. a scanned-image PDF with no extractable text). |
| `too_short` | Under 100 characters or 20 words. |
| `low_content_diversity` | Long enough, but repeats the same handful of words (e.g. `"teste teste teste..."`) — real resumes repeat words too, but not to this degree. |

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
channel.queue_declare(queue="resumes_laravel_queue", durable=True)
channel.queue_declare(queue="resumes_output", durable=True)

request_id = str(uuid.uuid4())
channel.basic_publish(
    exchange="",
    routing_key="resumes_laravel_queue",
    body=json.dumps({
        "analysis_request_id": request_id,
        "resume_text": "Python and FastAPI project experience.",
        "callback_queue": "resumes_output",
    }).encode("utf-8"),
    properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
)

def on_response(ch, method, _properties, body):
    payload = json.loads(body)
    if payload["analysis_request_id"] == request_id:
        print(payload["status"], payload["result"].get("score"))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()

channel.basic_consume(queue="resumes_output", on_message_callback=on_response)
channel.start_consuming()
```

## Main modules

| Module | Responsibility |
|---|---|
| `app/main.py` | Quart app factory, DI container wiring, blueprint registration. |
| `app/core/settings.py` | Loads `config.yaml` + secret env vars into one `Settings` object. |
| `app/core/container.py` | dependency-injector `Container`. |
| `app/controllers/analysis_controller.py` | `/api/v1/analyze`. |
| `app/services/ai/resume_analysis_manager.py` | Provider selection, fallback chain, safe failures. |
| `app/services/ai/resume_extraction_prompt.py` | Builds the resume-extraction prompt. |
| `app/services/parsing/resume_content_validator.py` | Rejects empty/troll resume text. |
| `app/services/parsing/resume_file_fetcher.py` | Downloads and extracts text from a file reference. |
| `app/services/parsing/readers/` | PDF/DOCX text extraction (adapter + aggregator). |
| `app/services/parsing/rabbitmq_payload_parser.py` | Parses JSON or legacy serialized Laravel payloads. |
| `app/models/resume_analysis.py` | The structured result contract (DTOs). |
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
