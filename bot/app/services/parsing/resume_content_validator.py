"""Heuristic gate rejecting empty, too-short, or low-effort ("troll") resume text."""

import re

from app.services.parsing.interfaces import ResumeContentValidation, ResumeContentValidatorInterface

MIN_LENGTH_CHARS = 100
MIN_WORD_COUNT = 20
MIN_UNIQUE_WORD_RATIO = 0.3

_WORD_RE = re.compile(r"\w+", re.UNICODE)


class ResumeContentValidator(ResumeContentValidatorInterface):
    def validate(self, text: str) -> ResumeContentValidation:
        stripped = text.strip()
        if not stripped:
            return ResumeContentValidation(False, "empty")

        words = _WORD_RE.findall(stripped.lower())
        if len(stripped) < MIN_LENGTH_CHARS or len(words) < MIN_WORD_COUNT:
            return ResumeContentValidation(False, "too_short")

        # A real resume repeats plenty of words (stopwords, tech names) but still has
        # real lexical variety; a low ratio catches spam like "test test test test...".
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < MIN_UNIQUE_WORD_RATIO:
            return ResumeContentValidation(False, "low_content_diversity")

        return ResumeContentValidation(True, None)
