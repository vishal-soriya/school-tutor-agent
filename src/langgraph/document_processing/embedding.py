"""
Embedding module for generating embeddings from text.
"""
import logging
from typing import List, Dict, Any

import os
import sentence_transformers

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """
    A class to generate embeddings from text.
    Note: With Weaviate's text2vec-transformers module,
    we don't need to generate embeddings ourselves.
    This class is for standalone use or custom embedding scenarios.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the model to use for embeddings
        """
        self.model_name = model_name
        self.model = None
        
    def load_model(self) -> None:
        """
        Load the embedding model.
        """
        try:
            self.model = sentence_transformers.SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
            
    def generate_embeddings(
        self, 
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings as float arrays
        """
        if not self.model:
            self.load_model()
            
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
