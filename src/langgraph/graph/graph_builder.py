import os
import logging
import datetime
import traceback
from pathlib import Path
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from src.langgraph.state.state import State
from src.langgraph.tools.tools import get_tools, create_tool_node
from src.langgraph.nodes.doubts_node import ChatbotWithToolNode
from src.langgraph.nodes.retriever.retriever_node import RetrieverNode
from src.langgraph.tracing.langsmith import init_langsmith

logger = logging.getLogger(__name__)

class GraphBuilder:
    def __init__(self, model, project_name="school-tutor-agent"):
        self.llm = model
        self.project_name = project_name
        
        # Initialize LangSmith for tracing
        self.langsmith_client = init_langsmith(project_name=project_name)
        if self.langsmith_client:
            logger.info(f"LangSmith tracing enabled for project '{project_name}'")
            
        # Create the state graph
        self.graph_builder = StateGraph(State)

    def chatbot_with_tools_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node 
        and a tool node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """
        ## Define the tool and tool node
        tools=get_tools()
        tool_node=create_tool_node(tools)

        ## Define the LLM
        llm=self.llm
        
        ## Define the retriever node
        retriever_node = RetrieverNode()

        ## Define the chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_with_tool_node=obj_chatbot_with_node.create_chatbot(tools)
        
        ## Add nodes
        self.graph_builder.add_node("retriever", retriever_node)
        self.graph_builder.add_node("chatbot", chatbot_with_tool_node)
        self.graph_builder.add_node("tools", tool_node)
        
        # Define graph flow with retrieval
        self.graph_builder.add_edge(START, "retriever")
        self.graph_builder.add_edge("retriever", "chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools", "chatbot")

    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case and generates a visualization.
        
        Args:
            usecase: The selected use case ("Revise Topics", etc.)
            
        Returns:
            Compiled graph
        """
        if usecase == "Revise Topics":
            self.chatbot_with_tools_build_graph()
        
        # Generate and save graph visualization (best effort)
        self.save_graph_image(usecase)
        
        # Compile with tracing if LangSmith is available
        if os.getenv("LANGSMITH_API_KEY"):
            # Enable tracing
            logger.info("Compiling graph with LangSmith tracing enabled")
            return self.graph_builder.compile(
                name=f"Tutor-{usecase.replace(' ', '-')}",
                checkpointer=None  # You can add a checkpointer here if needed
            )
        else:
            # Compile without tracing
            logger.warning("Compiling graph without LangSmith tracing")
            return self.graph_builder.compile()
            
    def save_graph_image(self, usecase: str):
        """
        Generate a visualization of the current graph and save it as an image using Mermaid.
        
        Args:
            usecase: The name of the use case for the filename
            
        Returns:
            Path to the saved image or None if failed
        """
        try:
            # Ensure the images directory exists
            images_dir = Path(__file__).parent / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Create a timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{usecase.replace(' ', '_')}_{timestamp}.png"
            filepath = images_dir / filename
            
            # Compile the graph to get access to the memory object
            compiled_graph = self.graph_builder.compile(name=f"Temp-{usecase.replace(' ', '-')}")
            
            # Try to generate a graph image using Mermaid
            try:
                # Check if IPython is available
                import importlib.util
                if importlib.util.find_spec("IPython"):
                    # Get the mermaid PNG data and save it
                    png_data = compiled_graph.get_graph().draw_mermaid_png()
                    if png_data:
                        with open(filepath, "wb") as f:
                            f.write(png_data)
                        logger.info(f"Graph visualization saved to {filepath}")
                        return str(filepath)
            except Exception as e:
                logger.warning(f"Could not generate graph image with mermaid: {e}")
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to save graph image: {e}")
            logger.debug(traceback.format_exc())
            return None
