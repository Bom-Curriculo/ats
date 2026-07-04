from abc import ABC, abstractmethod


class TextNormalizerInterface(ABC):
    """Normalize noise introduced by PDF extraction and inconsistent formatting."""

    @abstractmethod
    def normalize_resume_text(self, text: str) -> str:
        ...


class JobNormalizerInterface(ABC):
    """Structure job-post content and strip boilerplate without letting benefits affect scoring."""

    @abstractmethod
    def clean_job_text(self, text: str) -> str:
        ...

    @abstractmethod
    def normalize_job_text(self, text: str) -> dict[str, str | list[str]]:
        ...
