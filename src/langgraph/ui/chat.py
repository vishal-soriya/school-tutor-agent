import streamlit as st

def render_chat_ui():
    """Render the main chat interface."""
    # st.subheader("Chat with your AI Tutor")
    
    # Ensure the content uses full width
    st.markdown("""
        <style>
            /* Make the app use the full width */
            .block-container {
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Simple dark theme with indigo blue accent for chat
    st.markdown("""
    <style>
        /* User message styling with indigo blue accent */
        .stChatMessage [data-testid="chatAvatarIcon-user"] {
            background-color: #4e42f5 !important; /* Indigo Blue */
        }
        
        /* Assistant message styling with lighter indigo */
        .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
            background-color: #6b61f8 !important; /* Lighter Indigo */
        }
        
        /* Chat message text - white */
        .stChatMessage p, .stChatMessage div {
            color: #FFFFFF !important;
            font-size: 16px !important;
        }
        
        /* Message container - dark theme */
        .stChatMessage {
            background-color: #333333 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            margin-bottom: 8px !important;
            transition: all 0.3s !important;
        }
        
        /* Message container hover - add white border */
        .stChatMessage:hover {
            border: 1px solid white !important;
            box-shadow: 0 0 5px rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Chat input box - using default Streamlit theme */
        .stChatInput {
            border: none !important; /* Remove outer border */
            border-radius: 6px !important;
            padding: 8px !important;
            font-size: 16px !important;
            background-color: #333333 !important;
            color: white !important;
            transition: all 0.3s !important;
        }
        
        /* Chat input hover - subtle effect without border */
        .stChatInput:hover, .stChatInput:focus {
            box-shadow: 0 0 5px rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Input container - full width */
        .stChatInputContainer {
            background-color: transparent !important;
            padding-bottom: 10px !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Ensure the chat input takes full width */
        .stChatInput, div[data-testid="stChatInput"] {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Target the specific input element for full width */
        .stChatInput input, div[data-testid="stChatInput"] input {
            width: 100% !important;
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Container for messages - will be autoscrolled by Streamlit
    message_container = st.container()
    
    # Display existing messages with dark theme styling
    with message_container:
        # Show empty state if no messages with default Streamlit styling
        if not st.session_state.messages:
            st.info("👋 Send a message to start chatting with your AI Tutor")
            
        # Display existing messages with dark theme formatting
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input at the bottom
    if prompt := st.chat_input("Ask your question here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simulate AI response (placeholder)
        with st.chat_message("assistant"):
            response = "I'm your AI tutor. I'll help you with your studies!"
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # No need for rerun - Streamlit will automatically rerun with the updated session state
