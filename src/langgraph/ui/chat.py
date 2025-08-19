import streamlit as st
import json
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class DisplayResultStreamlit:
    def __init__(self,objective, graph,user_message):
        self.objective = objective
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        objective = self.objective
        graph = self.graph
        user_message = self.user_message
        print(user_message)

        if objective:
            # Prepare state and invoke the graph
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            for message in res['messages']:
                if type(message) == HumanMessage:
                    with st.chat_message("user"):
                        st.write(message.content)
                elif type(message)==ToolMessage:
                    with st.chat_message("ai"):
                        st.write("Tool Call Start")
                        st.write(message.content)
                        st.write("Tool Call End")
                elif type(message)==AIMessage and message.content:
                    with st.chat_message("assistant"):
                        st.write(message.content)

def render_chat_ui(objective):
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
    
    # Chat input at the bottom with a unique key
    if prompt := st.chat_input("Ask your question here...", key="main_chat_input"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with graph if available
        if st.session_state.graph_builder is not None:
            # Create HumanMessage for the graph
            user_message = HumanMessage(content=prompt)
            
            # Set up initial state and invoke the graph
            try:
                initial_state = {"messages": [user_message]}
                # The compiled graph has the invoke method, not the GraphBuilder object
                res = st.session_state.graph_builder.invoke(initial_state)
                
                # Process the response messages
                for message in res.get('messages', []):
                    if isinstance(message, HumanMessage):
                        # Skip displaying the user message again
                        continue
                    elif isinstance(message, ToolMessage):
                        with st.chat_message("tool"):
                            st.write("Tool Call:")
                            st.write(message.content)
                    elif isinstance(message, AIMessage) and message.content:
                        with st.chat_message("assistant"):
                            st.write(message.content)
                            
                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": message.content
                        })
            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")
                # Add error message to chat history
                error_message = f"I encountered an error: {str(e)}"
                if "invoke" in str(e):
                    error_message += "\nThe graph may not be properly compiled. Please reload the application."
                    # Reset the graph builder so it can be rebuilt on next run
                    st.session_state.graph_builder = None
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message
                })
        else:
            # If graph isn't available, show a placeholder response
            with st.chat_message("assistant"):
                response = "I'm setting up your AI tutor. Please make sure you've selected the right options in the sidebar."
                st.markdown(response)
                
                # Add placeholder response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })