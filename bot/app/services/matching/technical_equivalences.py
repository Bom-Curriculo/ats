"""Technical equivalences shared with the evidence gate."""

from __future__ import annotations

import re

from app.services.matching.interfaces import (
    EvidenceLevel,
    Inference,
    InferenceStrength,
    JobLevel,
    TechnicalEquivalenceResolverInterface,
)
from app.services.normalization.text_normalizer import normalize_for_comparison

INFERENCES: tuple[Inference, ...] = (
    Inference("HTML", "HTML5", InferenceStrength.STRONG),
    Inference("CSS", "CSS3", InferenceStrength.STRONG),
    Inference("TypeScript", "JavaScript", InferenceStrength.STRONG),
    Inference("Next.js", "React", InferenceStrength.STRONG),
    Inference("Nuxt", "Vue", InferenceStrength.STRONG),
    Inference("Spring Boot", "Java", InferenceStrength.STRONG),
    Inference("Spring Boot", "Spring", InferenceStrength.STRONG),
    Inference("Spring Boot", "APIs REST", InferenceStrength.LIKELY, ("api", "rest", "endpoint", "controller")),
    Inference("FastAPI", "Python", InferenceStrength.STRONG),
    Inference("FastAPI", "APIs REST", InferenceStrength.LIKELY),
    Inference("Flask", "Python", InferenceStrength.STRONG),
    Inference("Django REST Framework", "Django", InferenceStrength.STRONG),
    Inference("Django REST Framework", "APIs REST", InferenceStrength.STRONG),
    Inference("Node.js", "JavaScript", InferenceStrength.STRONG),
    Inference("Express.js", "Node.js", InferenceStrength.STRONG),
    Inference("NestJS", "Node.js", InferenceStrength.STRONG),
    Inference("NestJS", "TypeScript", InferenceStrength.STRONG),
    Inference("Laravel", "PHP", InferenceStrength.STRONG),
    Inference("Laravel", "MVC", InferenceStrength.LIKELY),
    Inference("Symfony", "PHP", InferenceStrength.STRONG),
    Inference("ASP.NET Core", "C#", InferenceStrength.STRONG),
    Inference("ASP.NET Core", ".NET", InferenceStrength.STRONG),
    Inference("Flutter", "Dart", InferenceStrength.STRONG),
    Inference("Docker Compose", "Docker", InferenceStrength.STRONG),
    Inference("GitHub Actions", "CI/CD", InferenceStrength.LIKELY),
    Inference("GitHub Actions", "Git", InferenceStrength.WEAK),
    Inference("Tailwind CSS", "CSS", InferenceStrength.WEAK),
    Inference("Bootstrap", "CSS", InferenceStrength.WEAK),
    Inference("PostgreSQL", "SQL", InferenceStrength.LIKELY),
    Inference("MySQL", "SQL", InferenceStrength.LIKELY),
    Inference("MariaDB", "SQL", InferenceStrength.LIKELY),
    Inference("SQLite", "SQL", InferenceStrength.LIKELY),
    Inference("Prisma", "SQL", InferenceStrength.WEAK),
    Inference("SQLAlchemy", "SQL", InferenceStrength.WEAK),
    Inference("Eloquent", "SQL", InferenceStrength.WEAK),
    Inference("Entity Framework", "SQL", InferenceStrength.WEAK),
    Inference("Jest", "testes automatizados", InferenceStrength.LIKELY),
    Inference("Vitest", "testes automatizados", InferenceStrength.LIKELY),
    Inference("Pytest", "testes automatizados", InferenceStrength.LIKELY),
    Inference("JUnit", "testes automatizados", InferenceStrength.LIKELY),
    Inference("PHPUnit", "testes automatizados", InferenceStrength.LIKELY),
    Inference("Cypress", "E2E", InferenceStrength.STRONG),
    Inference("Playwright", "E2E", InferenceStrength.STRONG),
    Inference("Selenium", "E2E", InferenceStrength.LIKELY),
    Inference("RAG", "LLMs", InferenceStrength.LIKELY),
    Inference("RAG", "Embeddings", InferenceStrength.LIKELY),
    Inference("RAG", "Vector DB", InferenceStrength.LIKELY),
    Inference("OpenAI API", "APIs de IA", InferenceStrength.STRONG),
    Inference("Gemini API", "APIs de IA", InferenceStrength.STRONG),
    Inference("Vercel", "deploy", InferenceStrength.LIKELY),
    Inference("Railway", "deploy", InferenceStrength.LIKELY),
    Inference("Render", "deploy", InferenceStrength.LIKELY),
    Inference("Netlify", "deploy", InferenceStrength.LIKELY),
    *(Inference("SQL", item, InferenceStrength.LIKELY) for item in ("SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE")),
    *(Inference("Git", item, InferenceStrength.LIKELY) for item in ("branches", "pull requests", "code review")),
    Inference("testes automatizados", "testes unitários", InferenceStrength.LIKELY),
    Inference("testes automatizados", "testes de integração", InferenceStrength.LIKELY),
)


# Group subrequirements to avoid counting the same requirement twice.
SUBREQUIREMENT_GROUPS: dict[str, tuple[str, ...]] = {
    "SQL e operações básicas": ("SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE", "GROUP BY", "ORDER BY", "CRUD"),
    "Git e fluxo de colaboração": ("Git", "branches", "pull requests", "code review", "merge", "GitHub", "GitLab"),
    "Testes automatizados e tipos de teste": ("testes automatizados", "testes unitários", "testes de integração", "E2E", "Jest", "Vitest", "Pytest", "JUnit", "PHPUnit", "Cypress", "Playwright", "Selenium"),
    "APIs REST e integrações": ("APIs REST", "APIs", "consumo de APIs", "desenvolvimento de APIs", "integração de APIs", "endpoints", "webhooks"),
}


class TechnicalEquivalenceResolver(TechnicalEquivalenceResolverInterface):
    """Job-level detection, evidence weighting, and technology-inference lookups."""

    def detect_job_level(self, text: str) -> JobLevel:
        text = normalize_for_comparison(text)
        patterns = (
            (JobLevel.INTERNSHIP, r"\bestagi[oa]|\bintern(ship)?\b"),
            (JobLevel.TRAINEE, r"\btrainee\b"),
            (JobLevel.JUNIOR, r"\bjunior\b|\bjr\.?\b"),
            (JobLevel.SENIOR, r"\bsenior\b|\bsr\.?\b|especialista"),
            (JobLevel.MID_LEVEL, r"\bpleno\b|\bmid[- ]?level\b"),
        )
        return next((level for level, pattern in patterns if re.search(pattern, text)), JobLevel.NOT_PROVIDED)

    def source_weight(self, level: JobLevel, evidence: EvidenceLevel) -> float:
        """Evidence weight changes according to the job level."""
        by_level = {
            JobLevel.NOT_PROVIDED: {EvidenceLevel.STRONG_PRACTICAL: 1.0, EvidenceLevel.PARTIAL_PRACTICAL: .9, EvidenceLevel.EDUCATIONAL: .75, EvidenceLevel.STANDALONE_SKILL: .75, EvidenceLevel.RELATED: .25},
            JobLevel.INTERNSHIP: {EvidenceLevel.STRONG_PRACTICAL: 1.0, EvidenceLevel.PARTIAL_PRACTICAL: .9, EvidenceLevel.EDUCATIONAL: .6, EvidenceLevel.STANDALONE_SKILL: .4, EvidenceLevel.RELATED: .3},
            JobLevel.TRAINEE: {EvidenceLevel.STRONG_PRACTICAL: 1.0, EvidenceLevel.PARTIAL_PRACTICAL: .85, EvidenceLevel.EDUCATIONAL: .55, EvidenceLevel.STANDALONE_SKILL: .35, EvidenceLevel.RELATED: .25},
            JobLevel.JUNIOR: {EvidenceLevel.STRONG_PRACTICAL: 1.0, EvidenceLevel.PARTIAL_PRACTICAL: .8, EvidenceLevel.EDUCATIONAL: .45, EvidenceLevel.STANDALONE_SKILL: .3, EvidenceLevel.RELATED: .25},
            JobLevel.MID_LEVEL: {EvidenceLevel.STRONG_PRACTICAL: 1.0, EvidenceLevel.PARTIAL_PRACTICAL: .55, EvidenceLevel.EDUCATIONAL: .2, EvidenceLevel.STANDALONE_SKILL: .15, EvidenceLevel.RELATED: .15},
            JobLevel.SENIOR: {EvidenceLevel.STRONG_PRACTICAL: 1.0, EvidenceLevel.PARTIAL_PRACTICAL: .5, EvidenceLevel.EDUCATIONAL: .15, EvidenceLevel.STANDALONE_SKILL: .1, EvidenceLevel.RELATED: .1},
        }
        base = by_level.get(level, by_level[JobLevel.NOT_PROVIDED])
        return base.get(evidence, 0.0)

    def public_status(self, evidence: EvidenceLevel) -> str:
        return {
            EvidenceLevel.STRONG_PRACTICAL: "found_with_evidence",
            EvidenceLevel.PARTIAL_PRACTICAL: "found_with_evidence",
            EvidenceLevel.EDUCATIONAL: "found_without_clear_context",
            EvidenceLevel.STANDALONE_SKILL: "found_without_clear_context",
            EvidenceLevel.RELATED: "related_but_not_explicit",
            EvidenceLevel.ABSENT: "missing",
        }[evidence]

    def inferences_for(self, target: str) -> tuple[Inference, ...]:
        """Return normalized sources that imply the target."""
        target = normalize_for_comparison(target)
        return tuple(i for i in INFERENCES if normalize_for_comparison(i.target) == target)


_resolver = TechnicalEquivalenceResolver()


def detect_job_level(text: str) -> JobLevel:
    return _resolver.detect_job_level(text)


def source_weight(level: JobLevel, evidence: EvidenceLevel) -> float:
    return _resolver.source_weight(level, evidence)


def public_status(evidence: EvidenceLevel) -> str:
    return _resolver.public_status(evidence)


def inferences_for(target: str) -> tuple[Inference, ...]:
    return _resolver.inferences_for(target)
