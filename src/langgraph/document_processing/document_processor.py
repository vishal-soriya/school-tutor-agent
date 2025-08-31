"""
Document processor module to orchestrate the document processing pipeline.
"""
import logging
import os
from typing import List, Dict, Any, Optional

from src.langgraph.document_processing.pdf_loader import PDFLoader
from src.langgraph.document_processing.text_chunker import TextChunker
from src.langgraph.document_processing.vector_store import WeaviateVectorStore

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    A class to orchestrate the document processing pipeline.
    """
    
    def __init__(
        self,
        vector_store: Optional[WeaviateVectorStore] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the document processor.
        
        Args:
            vector_store: Vector store for document storage
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.pdf_loader = PDFLoader()
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.vector_store = vector_store or WeaviateVectorStore()
        
    def process_pdf(
        self, 
        file_path: str,
        connect_vector_store: bool = True,
        chunk_docs: bool = True
    ) -> List[str]:
        """
        Process a PDF file and store in the vector database.
        
        Args:
            file_path: Path to the PDF file
            connect_vector_store: Whether to connect to the vector store
            chunk_docs: Whether to chunk the documents or keep as full pages
            
        Returns:
            List of document IDs
        """
        try:
            # Extract text from PDF using LangChain loader
            logger.info(f"Processing PDF: {file_path}")
            documents = self.pdf_loader.extract_text_from_pdf(file_path)
            
            # Chunk the text if requested
            if chunk_docs:
                processed_documents = self.chunker.chunk_text(documents)
                logger.info(f"Chunked {len(documents)} pages into {len(processed_documents)} chunks")
            else:
                processed_documents = documents
                logger.info(f"Using {len(documents)} full pages without chunking")
            
            # Store in vector database
            if connect_vector_store:
                self.vector_store.connect()
                
            document_ids = self.vector_store.add_documents(processed_documents)
            
            logger.info(f"Successfully processed {file_path} into {len(document_ids)} chunks/pages")
            return document_ids
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise
            
    def process_uploaded_pdf(
        self,
        uploaded_file,
        connect_vector_store: bool = True,
        chunk_docs: bool = True
    ) -> List[str]:
        """
        Process a PDF uploaded via Streamlit and store in vector database.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            connect_vector_store: Whether to connect to the vector store
            chunk_docs: Whether to chunk the documents or keep as full pages
            
        Returns:
            List of document IDs
        """
        try:
            # Extract text from uploaded PDF using LangChain loader
            logger.info(f"Processing uploaded PDF: {uploaded_file.name}")
            documents = self.pdf_loader.extract_text_from_uploaded_pdf(uploaded_file)
            
            # Chunk the text if requested
            if chunk_docs:
                processed_documents = self.chunker.chunk_text(documents)
                logger.info(f"Chunked {len(documents)} pages into {len(processed_documents)} chunks")
            else:
                processed_documents = documents
                logger.info(f"Using {len(documents)} full pages without chunking")
            
            # Store in vector database
            if connect_vector_store:
                self.vector_store.connect()
                
            document_ids = self.vector_store.add_documents(processed_documents)
            
            logger.info(f"Successfully processed {uploaded_file.name} into {len(document_ids)} chunks/pages")
            return document_ids
            
        except Exception as e:
            logger.error(f"Error processing uploaded PDF {uploaded_file.name}: {e}")
            raise
            
    def search_documents(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters for search
            
        Returns:
            List of relevant documents
        """
        try:
            # Make sure we're connected and schema is set up
            self.vector_store.connect()
            self.vector_store.setup_schema()
            
            # Check if there are any documents in the index
            # If no documents, return empty results to prevent errors
            schema = self.vector_store.client.schema.get()
            class_names = [c['class'] for c in schema.get('classes', [])]
            
            if self.vector_store.index_name not in class_names:
                logger.warning(f"Schema {self.vector_store.index_name} does not exist yet. No documents to search.")
                return []
            
            # Try to search with the query
            return self.vector_store.search(query=query, limit=limit, filters=filters)
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            # Return empty list instead of raising exception
            return []
