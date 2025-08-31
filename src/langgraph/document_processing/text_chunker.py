"""
Text chunker module for splitting text into smaller chunks for embedding using LangChain.
"""
import logging
from typing import List, Dict, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class TextChunker:
    """
    A class to split text into smaller chunks for embedding using LangChain text splitters.
    """
    
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize the text chunker with LangChain's RecursiveCharacterTextSplitter.
        
        Args:
            chunk_size: The size of each chunk in characters
            chunk_overlap: The overlap between chunks in characters
            separators: List of separators to use for splitting, in order of priority
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators in priority order if none provided
        self.separators = separators or [
            "\n\n",  # Paragraphs
            "\n",    # Line breaks
            ". ",    # Sentences
            ", ",    # Phrases
            " ",     # Words
            ""       # Characters
        ]
        
        # Create the LangChain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )
        
    def chunk_text(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Split documents into smaller chunks using LangChain's text splitter.
        
        Args:
            documents: List of dictionaries with text and metadata
            
        Returns:
            List of dictionaries with chunked text and metadata
        """
        # Convert to LangChain Document format for splitting
        langchain_docs = []
        for doc in documents:
            if not doc["text"] or not doc["text"].strip():
                continue
                
            langchain_docs.append(
                Document(
                    page_content=doc["text"], 
                    metadata=doc["metadata"]
                )
            )
        
        # Use LangChain's splitter to chunk the documents
        chunked_langchain_docs = self.text_splitter.split_documents(langchain_docs)
        
        # Convert back to our format
        chunked_documents = []
        for i, doc in enumerate(chunked_langchain_docs):
            # Copy metadata and add chunk information
            metadata = doc.metadata.copy()
            metadata["chunk"] = i + 1
            
            chunked_documents.append({
                "text": doc.page_content,
                "metadata": metadata
            })
        
        logger.info(f"Split {len(documents)} documents into {len(chunked_documents)} chunks")
        return chunked_documents
