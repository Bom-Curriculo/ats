import re

from app.models.analysis import RequirementGroup, RequirementAnalysisItem
from app.services.matching.common_terms import GIT_TERMS, SQL_TERMS
from app.services.matching.technical_equivalences import EvidenceLevel, JobLevel, source_weight
from app.services.matching.technology_catalog import TECHNOLOGY_CATALOG
from app.services.matching.technical_matching import contains_alias
from app.services.matching.interfaces import RequirementGroupBuilderInterface
from app.services.normalization.text_normalizer import normalize_for_comparison

IA = {"LLMs", "APIs de IA", "Prompt Engineering"}


def _value(item: RequirementAnalysisItem | None, level: JobLevel) -> float:
    if not item:
        return 0
    return source_weight(level, EvidenceLevel(item.evidence_level))


def _status(value: float) -> str:
    return "atendido" if value >= .75 else ("parcialmente_atendido" if value > 0 else "nao_atendido")


def _source(items: list[RequirementAnalysisItem]) -> str | None:
    sources = list(dict.fromkeys(x.evidence_source for x in items if x.evidence_source))
    return "; ".join(sources) if sources else None


def _explicit_alternatives(job: str, available: set[str]) -> list[list[str]]:
    groups = []

    for line in job.splitlines():
        parts = re.split(r"\s+(?:ou|or)\s+", normalize_for_comparison(line))
        if len(parts) < 2:
            continue
        found_items = []

        for part in parts:
            candidates = [t.name for t in TECHNOLOGY_CATALOG if t.name in available and contains_alias(part, t.aliases, t.name)]
            if candidates:
                found_items.append(candidates[-1])

        found_items = list(dict.fromkeys(found_items))

        if len(found_items) >= 2:
            groups.append(found_items)
    return groups


class RequirementGroupBuilder(RequirementGroupBuilderInterface):
    """Group alternative/complementary requirements so they aren't scored twice."""

    def build(
        self, items: list[RequirementAnalysisItem], level_text: str, job_text: str = ""
    ) -> tuple[list[RequirementGroup], int, dict[str, int]]:
        try:
            level = JobLevel(level_text)
        except ValueError:
            level = JobLevel.NOT_PROVIDED
        alias_to_section = {x.item: x for x in items}

        groups: list[RequirementGroup] = []
        used: set[str] = set()

        def add_group(name: str, names: list[str], mode: str, group_type: str, value: float):
            existing = [alias_to_section[n] for n in names if n in alias_to_section]
            if not existing:
                return
            used.update(x.item for x in existing)
            groups.append(RequirementGroup(
                name=name, type=group_type, mode=mode,
                items=[x.item for x in existing], group_status=_status(value),
                summarized_evidence=_source(existing), score_impact=round(value * 100, 1),
                rationale=(
                    "Uma alternativa comprovada atende o grupo." if mode == "any" else
                    "Itens complementares são ponderados sem multiplicar penalidades." if mode == "weighted" else
                    "Todos os itens do grupo contribuem para o atendimento."
                ),
            ))

        for alternatives in _explicit_alternatives(job_text, set(alias_to_section)):
            # FastAPI/Flask/Django are commonly listed as "or" alternatives in job
            # posts but aren't a real explicit-choice group for scoring purposes.
            if set(alternatives) <= {"FastAPI", "Flask", "Django"}:
                continue
            alternative_type = "differential" if all(alias_to_section[x].category == "differential" for x in alternatives) else "required"
            add_group("Alternativas: " + " ou ".join(alternatives), alternatives, "any", alternative_type,
                      max(_value(alias_to_section[x], level) for x in alternatives))

        front = [x for x in ("Angular", "React") if x in alias_to_section and x not in used]
        add_group("Stack front-end", front, "any", "required",
                  max((_value(alias_to_section[x], level) for x in front), default=0))

        java = [_value(alias_to_section.get(x), level) for x in ("Java", "Spring Boot") if x in alias_to_section]
        backend_names = [x for x in ("Java", "Spring Boot", "Python", "FastAPI", "Flask") if x in alias_to_section]

        if backend_names:
            java_branch = sum(java) / len(java) if java else 0
            language = _value(alias_to_section.get("Python"), level)
            framework = max(_value(alias_to_section.get("FastAPI"), level), _value(alias_to_section.get("Flask"), level))
            python_branch = (language + framework) / 2 if language or framework else 0
            add_group("Backend Java ou Python", backend_names, "any", "required", max(java_branch, python_branch))

        sql_items = [x for x in SQL_TERMS if x in alias_to_section]
        if sql_items:
            base = _value(alias_to_section.get("SQL"), level)
            commands = [_value(alias_to_section[x], level) for x in sql_items if x != "SQL"]
            value = base * .7 + (max(commands) if commands else base) * .3
            add_group("SQL e operações CRUD", sorted(sql_items, key=lambda x: (x != "SQL", x)), "weighted", "required", value)

        devops = [x for x in ("Docker", "Kubernetes") if x in alias_to_section]
        add_group("Contêineres e orquestração", devops, "all", "required",
                  sum(_value(alias_to_section[x], level) for x in devops) / len(devops) if devops else 0)

        git = [x for x in GIT_TERMS if x in alias_to_section]
        add_group("Git e fluxo colaborativo", git, "weighted", "required",
                  sum(_value(alias_to_section[x], level) for x in git) / len(git) if git else 0)

        ia = [x for x in IA if x in alias_to_section]
        add_group("Experiência com IA", ia, "weighted", "differential",
                  sum(_value(alias_to_section[x], level) for x in ia) / len(ia) if ia else 0)

        for item in items:
            if item.item in used:
                continue
            item_type = "differential" if item.category == "differential" else ("context" if item.category == "context" else "required")
            add_group(item.item, [item.item], "all", item_type, _value(item, level))

        weights = {"required": 3.0, "desired": 2.0, "differential": 1.0, "context": .5}
        total = sum(weights.get(g.type, 1) for g in groups)
        points = sum(weights.get(g.type, 1) * g.score_impact / 100 for g in groups)
        score = round(points / total * 100) if total else 0
        return groups, score, {g.name: round(g.score_impact) for g in groups}


def build_requirement_groups(
    items: list[RequirementAnalysisItem], level_text: str, job_text: str = ""
) -> tuple[list[RequirementGroup], int, dict[str, int]]:
    return RequirementGroupBuilder().build(items, level_text, job_text)
