# ATS Resume Builder Bot

Python service for deterministic ATS analysis with optional AI enrichment.

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

## HTTP API

Routes:

- `GET /health`
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
The legacy endpoint may serialize deprecated Portuguese aliases for compatibility.

## AI providers

Supported providers are Groq, Gemini, DeepSeek, OpenAI, Ollama, and Mock. Configure
selection through `IA_PROVIDER`; automatic fallback order is configured with
`IA_PROVIDER_CHAIN`. Provider failures are sanitized before logging or returning
diagnostics.

The external AI boundary receives only sanitized, compact context. Full resume
text, email addresses, phone numbers, CPF values, tokens, addresses, and sensitive
URLs must never be logged or sent to external providers.

## RabbitMQ worker

Run the worker from `bot/`:

```bash
python -m app.workers.rabbitmq_consumer
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
| `app/main.py` | FastAPI application and HTTP compatibility boundary. |
| `app/services/ats_analyzer.py` | Deterministic pipeline and final reconciliation. |
| `app/services/section_extractor.py` | Bilingual section extraction. |
| `app/services/resume_entity_parser.py` | Generic project and entity parsing. |
| `app/services/fact_bank.py` | Traceable evidence source of truth. |
| `app/services/technical_matching.py` | Boundary-aware technical matching. |
| `app/services/requirement_groups.py` | Alternative and grouped requirements. |
| `app/services/evidence_selection.py` | Sanitized evidence selection. |
| `app/services/ai_orchestrator.py` | Structured AI stages and fallbacks. |
| `app/services/ai_pipeline_prompts.py` | Compact structured prompts. |
| `app/services/ai_manager.py` | Provider selection and safe failures. |
| `app/services/privacy_sanitizer.py` | Conservative PII and secret removal. |
| `app/schemas/` | Internal English Pydantic contracts. |
| `app/providers/` | Provider adapters. |
| `tests/` | Deterministic and mocked-provider tests. |

## Validation

```bash
python -m compileall -q bot/app bot/tests
python -m pytest -q bot/tests
git diff --check -- bot
```
