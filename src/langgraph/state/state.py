from typing_extensions import TypedDict, List, Optional
from langgraph.graph.message import add_messages
from typing import Annotated, Dict, Any, Union


class State(TypedDict, total=False):
    """
    Represent the structure of the state used in graph
    
    Includes fields for RAG context and system messages
    """
    
    messages: Annotated[List, add_messages]
    context: List[Dict[str, Any]]  # Retrieved document context
    system_message: str  # System message with context for the LLM
    sources: List[Dict[str, Union[str, int]]]  # Source information for retrieved documents