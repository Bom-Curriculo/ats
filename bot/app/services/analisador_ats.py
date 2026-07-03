"""Backward-compatible imports for the former Portuguese module name."""

from app.services.ats_analyzer import *  # noqa: F403
from app.services.ats_analyzer import analyze_resume as analisar_curriculo
from app.services.ats_analyzer import analyze_resume_with_ai as analisar_curriculo_com_ia
