"""
Main module for the SchoolTutor LangGraph application.
"""
import streamlit as st
from src.langgraph.ui.app import StreamlitApp
from src.langgraph.ui.chat import render_chat_ui
from src.langgraph.llm.groqllm import GroqLLM
from src.langgraph.graph.graph_builder import GraphBuilder

def load_langgraph_ai_app():
    """
    Load and run the LangGraph AI tutor application.
    This function initializes and renders the Streamlit UI.
    """
    # Initialize session state if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "graph_builder" not in st.session_state:
        st.session_state.graph_builder = None
    
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
    
    # Render the chat UI just once
    render_chat_ui(objective=objective)

if __name__ == "__main__":
    load_langgraph_ai_app()
