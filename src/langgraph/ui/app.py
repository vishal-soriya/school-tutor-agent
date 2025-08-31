import streamlit as st
from .header import render_header
from .sidebar import render_sidebar
from .chat import render_chat_ui
from .study_materials import render_study_materials
from .progress import render_progress_tracker
from .pdf_viewer import render_pdf_viewer
from .pdf_upload import render_pdf_upload_ui
from .uiconfig import Config

class StreamlitApp():
    def __init__(self):
        self.config=Config()
        self.user_controls={}

    def load_streamlit_ui(self):
        # Page configuration and CSS are now handled in main.py
        
        # Render header
        render_header()
        
        # Render sidebar and get user selections
        sidebar_state = render_sidebar(self.config)
        self.user_controls.update(sidebar_state)
        print(f"Updated user controls: {self.user_controls}")

        # Show the selected page
        selected_page = sidebar_state.get("selected_page", "Chat")
        
        if selected_page == "Chat":
            # No need to render chat here as it's done in main.py
            pass
        elif selected_page == "Study Materials":
            render_pdf_upload_ui()

        return self.user_controls