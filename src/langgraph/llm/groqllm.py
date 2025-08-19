import os
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GroqLLM:
    def __init__(self,user_controls_input):
        self.user_controls_input=user_controls_input

    def get_llm_model(self):
        try:
            # Get API key from environment variables loaded from .env file
            groq_api_key = os.getenv("GROQ_API_KEY")
            selected_groq_model=self.user_controls_input['selected_groq_model']
            
            # Check if API key is empty or None
            if not groq_api_key:
                st.error("Please add your GROQ_API_KEY to the .env file")
                return None
                
            # Create the LLM model with the API key
            llm=ChatGroq(api_key=groq_api_key,model=selected_groq_model)
            
        except Exception as e:
            st.error(f"Error occurred: {e}")
            return None
            
        return llm