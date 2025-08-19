import streamlit as st

def render_sidebar(config):
    """Render the sidebar navigation panel."""
    with st.sidebar:
        st.header("Navigation")
        
        # Model selection
        model = st.selectbox(
            "Select Model", 
            config.get_groq_model_options()
        )
        
        objective = st.selectbox(
            "I want to ", 
            config.get_usecase_options()
        )

        subject = st.selectbox(
            "Subject", 
            config.get_subject_options()
        )

        chapter = st.selectbox(
            "Select chapter", 
            config.get_chapter_options()
        )

        # Learning objective
        # objective = st.radio(
        #     "Objective",
        #     [
        #         "Revise topics",
        #         "Practice Questions",
        #         "Last minute preparation",
        #         "Trick questions"
        #     ]
        # )
        
        # File uploader for PDF
        # uploaded_file = st.file_uploader("Upload Chapter PDF", type=["pdf"])
        
        # Action button
        start_button = st.button("Start Learning", type="primary")
        
        return {
            "selected_groq_model": model,
            "objective": objective,
            "subject": subject,
            "chapter": chapter,
            # "uploaded_file": uploaded_file,
            "start_button": start_button
        }
