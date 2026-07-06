"""Dependency-injection wiring for the whole application.

Every service is registered here as a `Factory` bound to the concrete
implementation of its interface (`app/services/**/interfaces.py`).
Controllers and the RabbitMQ worker obtain their dependencies through this
container rather than importing a concrete module and instantiating it
directly — consumers depend on the interface type, and the container decides
which implementation satisfies it (dependency inversion).

Providers are `Factory` (built fresh on each resolution), not `Singleton`:
`Settings.load()` re-reads `config.yaml` and the environment on every call; a
cached `Singleton` here would freeze configuration at process startup and
ignore any later environment change (notably breaking test monkeypatching of
provider selection).
"""

from dependency_injector import containers, providers

from app.core.settings import Settings
from app.providers.factory import ProviderFactory

from app.services.parsing.rabbitmq_payload_parser import RabbitMQPayloadParser
from app.services.parsing.readers.docx_reader import DocxDocumentReader
from app.services.parsing.readers.pdf_reader import PdfDocumentReader
from app.services.parsing.readers.reader_aggregator import DocumentReaderAggregator
from app.services.parsing.resume_content_validator import ResumeContentValidator
from app.services.parsing.resume_file_fetcher import ResumeFileFetcher

from app.services.ai.resume_analysis_manager import ResumeAnalysisManager

from app.workers.rabbitmq_worker import RabbitMQWorker


class Container(containers.DeclarativeContainer):
    settings = providers.Factory(Settings.load)

    # Providers / AI selection
    provider_factory = providers.Factory(ProviderFactory, settings=settings)

    # Parsing
    rabbitmq_payload_parser = providers.Factory(RabbitMQPayloadParser)
    pdf_document_reader = providers.Factory(PdfDocumentReader)
    docx_document_reader = providers.Factory(DocxDocumentReader)
    document_reader_aggregator = providers.Factory(
        DocumentReaderAggregator,
        readers=providers.List(pdf_document_reader, docx_document_reader),
    )
    resume_file_fetcher = providers.Factory(
        ResumeFileFetcher,
        reader_aggregator=document_reader_aggregator,
    )
    resume_content_validator = providers.Factory(ResumeContentValidator)

    # AI
    resume_analysis_manager = providers.Factory(
        ResumeAnalysisManager,
        settings=settings,
        provider_factory=provider_factory,
    )

    rabbitmq_worker = providers.Factory(
        RabbitMQWorker,
        settings=settings,
        resume_analysis_manager=resume_analysis_manager,
        payload_parser=rabbitmq_payload_parser,
        resume_file_fetcher=resume_file_fetcher,
        resume_content_validator=resume_content_validator,
    )
