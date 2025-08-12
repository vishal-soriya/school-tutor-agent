import streamlit as st
import pandas as pd
import time

def render_progress_tracker():
    """Render the learning progress tracking UI."""
    with st.expander("Progress Tracker"):
        # Topic progress
        st.subheader("Topic Progress")
        
        topics = [
            {"name": "Topic 1", "progress": 80},
            {"name": "Topic 2", "progress": 60},
            {"name": "Topic 3", "progress": 30},
            {"name": "Topic 4", "progress": 90},
        ]
        
        for topic in topics:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(topic["name"])
            with col2:
                st.progress(topic["progress"] / 100)
        
        # Learning statistics
        st.subheader("Learning Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Questions Answered", value="24", delta="+3")
            
        with col2:
            st.metric(label="Accuracy", value="75%", delta="+5%")
            
        with col3:
            st.metric(label="Time Spent", value="3h 15m", delta="+45m")
        
        # Practice history
        st.subheader("Practice History")
        
        # Sample practice history data
        data = {
            "Date": ["2025-08-10", "2025-08-09", "2025-08-08", "2025-08-07"],
            "Topic": ["Topic 1", "Topic 2", "Topic 1", "Topic 3"],
            "Score": [8, 7, 6, 9],
            "Time (min)": [45, 30, 35, 40]
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df)
