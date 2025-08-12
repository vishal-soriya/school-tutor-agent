import streamlit as st
from .header import render_header
from .sidebar import render_sidebar
from .chat import render_chat_ui
from .study_materials import render_study_materials
from .progress import render_progress_tracker
from .pdf_viewer import render_pdf_viewer
from .uiconfig import Config

class StreamlitApp():
    def __init__(self):
        self.config=Config()
        self.user_controls={}

    def load_streamlit_ui(self):
        # Set page configuration
        st.set_page_config(
            page_title="ChapterWise",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Minimal CSS to keep default Streamlit theme while ensuring dark mode
        st.markdown("""
            <style>
            /* Ensure full width and proper spacing */
            .block-container {
                padding: 1rem !important;
                max-width: 100% !important;
                width: 100% !important;
            }
            
            /* Full width content */
            .stApp {
                width: 100% !important;
                max-width: 100% !important;
            }
            
            /* Radio buttons - no background */
            .stRadio>div {
                background-color: transparent !important;
            }
            
            /* Fix for hover states */
            .stButton>button:hover, .stSelectbox>div>div:hover, .stRadio label:hover {
                box-shadow: 0 0 5px rgba(255, 255, 255, 0.3) !important;
            }
            
            /* Chat messages container with default styling */
            .stChatMessageContent {
                color: white !important;
            }
            
            /* Individual radio options */
            .stRadio label {
                transition: all 0.3s !important;
                padding: 5px !important;
                border-radius: 4px !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Render header
        render_header()
        
        # Render sidebar and get user selections
        sidebar_state = render_sidebar(self.config)
        self.user_controls.update(sidebar_state)
        print(f"Updated user controls: {self.user_controls}")

        render_chat_ui()