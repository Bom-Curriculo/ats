"""Backward-compatible imports for the former Portuguese module name."""

from app.services.text_normalizer import *  # noqa: F403
from app.services.text_normalizer import normalize_for_comparison as normalizar_para_comparacao
from app.services.text_normalizer import normalize_resume_text as normalizar_texto_curriculo
