##até agr
análise local de currículo e vaga;
extração e classificação de requisitos;inventário técnico e Fact Bank rastreável;
keyword coverage ponderado;
grupos de requisitos e alternativas;
score semântico agrupado;
pipeline de IA em etapas;
sugestões condicionadas a evidências reais;
fallback local entre providers;
sanitização de dados pessoais;
- observabilidade segura do parser e do pipeline.


# fluxco basicamente
Currículo + Vaga
  1 Sanitização
  2 Parser de currículo
  -3Fact Bank
  4 Extração/classificação da vaga
  5 Keyword report e grupos
  6 Seleção de evidências
  7 Pipeline IA em etapas
  8 Validação anti-alucinação
  9 Score final
  10 JSON de resposta
```

## Fluxo da IA

1. `preparar_contexto_ia`: cria contexto compacto e sanitizado
2. `classificar_vaga`: identifica função, senioridade, requisitos e filtros
3. `selecionar_evidencias_relevantes`: seleciona localmente até 20 provas
4. `avaliar_requisitos_contextualmente`: avalia requisitos sem elevar a força local
5. `priorizar_lacunas`: separa lacuna real de falta de descrição
6. `gerar_sugestoes_seguras`: propõe ajustes, estudo ou projeto real
7. `consolidar_resposta_ia`: valida schema e aplica conciliação final

Parser, Fact Bank, matching, seleção de evidências, validação e score possuem implementação local.
Se uma etapa externa falhar o pipeline registra fallback e continua. Se todos os providers falharem proi algum motivo a API retornao fallback

## Segurança contra alucinação

experiência profissional possui a maior força;
freela exige sinal de entrega real;
projeto é prática de projeto, não emprego;
open source exige sinal de contribuição;
residência tecnológica é prática orientada, não emprego formal;
projeto acadêmico é prática parcial;
curso e certificação são evidências educacionais;
skill isolada não comprova prática;
evidência local prevalece sobre a IA;
tecnologia ausente gera lacuna ou sugestão de estudo/projeto.

A pós-validação remove evidência inventada, rebaixa fontes promovidas incorretamente, rejeita dados pessoais reintroduzidos e reduz o peso
da IA quando há correções

## Fact Bank

O campo `fact_bank` separa:

- `experiencias`;
- `projetos`;
- `projetos_academicos`;
- `freelas`;
- `open_source`;
- `residencias`;
- `cursos`;
- `certificacoes`;
- `skills`;
- `idiomas`;
- `conquistas`;
- `evidencias`;
- `tecnologias_por_fonte`.


Providers suportados:

- Gemini;
- Groq, DeepSeek e OpenAI por endpoint OpenAI-compatible;
- Ollama local;
- `MockProvider` para testes.

Variáveis principais de `.env.example` (rewcomendações do gepeto (gpt)):

| Variável | Uso |
|---|---|
| `IA_PROVIDER` | Provider explícito ou `auto`. |
| `IA_PROVIDER_CHAIN` | Ordem de fallback. |
| `USAR_IA_PADRAO` | Habilita IA por padrão. |
| `GEMINI_MODEL` | Modelo Gemini. |
| `GROQ_MODEL` | Modelo Groq. |
| `DEEPSEEK_MODEL` | Modelo DeepSeek. |
| `OPENAI_MODEL` | Modelo OpenAI. |
| `OLLAMA_MODEL` | Modelo Ollama. |
| `OLLAMA_BASE_URL` | Endpoint local do Ollama. |
| `IA_TASK_PROVIDER_POLICY` | Perfis lógicos por tarefa. |


pra rodar dale:

```bash
cd bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Swagger: `http://127.0.0.1:8000/docs`.

Esse é o conjunto recomendado para revisão do PR.

## Como testar o endpoint manualmente


Rotas:

- `GET /health`
- `POST /api/v1/analisar`

Exemplo sem dados pessoais:



```bash
curl -sS http://127.0.0.1:8000/api/v1/analisar \
  -H 'Content-Type: application/json' \
  -d '{
    "curriculo_texto": "Desenvolvedor júnior com projeto React e API FastAPI.",
    "vaga_texto": "Vaga júnior full stack com React, FastAPI e SQL.",
    "idioma": "pt-BR",
    "nivel_vaga": "junior",
    "usar_ia": false
  }'
```

## Worker RabbitMQ (MVP)

O consumer roda separado do FastAPI e usa `RABBITMQ_HOST`, `RABBITMQ_PORT`,
`RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_VHOST`,
`RABBITMQ_INPUT_QUEUE` (padrão `resumes_queue`) e `RABBITMQ_OUTPUT_QUEUE`
(padrão `resumes_results_queue`). A partir da pasta `bot`, execute:

```bash
python -m app.workers.rabbitmq_consumer
```

Exemplo para publicar uma entrada JSON limpa com `rabbitmqadmin`:

```bash
rabbitmqadmin publish exchange=amq.default routing_key=resumes_queue \
  payload='{"analysis_request_id":"uuid","user_id":12,"resume_cv_url":"http://backend:8000/storage/uploads/resumes/cvs/arquivo.docx","resume_linkedin_url":"http://backend:8000/storage/uploads/resumes/linkedins/arquivo.docx","vaga_texto":"descrição da vaga","callback_queue":"resumes_results_queue"}' \
  properties='{"content_type":"application/json","delivery_mode":2}'
```

URLs entre containers devem usar o nome do serviço (por exemplo,
`http://backend:8000`) ou uma URL externa; `localhost` aponta para o próprio
container do worker. Enquanto não houver extração de PDF/DOCX, mensagens que
tenham somente arquivo recebem `received_pending_extraction`.

## Campos importantes da resposta

- `pontuacao_ats`;
- `palavras_chave_encontradas`;
- `palavras_chave_faltando`;
- `analise_por_requisito`;
- `fact_bank`;
- `keyword_report`;
- `grupos_requisitos`;
- `score_por_grupo`;
- `pipeline_ia`;
- `parser_warnings`;
- `secoes_detectadas`;
- `secoes_com_baixa_confianca`;
- `fontes_evidencia_resumo`;
- `sanitizacao_resumo`;
- `score_final_recomendado`;
- `explicacao_score_final`.

## Arquivos principais (formataçãofeita pelo gepeto)

| Arquivo/pasta | Responsabilidade |
|---|---|
| `app/main.py` | Aplicação e rotas FastAPI. |
| `app/services/analisador_ats.py` | Pipeline local e conciliação final. |
| `app/services/extrator_secoes.py` | Parser bilíngue e confiança das seções. |
| `app/services/parser_entidades_curriculo.py` | Extração genérica de projetos. |
| `app/services/fact_bank.py` | Fonte de verdade e prioridade das evidências. |
| `app/services/matching_tecnico.py` | Matching técnico com limites léxicos. |
| `app/services/grupos_requisitos.py` | Alternativas e subrequisitos agrupados. |
| `app/services/selecao_evidencias.py` | Recuperação limitada e sanitizada. |
| `app/services/orquestrador_ia.py` | Etapas e fallback do pipeline. |
| `app/services/prompts_pipeline_ia.py` | Prompts pequenos com schema. |
| `app/services/gerenciador_ia.py` | Cadeia de providers e erros seguros. |
| `app/services/sanitizador_privacidade.py` | Remoção conservadora de PII e segredos. |
| `app/schemas/pipeline_ia.py` | Schemas das etapas. |
| `app/providers/base.py` | Interface comum dos providers. |
| `app/providers/gemini.py` | Adapter Gemini. |
| `app/providers/compativel_openai.py` | Adapter OpenAI-compatible. |
| `app/providers/ollama.py` | Adapter local Ollama. |
| `app/providers/mock.py` | Provider determinístico para testes. |
| `tests/` | Testes locais e providers mockados. |

## referencias

usei de base:
- [srbhr/Resume-Matcher](https://github.com/srbhr/Resume-Matcher)
- [JaimeYeung/Resume-Tailor-AI](https://github.com/JaimeYeung/Resume-Tailor-AI)
