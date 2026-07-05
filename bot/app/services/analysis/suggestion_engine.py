import re
from difflib import SequenceMatcher

from app.models.analysis import RequirementAnalysisItem, DetailedSuggestions, ResumeEvidence
from app.services.analysis.interfaces import SuggestionEngineInterface
from app.services.matching.common_terms import BRAZILIAN_CITIES, GIT_TERMS, SQL_TERMS
from app.services.normalization.text_normalizer import normalize_for_comparison
from app.services.normalization.job_normalizer import clean_job_text

# A duplicate-input request is almost always a test/placeholder, not a real
# analysis: reject it above this normalized-length and similarity threshold.
DUPLICATE_INPUT_MIN_LENGTH = 50
DUPLICATE_INPUT_MIN_SIMILARITY = 0.92

_TERM_GROUPS = {
    "SQL": (SQL_TERMS, "SQL: consultas, JOINs, CRUD e modelagem"),
    "Git": (GIT_TERMS, "Git/versionamento: branches, pull requests e code review"),
    "Testes": (
        {"testes automatizados", "testes unitários", "testes de integração", "Jest", "Vitest", "Pytest", "JUnit", "PHPUnit", "Cypress", "Playwright"},
        "testes automatizados: unitários, integração ou e2e",
    ),
    "APIs": ({"APIs", "APIs REST", "Webhooks"}, "APIs REST e integrações: consumo, endpoints e webhooks"),
}


class SuggestionEngine(SuggestionEngineInterface):
    """Local, evidence-bound suggestions, gap prioritization, and input sanity checks."""

    def is_valid_input(self, resume: str, job: str) -> tuple[bool, list[str]]:
        resume_form, job_form = self._comparable_forms(resume, job)
        similarity = SequenceMatcher(None, resume_form, job_form).ratio() if resume_form and job_form else 0

        if resume_form == job_form or (
            min(len(resume_form), len(job_form)) > DUPLICATE_INPUT_MIN_LENGTH
            and similarity >= DUPLICATE_INPUT_MIN_SIMILARITY
        ):
            return False, [
                "Currículo e vaga são iguais ou muito parecidos; confirme os campos enviados."
            ]

        return True, []

    def _comparable_forms(self, resume: str, job: str) -> tuple[str, str]:
        return normalize_for_comparison(resume), normalize_for_comparison(clean_job_text(job))

    def detect_possible_blockers(self, resume: str, job: str) -> list[str]:
        cv, description = self._comparable_forms(resume, job)

        blockers = (
            self._incomplete_degree_blocker(cv, description),
            self._english_level_blocker(cv, description),
            self._location_mismatch_blocker(cv, description),
        )
        return [blocker for blocker in blockers if blocker]

    def _incomplete_degree_blocker(self, cv: str, description: str) -> str | None:
        if re.search(r"graduacao completa|ensino superior complete", description) and re.search(
            r"graduacao.{0,40}cursando|cursando.{0,40}graduacao", cv
        ):
            return "Vaga pede graduação completa; currículo indica graduação em andamento."
        return None

    def _english_level_blocker(self, cv: str, description: str) -> str | None:
        if re.search(r"ingles avancado|advanced english", description) and "ingles tecnico" in cv:
            return "Vaga pede inglês avançado; currículo indica inglês técnico."
        return None

    def _location_mismatch_blocker(self, cv: str, description: str) -> str | None:
        if not re.search(r"\b(hibrid[oa]|presencial)\b", description):
            return None

        job_city = next((c for c in BRAZILIAN_CITIES if normalize_for_comparison(c) in description), None)
        resume_city = next((c for c in BRAZILIAN_CITIES if normalize_for_comparison(c) in cv), None)

        if job_city and resume_city and job_city != resume_city:
            return f"Vaga é híbrida/presencial em {job_city}; currículo indica {resume_city}."
        return None

    def _group_label(self, item_name: str) -> tuple[str | None, str]:
        group = next((name for name, (members, _) in _TERM_GROUPS.items() if item_name in members), None)
        label = _TERM_GROUPS[group][1] if group else item_name
        return group, label

    def _suggestions_from_requirement_items(
        self, items: list[RequirementAnalysisItem]
    ) -> tuple[list[str], list[str], list[str]]:
        adjustments: list[str] = []
        gaps: list[str] = []
        next_steps: list[str] = []
        processed_groups: set[str] = set()

        for item in items:
            group, label = self._group_label(item.item)
            if group:
                if group in processed_groups:
                    continue
                processed_groups.add(group)

            if item.status == "found_without_clear_context":
                adjustments.append(f"Detalhe best {label}, se você já usou em projects ou experiência.")
            elif item.status == "missing":
                gaps.append(f"Se não tiver experiência com {label}, trate como lacuna técnica da vaga.")
                next_steps.append(
                    f"Considere estudar e criar um project prático com {label}, sem declarar experiência antes de utilizá-lo."
                )
            elif item.status == "related_but_not_explicit":
                adjustments.append(item.guidance)

        return adjustments, gaps, next_steps

    def _missing_skills_section_adjustment(self, evidence_items: ResumeEvidence) -> str | None:
        if evidence_items.skills_section:
            return None
        return (
            "Crie uma seção 'Competências Técnicas' claramente identificada; ela é fortemente "
            "recomendada para ATS tech, mas sua ausência não reprova automaticamente."
        )

    def _missing_experience_next_step(self, evidence_items: ResumeEvidence) -> str | None:
        if evidence_items.professional_experience:
            return None
        return (
            "Sem experiência profissional, evidencie projects pessoais ou acadêmicos, labs, "
            "freelance, residência tecnológica e courses práticos; isso não causa reprovação automática."
        )

    def _portfolio_next_step(self, job: str, items: list[RequirementAnalysisItem]) -> str | None:
        normalized_job = normalize_for_comparison(job)
        missing_items = [i.item for i in items if i.status == "missing"]
        if "portfolio" in normalized_job and "portfólio" in missing_items:
            return "Monte um portfólio com projects reais porque esta vaga o solicita."
        return None

    def generate_local_suggestions(
        self,
        items: list[RequirementAnalysisItem],
        evidence_items: ResumeEvidence,
        impeditivos: list[str],
        job: str,
    ) -> DetailedSuggestions:
        adjustments, gaps, next_steps = self._suggestions_from_requirement_items(items)
        attention = list(impeditivos)

        skills_section_adjustment = self._missing_skills_section_adjustment(evidence_items)
        if skills_section_adjustment:
            adjustments.insert(0, skills_section_adjustment)

        experience_next_step = self._missing_experience_next_step(evidence_items)
        if experience_next_step:
            next_steps.append(experience_next_step)

        portfolio_next_step = self._portfolio_next_step(job, items)
        if portfolio_next_step:
            next_steps.append(portfolio_next_step)

        adjustments = list(dict.fromkeys(adjustments))
        gaps = list(dict.fromkeys(gaps))
        next_steps = list(dict.fromkeys(next_steps))
        honesty_alerts = ["Não inclua tecnologias, práticas ou resultados que você não possa comprovar."]
        return DetailedSuggestions(
            recommended_adjustments=adjustments,
            technical_gaps=gaps,
            attention_points=attention,
            next_steps=next_steps,
            resume_adjustments=adjustments,
            real_gaps=gaps,
            study_next_steps=next_steps,
            anti_fabrication_alerts=honesty_alerts,
        )


def detect_possible_blockers(resume: str, job: str) -> list[str]:
    return SuggestionEngine().detect_possible_blockers(resume, job)


def generate_local_suggestions(
    items: list[RequirementAnalysisItem],
    evidence_items: ResumeEvidence,
    impeditivos: list[str],
    job: str,
) -> DetailedSuggestions:
    return SuggestionEngine().generate_local_suggestions(items, evidence_items, impeditivos, job)
