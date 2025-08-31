"""
Main module for the SchoolTutor LangGraph application.
"""
import os
import logging
import streamlit as st

logger = logging.getLogger(__name__)
from src.langgraph.ui.app import StreamlitApp
from src.langgraph.ui.chat import render_chat_ui
from src.langgraph.llm.groqllm import GroqLLM
from src.langgraph.graph.graph_builder import GraphBuilder
from src.langgraph.tracing.langsmith import init_langsmith, display_langsmith_info

def load_langgraph_ai_app():
    """
    Load and run the LangGraph AI tutor application.
    This function initializes and renders the Streamlit UI.
    """
    # Set page configuration first - this MUST be the first Streamlit command
    st.set_page_config(
        page_title="School Tutor",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply global CSS styling
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
    
    # Display important information for first-time users
    if "first_run" not in st.session_state:
        st.info("""
        ### Welcome to School Tutor Agent! 🎓
        
        To get started:
        1. Go to **Study Materials** in the sidebar
        2. Upload PDF textbooks or chapters
        3. Process the documents
        4. Return to **Chat** and ask questions about the content
        
        The AI will only answer based on the content in your PDFs.
        """)
        st.session_state.first_run = True
    
    # Initialize session state if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "graph_builder" not in st.session_state:
        st.session_state.graph_builder = None
        
    # Initialize LangSmith for tracing (if API key is available)
    if os.getenv("LANGSMITH_API_KEY"):
        langsmith_client = init_langsmith(project_name="school-tutor-agent")
        # if langsmith_client:
        #     st.sidebar.success("✅ LangSmith tracing enabled")
        #     # Add LangSmith info to sidebar
        #     with st.sidebar.expander("LangSmith Tracing Info"):
        #         display_langsmith_info()
    
    # Load the UI components (sidebar, etc.)
    ui = StreamlitApp()
    user_input = ui.load_streamlit_ui()
    
    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return
    
    # Get selected objective
    objective = user_input.get("objective")
    
    # Initialize LLM and graph if not already done
    if st.session_state.graph_builder is None and objective:
        obj_llm_config = GroqLLM(user_controls_input=user_input)
        model = obj_llm_config.get_llm_model()
        
        if not model:
            st.error("Error: LLM model could not be initialized. Check your .env file for GROQ_API_KEY.")
            return
            
        # Set up the graph builder
        graph_builder = GraphBuilder(model)
        # Compile the graph and store the compiled graph in session state
        compiled_graph = graph_builder.setup_graph(objective)
        st.session_state.graph_builder = compiled_graph
        
        # Display graph visualization if available
        try:
            from pathlib import Path
            import glob
            
            # Find the most recent graph image
            images_dir = Path(__file__).parent / "graph" / "images"
            if images_dir.exists():
                image_files = sorted(glob.glob(str(images_dir / f"{objective.replace(' ', '_')}*.png")))
                if image_files:
                    latest_image = image_files[-1]
                    with st.sidebar.expander("Graph Visualization", expanded=False):
                        st.image(latest_image, caption="Conversation Flow Graph", use_column_width=True)
                        st.caption(f"Graph structure for {objective}")
                else:
                    # No graph images found
                    with st.sidebar.expander("Graph Visualization", expanded=False):
                        st.info(
                            "Graph visualization is not available. This could be because IPython "
                            "is not installed or the graph visualization failed to generate."
                        )
                        
                        with st.expander("Install missing dependencies"):
                            st.markdown(
                                "To enable graph visualization, install the required packages:\n"
                                "```\n"
                                "pip install ipython\n"
                                "```\n"
                                "Then restart your application."
                            )
        except Exception as e:
            logger.warning(f"Could not display graph visualization: {e}")
    
    # Render the chat UI just once
    render_chat_ui(objective=objective)

if __name__ == "__main__":
    load_langgraph_ai_app()
