"""
Retriever node for LangGraph to retrieve relevant documents from the vector store.
"""
import logging
import os
from typing import Dict, Any, List, Optional, Callable
from langchain_core.messages import HumanMessage

from src.langgraph.document_processing.document_processor import DocumentProcessor
from src.langgraph.document_processing.vector_store import WeaviateVectorStore

logger = logging.getLogger(__name__)

class CustomRetriever:
    """
    A custom retriever for the Weaviate vector store.
    This doesn't inherit from BaseRetriever to avoid Pydantic issues.
    """
    
    def __init__(
        self,
        document_processor: DocumentProcessor,
        limit: int = 5
    ):
        """
        Initialize the retriever.
        
        Args:
            document_processor: Document processor with vector store
            limit: Maximum number of results to retrieve
        """
        self.document_processor = document_processor
        self.limit = limit
    
    def get_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Get documents relevant to a query.
        
        Args:
            query: The query to search for
            
        Returns:
            List of relevant documents or empty list if none found or error occurs
        """
        if not query:
            logger.warning("Empty query provided to retriever")
            return []
            
        try:
            # Use the document processor to search, which now has better error handling
            docs = self.document_processor.search_documents(
                query=query,
                limit=self.limit
            )
            
            if not docs:
                logger.info(f"No documents found for query: {query[:50]}...")
                
            return docs
            
        except Exception as e:
            logger.error(f"Error in retriever: {e}")
            return []
        



class RetrieverNode:
    """
    A node for retrieving relevant context from the vector store.
    """
    
    def __init__(
        self,
        vector_store: Optional[WeaviateVectorStore] = None,
        limit: int = 5
    ):
        """
        Initialize the retriever node.
        
        Args:
            vector_store: Vector store to retrieve from
            limit: Maximum number of results to retrieve
        """
        self.vector_store = vector_store or WeaviateVectorStore(
            host=os.getenv("WEAVIATE_HOST", "localhost"),
            port=os.getenv("WEAVIATE_PORT", "8080")
        )
        
        # Try to initialize connection and schema
        try:
            self.vector_store.connect()
            self.vector_store.setup_schema()
            logger.info("Successfully connected to Weaviate and set up schema")
        except Exception as e:
            logger.warning(f"Initial Weaviate connection failed: {e}. Will retry during first query.")
        
        self.document_processor = DocumentProcessor(vector_store=self.vector_store)
        self.limit = limit
        self.retriever = CustomRetriever(
            document_processor=self.document_processor,
            limit=limit
        )
        
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant documents based on the last user message.
        
        Args:
            state: The current state with messages
            
        Returns:
            Updated state with retrieved context
        """
        messages = state.get("messages", [])
        
        # Get the most recent user message
        user_message = None
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                user_message = message.content
                break
                
        if not user_message:
            logger.warning("No user message found in state")
            state["context"] = []
            state["system_message"] = "You are a helpful AI tutor. No PDF content has been loaded yet."
            return state
            
        try:
            # Use the retriever to get relevant documents
            retrieved_docs = self.retriever.get_relevant_documents(user_message)
            
            # Format retrieved documents for context
            formatted_context = []
            for i, doc in enumerate(retrieved_docs):
                formatted_doc = {
                    "content": doc["text"],
                    "metadata": doc["metadata"],
                    "relevance_score": 1.0 - doc.get("_distance", 0.0)  # Convert distance to similarity
                }
                formatted_context.append(formatted_doc)
                
            # Add retrieved context to state
            state["context"] = formatted_context
            
            # Add source information if we have context
            if formatted_context:
                sources = [
                    {
                        "title": doc["metadata"].get("file_name", "Unknown"),
                        "page": doc["metadata"].get("page", "Unknown")
                    }
                    for doc in formatted_context
                ]
                state["sources"] = sources
                
                # Create a system message with the context for the LLM
                context_text = "\n\n".join([doc["content"] for doc in formatted_context])
                state["system_message"] = (
                    "You are a helpful AI tutor. Answer the user's question based only on the "
                    "following context. If you can't answer the question based on the context, "
                    "say that you don't know.\n\nContext:\n" + context_text
                )
                
                logger.info(f"Retrieved {len(formatted_context)} documents for query: {user_message[:50]}...")
            else:
                # No documents found, set appropriate system message
                state["sources"] = []
                state["system_message"] = (
                    "You are a helpful AI tutor. No relevant content was found in the uploaded PDFs "
                    "for this question. Please inform the user that they might need to upload PDF "
                    "documents with relevant content or rephrase their question."
                )
                logger.warning(f"No documents found for query: {user_message[:50]}...")
            
            return state
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            # Return empty context with an error message
            state["context"] = []
            state["system_message"] = (
                "You are a helpful AI tutor. There was an error retrieving document context. "
                "Please inform the user that there might be an issue with the PDF processing system."
            )
            return state
