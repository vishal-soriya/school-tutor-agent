"""
LangSmith tracing configuration for the LangGraph application.
"""
import os
from typing import Optional
import logging
from langsmith import Client
import streamlit as st

logger = logging.getLogger(__name__)

def init_langsmith(
    project_name: Optional[str] = "school-tutor-agent",
    enable_tracing: bool = True
) -> Optional[Client]:
    """
    Initialize LangSmith for tracing LLM calls and graph execution.
    
    Args:
        project_name: The name of the project in LangSmith
        enable_tracing: Whether to enable tracing
        
    Returns:
        LangSmith client if initialization was successful, None otherwise
    """
    if not enable_tracing:
        logger.info("LangSmith tracing is disabled")
        return None
    
    # Get LangSmith API key from environment
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        logger.warning("LANGSMITH_API_KEY not found in environment variables. LangSmith tracing disabled.")
        return None
    
    # Set environment variables for LangSmith
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = project_name
    # Set the endpoint if not already set
    if not os.getenv("LANGSMITH_ENDPOINT"):
        os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    
    try:
        # Initialize the LangSmith client
        client = Client()
        logger.info(f"LangSmith tracing enabled for project '{project_name}'")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LangSmith client: {e}")
        return None

def display_langsmith_info() -> None:
    """
    Display LangSmith information in the Streamlit sidebar.
    This includes a link to the LangSmith dashboard and information about
    what's being traced.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    project_name = os.getenv("LANGSMITH_PROJECT", "school-tutor-agent")
    
    if api_key:
        st.sidebar.success("✅ LangSmith tracing is enabled")
        st.sidebar.markdown(f"**Project**: `{project_name}`")
        
        # Display a link to the LangSmith dashboard
        dashboard_url = "https://smith.langchain.com/"
        st.sidebar.markdown(f"[View traces in LangSmith]({dashboard_url})")
    else:
        st.sidebar.warning("⚠️ LangSmith tracing is disabled")
        st.sidebar.markdown("Add `LANGSMITH_API_KEY` to your .env file to enable tracing.")
