"""Backward-compatible imports for the former Portuguese module name."""

from app.schemas.analysis import *  # noqa: F403
from app.schemas.analysis import AnalysisRequest as SolicitacaoAnalise
from app.schemas.analysis import AnalysisResult as ResultadoAnalise
from app.schemas.analysis import ResumeSource as FonteCurriculo
