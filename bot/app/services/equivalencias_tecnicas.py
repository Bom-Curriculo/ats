"""isso é usado pelo evidence gate tbm"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from app.services.normalizador_texto import normalizar_para_comparacao


class NivelEvidencia(StrEnum):
    PRATICA_FORTE = "evidencia_pratica_forte"
    PRATICA_PARCIAL = "evidencia_pratica_parcial"
    EDUCACIONAL = "evidencia_educacional"
    SKILL_SOLTA = "evidencia_skill_solto"
    RELACIONADA = "evidencia_relacionada"
    AUSENTE = "sem_evidencia"


class NivelVaga(StrEnum):
    ESTAGIO = "estagio"
    TRAINEE = "trainee"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    NAO_INFORMADO = "nao_informado"


class ForcaInferencia(StrEnum):
    FORTE = "implicacao_forte"
    PROVAVEL = "relacao_provavel"
    FRACA = "relacao_fraca"


@dataclass(frozen=True)
class Inferencia:
    origem: str
    destino: str
    forca: ForcaInferencia
    exige_contexto: tuple[str, ...] = ()


# O sentido é origem -> destino
INFERENCIAS: tuple[Inferencia, ...] = (
    Inferencia("HTML", "HTML5", ForcaInferencia.FORTE),
    Inferencia("CSS", "CSS3", ForcaInferencia.FORTE),
    Inferencia("TypeScript", "JavaScript", ForcaInferencia.FORTE),
    Inferencia("Next.js", "React", ForcaInferencia.FORTE),
    Inferencia("Nuxt", "Vue", ForcaInferencia.FORTE),
    Inferencia("Spring Boot", "Java", ForcaInferencia.FORTE),
    Inferencia("Spring Boot", "Spring", ForcaInferencia.FORTE),
    Inferencia("Spring Boot", "APIs REST", ForcaInferencia.PROVAVEL, ("api", "rest", "endpoint", "controller")),
    Inferencia("FastAPI", "Python", ForcaInferencia.FORTE),
    Inferencia("FastAPI", "APIs REST", ForcaInferencia.PROVAVEL),
    Inferencia("Flask", "Python", ForcaInferencia.FORTE),
    Inferencia("Django REST Framework", "Django", ForcaInferencia.FORTE),
    Inferencia("Django REST Framework", "APIs REST", ForcaInferencia.FORTE),
    Inferencia("Node.js", "JavaScript", ForcaInferencia.FORTE),
    Inferencia("Express.js", "Node.js", ForcaInferencia.FORTE),
    Inferencia("NestJS", "Node.js", ForcaInferencia.FORTE),
    Inferencia("NestJS", "TypeScript", ForcaInferencia.FORTE),
    Inferencia("Laravel", "PHP", ForcaInferencia.FORTE),
    Inferencia("Laravel", "MVC", ForcaInferencia.PROVAVEL),
    Inferencia("Symfony", "PHP", ForcaInferencia.FORTE),
    Inferencia("ASP.NET Core", "C#", ForcaInferencia.FORTE),
    Inferencia("ASP.NET Core", ".NET", ForcaInferencia.FORTE),
    Inferencia("Flutter", "Dart", ForcaInferencia.FORTE),
    Inferencia("Docker Compose", "Docker", ForcaInferencia.FORTE),
    Inferencia("GitHub Actions", "CI/CD", ForcaInferencia.PROVAVEL),
    Inferencia("GitHub Actions", "Git", ForcaInferencia.FRACA),
    Inferencia("Tailwind CSS", "CSS", ForcaInferencia.FRACA),
    Inferencia("Bootstrap", "CSS", ForcaInferencia.FRACA),
    Inferencia("PostgreSQL", "SQL", ForcaInferencia.PROVAVEL),
    Inferencia("MySQL", "SQL", ForcaInferencia.PROVAVEL),
    Inferencia("MariaDB", "SQL", ForcaInferencia.PROVAVEL),
    Inferencia("SQLite", "SQL", ForcaInferencia.PROVAVEL),
    Inferencia("Prisma", "SQL", ForcaInferencia.FRACA),
    Inferencia("SQLAlchemy", "SQL", ForcaInferencia.FRACA),
    Inferencia("Eloquent", "SQL", ForcaInferencia.FRACA),
    Inferencia("Entity Framework", "SQL", ForcaInferencia.FRACA),
    Inferencia("Jest", "testes automatizados", ForcaInferencia.PROVAVEL),
    Inferencia("Vitest", "testes automatizados", ForcaInferencia.PROVAVEL),
    Inferencia("Pytest", "testes automatizados", ForcaInferencia.PROVAVEL),
    Inferencia("JUnit", "testes automatizados", ForcaInferencia.PROVAVEL),
    Inferencia("PHPUnit", "testes automatizados", ForcaInferencia.PROVAVEL),
    Inferencia("Cypress", "E2E", ForcaInferencia.FORTE),
    Inferencia("Playwright", "E2E", ForcaInferencia.FORTE),
    Inferencia("Selenium", "E2E", ForcaInferencia.PROVAVEL),
    Inferencia("RAG", "LLMs", ForcaInferencia.PROVAVEL),
    Inferencia("RAG", "Embeddings", ForcaInferencia.PROVAVEL),
    Inferencia("RAG", "Vector DB", ForcaInferencia.PROVAVEL),
    Inferencia("OpenAI API", "APIs de IA", ForcaInferencia.FORTE),
    Inferencia("Gemini API", "APIs de IA", ForcaInferencia.FORTE),
    Inferencia("Vercel", "deploy", ForcaInferencia.PROVAVEL),
    Inferencia("Railway", "deploy", ForcaInferencia.PROVAVEL),
    Inferencia("Render", "deploy", ForcaInferencia.PROVAVEL),
    Inferencia("Netlify", "deploy", ForcaInferencia.PROVAVEL),
    *(Inferencia("SQL", item, ForcaInferencia.PROVAVEL) for item in ("SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE")),
    *(Inferencia("Git", item, ForcaInferencia.PROVAVEL) for item in ("branches", "pull requests", "code review")),
    Inferencia("testes automatizados", "testes unitários", ForcaInferencia.PROVAVEL),
    Inferencia("testes automatizados", "testes de integração", ForcaInferencia.PROVAVEL),
)


# agrupa itens q sao subrequisitos de algo maior, pra não contar duplicado no score
GRUPOS_SUBREQUISITOS: dict[str, tuple[str, ...]] = {
    "SQL e operações básicas": ("SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE", "GROUP BY", "ORDER BY", "CRUD"),
    "Git e fluxo de colaboração": ("Git", "branches", "pull requests", "code review", "merge", "GitHub", "GitLab"),
    "Testes automatizados e tipos de teste": ("testes automatizados", "testes unitários", "testes de integração", "E2E", "Jest", "Vitest", "Pytest", "JUnit", "PHPUnit", "Cypress", "Playwright", "Selenium"),
    "APIs REST e integrações": ("APIs REST", "APIs", "consumo de APIs", "desenvolvimento de APIs", "integração de APIs", "endpoints", "webhooks"),
}


# tenta adivinhar o nível da vaga pelo texto
def detectar_nivel_vaga(texto: str) -> NivelVaga:
    texto = normalizar_para_comparacao(texto)
    padroes = (
        (NivelVaga.ESTAGIO, r"\bestagi[oa]|\bintern(ship)?\b"),
        (NivelVaga.TRAINEE, r"\btrainee\b"),
        (NivelVaga.JUNIOR, r"\bjunior\b|\bjr\.?\b"),
        (NivelVaga.SENIOR, r"\bsenior\b|\bsr\.?\b|especialista"),
        (NivelVaga.PLENO, r"\bpleno\b|\bmid[- ]?level\b"),
    )
    return next((nivel for nivel, padrao in padroes if re.search(padrao, texto)), NivelVaga.NAO_INFORMADO)


# peso da evidência muda conforme o nível da vaga (recomendação do gepeto))
def peso_fonte(nivel: NivelVaga, evidencia: NivelEvidencia) -> float:
    por_nivel = {
        NivelVaga.NAO_INFORMADO: {NivelEvidencia.PRATICA_FORTE: 1.0, NivelEvidencia.PRATICA_PARCIAL: .9, NivelEvidencia.EDUCACIONAL: .75, NivelEvidencia.SKILL_SOLTA: .75, NivelEvidencia.RELACIONADA: .25},
        NivelVaga.ESTAGIO: {NivelEvidencia.PRATICA_FORTE: 1.0, NivelEvidencia.PRATICA_PARCIAL: .9, NivelEvidencia.EDUCACIONAL: .6, NivelEvidencia.SKILL_SOLTA: .4, NivelEvidencia.RELACIONADA: .3},
        NivelVaga.TRAINEE: {NivelEvidencia.PRATICA_FORTE: 1.0, NivelEvidencia.PRATICA_PARCIAL: .85, NivelEvidencia.EDUCACIONAL: .55, NivelEvidencia.SKILL_SOLTA: .35, NivelEvidencia.RELACIONADA: .25},
        NivelVaga.JUNIOR: {NivelEvidencia.PRATICA_FORTE: 1.0, NivelEvidencia.PRATICA_PARCIAL: .8, NivelEvidencia.EDUCACIONAL: .45, NivelEvidencia.SKILL_SOLTA: .3, NivelEvidencia.RELACIONADA: .25},
        NivelVaga.PLENO: {NivelEvidencia.PRATICA_FORTE: 1.0, NivelEvidencia.PRATICA_PARCIAL: .55, NivelEvidencia.EDUCACIONAL: .2, NivelEvidencia.SKILL_SOLTA: .15, NivelEvidencia.RELACIONADA: .15},
        NivelVaga.SENIOR: {NivelEvidencia.PRATICA_FORTE: 1.0, NivelEvidencia.PRATICA_PARCIAL: .5, NivelEvidencia.EDUCACIONAL: .15, NivelEvidencia.SKILL_SOLTA: .1, NivelEvidencia.RELACIONADA: .1},
    }
    base = por_nivel.get(nivel, por_nivel[NivelVaga.NAO_INFORMADO])
    return base.get(evidencia, 0.0)


# traduz o enum interno pro status publico do schema
def status_publico(evidencia: NivelEvidencia) -> str:
    return {
        NivelEvidencia.PRATICA_FORTE: "encontrado_com_evidencia",
        NivelEvidencia.PRATICA_PARCIAL: "encontrado_com_evidencia",
        NivelEvidencia.EDUCACIONAL: "encontrado_sem_contexto_claro",
        NivelEvidencia.SKILL_SOLTA: "encontrado_sem_contexto_claro",
        NivelEvidencia.RELACIONADA: "relacionado_mas_nao_explicito",
        NivelEvidencia.AUSENTE: "faltando",
    }[evidencia]


# devolve td q infere o destino e normalizando antes
def inferencias_para(destino: str) -> tuple[Inferencia, ...]:
    alvo = normalizar_para_comparacao(destino)
    return tuple(i for i in INFERENCIAS if normalizar_para_comparacao(i.destino) == alvo)
