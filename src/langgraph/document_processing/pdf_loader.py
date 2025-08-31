"""
PDF loader module to extract text from PDF files using LangChain's document loaders.
"""
import os
import logging
import tempfile
from typing import List, Dict, Any, Optional
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader, PDFMinerLoader, DirectoryLoader
from langchain_community.document_loaders.base import BaseLoader

logger = logging.getLogger(__name__)

class PDFLoader:
    """
    A class to extract text and metadata from PDF files using LangChain loaders.
    """
    
    def __init__(self, use_pypdf: bool = True):
        """
        Initialize the PDF loader.
        
        Args:
            use_pypdf: Whether to use PyPDFLoader (True) or PDFMinerLoader (False)
        """
        self.use_pypdf = use_pypdf
        
    def get_loader(self, file_path: str) -> BaseLoader:
        """
        Get the appropriate document loader based on settings.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            LangChain document loader
        """
        if self.use_pypdf:
            return PyPDFLoader(file_path)
        else:
            return PDFMinerLoader(file_path)
        
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from a PDF file with metadata using LangChain.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries with text content and metadata
        """
        try:
            # Load documents with LangChain's loader
            loader = self.get_loader(file_path)
            langchain_docs = loader.load()
            
            # Convert LangChain documents to our format
            documents = []
            file_name = os.path.basename(file_path)
            total_pages = len(langchain_docs)
            
            for doc in langchain_docs:
                page = doc.metadata.get("page", 0) + 1  # LangChain uses 0-indexed pages
                
                documents.append({
                    "text": doc.page_content,
                    "metadata": {
                        "source": file_path,
                        "file_name": file_name,
                        "page": page,
                        "total_pages": total_pages
                    }
                })
            
            logger.info(f"Successfully extracted text from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
            
    def extract_text_from_uploaded_pdf(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Extract text from a PDF uploaded via Streamlit.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of dictionaries with text content and metadata
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                # Write uploaded file content to temp file
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = tmp_file.name
            
            # Process the temporary file
            documents = self.extract_text_from_pdf(temp_path)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error extracting text from uploaded PDF {uploaded_file.name}: {e}")
            raise
