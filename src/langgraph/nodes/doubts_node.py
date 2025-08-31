import logging
from src.langgraph.state.state import State
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class ChatbotWithToolNode:
    """
    Chatbot logic enhanced with tool integration and RAG context.
    """
    def __init__(self, model):
        self.llm = model

    def create_chatbot(self, tools):
        """
        Returns a chatbot node function that incorporates retrieved context.
        """
        llm_with_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            """
            Chatbot logic for processing the input state and returning a response.
            Uses system_message from state if available to provide context to the LLM.
            """
            try:
                # Check if we have a system message with context
                system_msg = state.get("system_message")
                if system_msg:
                    # Create a new messages list with system message first
                    messages_with_context = [SystemMessage(content=system_msg)]
                    
                    # Add all non-system messages from the original messages
                    for msg in state["messages"]:
                        if not isinstance(msg, SystemMessage):
                            messages_with_context.append(msg)
                            
                    logger.info("Added context from retriever to LLM prompt")
                    return {"messages": [llm_with_tools.invoke(messages_with_context)]}
                else:
                    logger.warning("No system_message found in state, proceeding without context")
                    return {"messages": [llm_with_tools.invoke(state["messages"])]}
            except Exception as e:
                logger.error(f"Error in chatbot node: {e}")
                # Fallback to original behavior on error
                return {"messages": [llm_with_tools.invoke(state["messages"])]}

        return chatbot_node
