from langgraph.graph import START,END, StateGraph
from langgraph.prebuilt import tools_condition,ToolNode

from src.langgraph.state.state import State
from src.langgraph.tools.tools import get_tools,create_tool_node
from src.langgraph.nodes.doubts_node import ChatbotWithToolNode

class GraphBuilder:
    def __init__(self,model):
        self.llm=model
        self.graph_builder=StateGraph(State)

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

        ## Define the chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_with_tool_node=obj_chatbot_with_node.create_chatbot(tools)
        
        ## Add nodes
        self.graph_builder.add_node("chatbot",chatbot_with_tool_node)
        self.graph_builder.add_node("tools",tool_node)
        
        # Define conditional and direct edges
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot",tools_condition)
        self.graph_builder.add_edge("tools","chatbot")

    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Revise Topics":
            self.chatbot_with_tools_build_graph()

        return self.graph_builder.compile()
