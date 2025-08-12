"""
UI module initialization for the ChapterWise AI Tutor application.
"""

from .header import render_header
from .sidebar import render_sidebar
from .chat import render_chat_ui
from .study_materials import render_study_materials
from .progress import render_progress_tracker
from .pdf_viewer import render_pdf_viewer

__all__ = [
    "render_header",
    "render_sidebar", 
    "render_chat_ui",
    "render_study_materials",
    "render_progress_tracker",
    "render_pdf_viewer"
]
