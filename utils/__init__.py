# utils package
# Expose core functions at package level

from .ai_advice import analyze_cv
from .job_search import search_linkedin_jobs, search_bayt_jobs

__all__ = [
    "analyze_cv",
    "search_linkedin_jobs",
    "search_bayt_jobs",
]
