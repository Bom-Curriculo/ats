"""Dependency-injection wiring for the whole application.

Every service is registered here as a `Factory` bound to the concrete
implementation of its interface (`app/services/**/interfaces.py`).
Controllers, the RabbitMQ worker, and tests obtain their dependencies
through this container rather than importing a concrete module and
instantiating it directly — consumers depend on the interface type, and the
container decides which implementation satisfies it (dependency inversion).

Providers are `Factory` (built fresh on each resolution), not `Singleton`:
`Settings.load()` re-reads `config.yaml` and the environment on every call; a
cached `Singleton` here would freeze configuration at process startup and
ignore any later environment change (notably breaking test monkeypatching of
provider selection).
"""

from dependency_injector import containers, providers

from app.core.settings import Settings
from app.providers.factory import ProviderFactory

from app.services.privacy.sanitizer import PrivacySanitizer

from app.services.normalization.text_normalizer import TextNormalizer
from app.services.normalization.job_normalizer import JobNormalizer

from app.services.parsing.section_extractor import SectionExtractor
from app.services.parsing.resume_inventory import ResumeInventoryBuilder
from app.services.parsing.resume_entity_parser import ResumeEntityParser
from app.services.parsing.rabbitmq_payload_parser import RabbitMQPayloadParser
from app.services.parsing.readers.docx_reader import DocxDocumentReader
from app.services.parsing.readers.pdf_reader import PdfDocumentReader
from app.services.parsing.readers.reader_aggregator import DocumentReaderAggregator

from app.services.matching.technical_matching import TechnicalMatcher
from app.services.matching.technology_catalog import TechnologyCatalog
from app.services.matching.technical_equivalences import TechnicalEquivalenceResolver
from app.services.matching.requirement_groups import RequirementGroupBuilder
from app.services.matching.keyword_report import KeywordReportBuilder
from app.services.matching.evidence_selection import EvidenceSelector

from app.services.analysis.fact_bank import FactBankBuilder
from app.services.analysis.requirement_extractor import RequirementExtractor
from app.services.analysis.score_calculator import ScoreCalculator
from app.services.analysis.suggestion_engine import SuggestionEngine
from app.services.analysis.ats_analysis_service import AtsAnalysisService

from app.services.ai.ai_context import AIContextBuilder
from app.services.ai.ai_pipeline_prompts import AIPipelinePrompts
from app.services.ai.ai_orchestrator import AIPipelineOrchestrator
from app.services.ai.structured_ai_analysis import StructuredAIAnalysisValidator
from app.services.ai.ai_manager import AIManager

from app.workers.rabbitmq_worker import RabbitMQWorker


class Container(containers.DeclarativeContainer):
    settings = providers.Factory(Settings.load)

    # Providers / AI selection
    provider_factory = providers.Factory(ProviderFactory, settings=settings)

    # Privacy
    sanitizer = providers.Factory(PrivacySanitizer)

    # Normalization
    text_normalizer = providers.Factory(TextNormalizer)
    job_normalizer = providers.Factory(JobNormalizer)

    # Parsing
    section_extractor = providers.Factory(SectionExtractor)
    resume_inventory_builder = providers.Factory(ResumeInventoryBuilder)
    resume_entity_parser = providers.Factory(ResumeEntityParser)
    rabbitmq_payload_parser = providers.Factory(RabbitMQPayloadParser)
    pdf_document_reader = providers.Factory(PdfDocumentReader)
    docx_document_reader = providers.Factory(DocxDocumentReader)
    document_reader_aggregator = providers.Factory(
        DocumentReaderAggregator,
        readers=providers.List(pdf_document_reader, docx_document_reader),
    )

    # Matching
    # EvidenceSelector.select() takes its `sanitizer` at call time (not via
    # __init__): it's a single-method collaborator, so there's nothing to
    # gain from holding the dependency as instance state between calls.
    technical_matcher = providers.Factory(TechnicalMatcher)
    technology_catalog = providers.Factory(TechnologyCatalog)
    technical_equivalence_resolver = providers.Factory(TechnicalEquivalenceResolver)
    requirement_group_builder = providers.Factory(RequirementGroupBuilder)
    keyword_report_builder = providers.Factory(KeywordReportBuilder)
    evidence_selector = providers.Factory(EvidenceSelector)

    # Analysis
    fact_bank_builder = providers.Factory(FactBankBuilder)
    requirement_extractor = providers.Factory(RequirementExtractor)
    score_calculator = providers.Factory(ScoreCalculator)
    suggestion_engine = providers.Factory(SuggestionEngine)

    # AI
    # AIContextBuilder.build() and StructuredAIAnalysisValidator.run() take
    # their `sanitizer` at call time for the same reason as EvidenceSelector.
    ai_context_builder = providers.Factory(AIContextBuilder)
    ai_pipeline_prompts = providers.Factory(AIPipelinePrompts)
    ai_pipeline_orchestrator = providers.Factory(
        AIPipelineOrchestrator,
        prompts=ai_pipeline_prompts,
        context_builder=ai_context_builder,
        evidence_selector=evidence_selector,
    )
    structured_ai_analysis_validator = providers.Factory(StructuredAIAnalysisValidator)

    ats_analysis_service = providers.Factory(
        AtsAnalysisService,
        requirement_extractor=requirement_extractor,
        score_calculator=score_calculator,
        suggestion_engine=suggestion_engine,
        sanitizer=sanitizer,
        text_normalizer=text_normalizer,
        job_normalizer=job_normalizer,
        technical_equivalence_resolver=technical_equivalence_resolver,
        section_extractor=section_extractor,
        resume_inventory_builder=resume_inventory_builder,
        fact_bank_builder=fact_bank_builder,
        requirement_group_builder=requirement_group_builder,
        keyword_report_builder=keyword_report_builder,
        ai_pipeline_orchestrator=ai_pipeline_orchestrator,
        structured_ai_analysis_validator=structured_ai_analysis_validator,
    )

    ai_manager = providers.Factory(
        AIManager,
        settings=settings,
        provider_factory=provider_factory,
        sanitizer=sanitizer,
        ats_analysis_service=ats_analysis_service,
    )

    rabbitmq_worker = providers.Factory(
        RabbitMQWorker,
        settings=settings,
        ai_manager=ai_manager,
        payload_parser=rabbitmq_payload_parser,
    )
