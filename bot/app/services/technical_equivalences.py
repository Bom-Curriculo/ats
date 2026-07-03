"""isso é usado pelo evidence gate tbm"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from app.services.text_normalizer import normalize_for_comparison


class EvidenceLevel(StrEnum):
    PRATICA_FORTE = "evidencia_pratica_forte"
    PRATICA_PARCIAL = "evidencia_pratica_parcial"
    EDUCACIONAL = "evidencia_educacional"
    SKILL_SOLTA = "evidencia_skill_solto"
    RELACIONADA = "evidencia_relacionada"
    AUSENTE = "sem_evidencia"


class JobLevel(StrEnum):
    ESTAGIO = "estagio"
    TRAINEE = "trainee"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    NAO_INFORMADO = "nao_informado"


class InferenceStrength(StrEnum):
    FORTE = "implicacao_forte"
    PROVAVEL = "relacao_provavel"
    FRACA = "relacao_fraca"


@dataclass(frozen=True)
class Inference:
    origem: str
    destino: str
    forca: InferenceStrength
    exige_contexto: tuple[str, ...] = ()


# O sentido é origem -> destino
INFERENCIAS: tuple[Inference, ...] = (
    Inference("HTML", "HTML5", InferenceStrength.FORTE),
    Inference("CSS", "CSS3", InferenceStrength.FORTE),
    Inference("TypeScript", "JavaScript", InferenceStrength.FORTE),
    Inference("Next.js", "React", InferenceStrength.FORTE),
    Inference("Nuxt", "Vue", InferenceStrength.FORTE),
    Inference("Spring Boot", "Java", InferenceStrength.FORTE),
    Inference("Spring Boot", "Spring", InferenceStrength.FORTE),
    Inference("Spring Boot", "APIs REST", InferenceStrength.PROVAVEL, ("api", "rest", "endpoint", "controller")),
    Inference("FastAPI", "Python", InferenceStrength.FORTE),
    Inference("FastAPI", "APIs REST", InferenceStrength.PROVAVEL),
    Inference("Flask", "Python", InferenceStrength.FORTE),
    Inference("Django REST Framework", "Django", InferenceStrength.FORTE),
    Inference("Django REST Framework", "APIs REST", InferenceStrength.FORTE),
    Inference("Node.js", "JavaScript", InferenceStrength.FORTE),
    Inference("Express.js", "Node.js", InferenceStrength.FORTE),
    Inference("NestJS", "Node.js", InferenceStrength.FORTE),
    Inference("NestJS", "TypeScript", InferenceStrength.FORTE),
    Inference("Laravel", "PHP", InferenceStrength.FORTE),
    Inference("Laravel", "MVC", InferenceStrength.PROVAVEL),
    Inference("Symfony", "PHP", InferenceStrength.FORTE),
    Inference("ASP.NET Core", "C#", InferenceStrength.FORTE),
    Inference("ASP.NET Core", ".NET", InferenceStrength.FORTE),
    Inference("Flutter", "Dart", InferenceStrength.FORTE),
    Inference("Docker Compose", "Docker", InferenceStrength.FORTE),
    Inference("GitHub Actions", "CI/CD", InferenceStrength.PROVAVEL),
    Inference("GitHub Actions", "Git", InferenceStrength.FRACA),
    Inference("Tailwind CSS", "CSS", InferenceStrength.FRACA),
    Inference("Bootstrap", "CSS", InferenceStrength.FRACA),
    Inference("PostgreSQL", "SQL", InferenceStrength.PROVAVEL),
    Inference("MySQL", "SQL", InferenceStrength.PROVAVEL),
    Inference("MariaDB", "SQL", InferenceStrength.PROVAVEL),
    Inference("SQLite", "SQL", InferenceStrength.PROVAVEL),
    Inference("Prisma", "SQL", InferenceStrength.FRACA),
    Inference("SQLAlchemy", "SQL", InferenceStrength.FRACA),
    Inference("Eloquent", "SQL", InferenceStrength.FRACA),
    Inference("Entity Framework", "SQL", InferenceStrength.FRACA),
    Inference("Jest", "testes automatizados", InferenceStrength.PROVAVEL),
    Inference("Vitest", "testes automatizados", InferenceStrength.PROVAVEL),
    Inference("Pytest", "testes automatizados", InferenceStrength.PROVAVEL),
    Inference("JUnit", "testes automatizados", InferenceStrength.PROVAVEL),
    Inference("PHPUnit", "testes automatizados", InferenceStrength.PROVAVEL),
    Inference("Cypress", "E2E", InferenceStrength.FORTE),
    Inference("Playwright", "E2E", InferenceStrength.FORTE),
    Inference("Selenium", "E2E", InferenceStrength.PROVAVEL),
    Inference("RAG", "LLMs", InferenceStrength.PROVAVEL),
    Inference("RAG", "Embeddings", InferenceStrength.PROVAVEL),
    Inference("RAG", "Vector DB", InferenceStrength.PROVAVEL),
    Inference("OpenAI API", "APIs de IA", InferenceStrength.FORTE),
    Inference("Gemini API", "APIs de IA", InferenceStrength.FORTE),
    Inference("Vercel", "deploy", InferenceStrength.PROVAVEL),
    Inference("Railway", "deploy", InferenceStrength.PROVAVEL),
    Inference("Render", "deploy", InferenceStrength.PROVAVEL),
    Inference("Netlify", "deploy", InferenceStrength.PROVAVEL),
    *(Inference("SQL", item, InferenceStrength.PROVAVEL) for item in ("SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE")),
    *(Inference("Git", item, InferenceStrength.PROVAVEL) for item in ("branches", "pull requests", "code review")),
    Inference("testes automatizados", "testes unitários", InferenceStrength.PROVAVEL),
    Inference("testes automatizados", "testes de integração", InferenceStrength.PROVAVEL),
)


# agrupa itens q sao subrequisitos de algo maior, pra não contar duplicado no score
GRUPOS_SUBREQUISITOS: dict[str, tuple[str, ...]] = {
    "SQL e operações básicas": ("SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE", "GROUP BY", "ORDER BY", "CRUD"),
    "Git e fluxo de colaboração": ("Git", "branches", "pull requests", "code review", "merge", "GitHub", "GitLab"),
    "Testes automatizados e tipos de teste": ("testes automatizados", "testes unitários", "testes de integração", "E2E", "Jest", "Vitest", "Pytest", "JUnit", "PHPUnit", "Cypress", "Playwright", "Selenium"),
    "APIs REST e integrações": ("APIs REST", "APIs", "consumo de APIs", "desenvolvimento de APIs", "integração de APIs", "endpoints", "webhooks"),
}


# tenta adivinhar o nível da vaga pelo texto
def detect_job_level(texto: str) -> JobLevel:
    texto = normalize_for_comparison(texto)
    padroes = (
        (JobLevel.ESTAGIO, r"\bestagi[oa]|\bintern(ship)?\b"),
        (JobLevel.TRAINEE, r"\btrainee\b"),
        (JobLevel.JUNIOR, r"\bjunior\b|\bjr\.?\b"),
        (JobLevel.SENIOR, r"\bsenior\b|\bsr\.?\b|especialista"),
        (JobLevel.PLENO, r"\bpleno\b|\bmid[- ]?level\b"),
    )
    return next((nivel for nivel, padrao in padroes if re.search(padrao, texto)), JobLevel.NAO_INFORMADO)


# peso da evidência muda conforme o nível da vaga (recomendação do gepeto))
def source_weight(nivel: JobLevel, evidencia: EvidenceLevel) -> float:
    por_nivel = {
        JobLevel.NAO_INFORMADO: {EvidenceLevel.PRATICA_FORTE: 1.0, EvidenceLevel.PRATICA_PARCIAL: .9, EvidenceLevel.EDUCACIONAL: .75, EvidenceLevel.SKILL_SOLTA: .75, EvidenceLevel.RELACIONADA: .25},
        JobLevel.ESTAGIO: {EvidenceLevel.PRATICA_FORTE: 1.0, EvidenceLevel.PRATICA_PARCIAL: .9, EvidenceLevel.EDUCACIONAL: .6, EvidenceLevel.SKILL_SOLTA: .4, EvidenceLevel.RELACIONADA: .3},
        JobLevel.TRAINEE: {EvidenceLevel.PRATICA_FORTE: 1.0, EvidenceLevel.PRATICA_PARCIAL: .85, EvidenceLevel.EDUCACIONAL: .55, EvidenceLevel.SKILL_SOLTA: .35, EvidenceLevel.RELACIONADA: .25},
        JobLevel.JUNIOR: {EvidenceLevel.PRATICA_FORTE: 1.0, EvidenceLevel.PRATICA_PARCIAL: .8, EvidenceLevel.EDUCACIONAL: .45, EvidenceLevel.SKILL_SOLTA: .3, EvidenceLevel.RELACIONADA: .25},
        JobLevel.PLENO: {EvidenceLevel.PRATICA_FORTE: 1.0, EvidenceLevel.PRATICA_PARCIAL: .55, EvidenceLevel.EDUCACIONAL: .2, EvidenceLevel.SKILL_SOLTA: .15, EvidenceLevel.RELACIONADA: .15},
        JobLevel.SENIOR: {EvidenceLevel.PRATICA_FORTE: 1.0, EvidenceLevel.PRATICA_PARCIAL: .5, EvidenceLevel.EDUCACIONAL: .15, EvidenceLevel.SKILL_SOLTA: .1, EvidenceLevel.RELACIONADA: .1},
    }
    base = por_nivel.get(nivel, por_nivel[JobLevel.NAO_INFORMADO])
    return base.get(evidencia, 0.0)


# traduz o enum interno pro status publico do schema
def public_status(evidencia: EvidenceLevel) -> str:
    return {
        EvidenceLevel.PRATICA_FORTE: "encontrado_com_evidencia",
        EvidenceLevel.PRATICA_PARCIAL: "encontrado_com_evidencia",
        EvidenceLevel.EDUCACIONAL: "encontrado_sem_contexto_claro",
        EvidenceLevel.SKILL_SOLTA: "encontrado_sem_contexto_claro",
        EvidenceLevel.RELACIONADA: "relacionado_mas_nao_explicito",
        EvidenceLevel.AUSENTE: "faltando",
    }[evidencia]


# devolve td q infere o destino e normalizando antes
def inferences_for(destino: str) -> tuple[Inference, ...]:
    alvo = normalize_for_comparison(destino)
    return tuple(i for i in INFERENCIAS if normalize_for_comparison(i.destino) == alvo)
