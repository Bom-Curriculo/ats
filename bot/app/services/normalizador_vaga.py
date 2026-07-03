"""Backward-compatible imports for the former Portuguese module name."""

from app.services.job_normalizer import *  # noqa: F403
from app.services.job_normalizer import clean_job_text as limpar_texto_vaga
from app.services.job_normalizer import normalize_job_text as normalizar_texto_vaga
