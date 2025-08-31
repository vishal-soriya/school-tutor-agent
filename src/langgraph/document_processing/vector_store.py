"""
Vector store module for managing document embeddings with Weaviate.
"""
import os
import uuid
import hashlib
import logging
from typing import List, Dict, Any, Optional, Union
import weaviate
from weaviate.client import Client
from weaviate.exceptions import WeaviateBaseError

logger = logging.getLogger(__name__)

class WeaviateVectorStore:
    """
    A class to manage document embeddings using Weaviate.
    """
    
    def __init__(
        self,
        host: str = os.getenv("WEAVIATE_HOST", "localhost"),
        port: str = os.getenv("WEAVIATE_PORT", "8080"),
        api_key: Optional[str] = None,
        index_name: str = "SchoolTutorDocuments",
        embedding_model: str = "text2vec-transformers",
    ):
        """
        Initialize the Weaviate vector store.
        
        Args:
            host: Weaviate host address
            port: Weaviate port
            api_key: Weaviate API key (if using cloud)
            index_name: Name of the class in Weaviate
            embedding_model: Model for text embeddings
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.client = None
        
    def connect(self) -> None:
        """
        Connect to the Weaviate server.
        """
        try:
            url = f"http://{self.host}:{self.port}"
            auth_config = None
            
            if self.api_key:
                auth_config = weaviate.auth.AuthApiKey(api_key=self.api_key)
                
            self.client = weaviate.Client(
                url=url,
                auth_client_secret=auth_config,
                additional_headers={
                    "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY", "")  # Optional for OpenAI models
                }
            )
            
            if self.client.is_ready():
                logger.info(f"Successfully connected to Weaviate at {url}")
            else:
                raise ConnectionError("Weaviate server is not ready")
                
        except Exception as e:
            logger.error(f"Error connecting to Weaviate: {e}")
            raise
            
    def setup_schema(self) -> None:
        """
        Create the schema for document storage if it doesn't exist.
        """
        if not self.client:
            self.connect()
            
        try:
            # Check if schema already exists
            schema = self.client.schema.get()
            class_names = [c['class'] for c in schema['classes']] if 'classes' in schema else []
            
            if self.index_name in class_names:
                logger.info(f"Schema {self.index_name} already exists")
                return
                
            # Define schema
            class_obj = {
                "class": self.index_name,
                "description": "School Tutor document storage for PDF content",
                "vectorizer": self.embedding_model,
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "The text content of the document chunk",
                    },
                    {
                        "name": "source",
                        "dataType": ["string"],
                        "description": "The source file path",
                    },
                    {
                        "name": "file_name",
                        "dataType": ["string"],
                        "description": "The name of the file",
                    },
                    {
                        "name": "page",
                        "dataType": ["int"],
                        "description": "The page number in the PDF",
                    },
                    {
                        "name": "total_pages",
                        "dataType": ["int"],
                        "description": "Total pages in the PDF",
                    },
                    {
                        "name": "chunk",
                        "dataType": ["int"],
                        "description": "Chunk number",
                    },
                ],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "poolingStrategy": "masked_mean",
                        "vectorizeClassName": False
                    }
                }
            }
            
            # Create the schema
            self.client.schema.create_class(class_obj)
            logger.info(f"Created schema {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error setting up schema: {e}")
            raise
            
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        batch_size: int = 50
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents with text and metadata
            batch_size: Size of batches for insertion
            
        Returns:
            List of document IDs
        """
        if not self.client:
            self.connect()
            
        # Ensure schema exists
        self.setup_schema()
        
        document_ids = []
        with self.client.batch as batch:
            batch.batch_size = batch_size
            
            for doc in documents:
                # Generate a UUID based on content for deduplication using MD5 hash
                # This ensures we get a valid UUID that's consistently derived from the content
                content_hash = hashlib.md5(doc["text"].encode('utf-8')).hexdigest()
                doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
                
                # Prepare properties
                properties = {
                    "content": doc["text"],
                    "source": doc["metadata"].get("source", ""),
                    "file_name": doc["metadata"].get("file_name", ""),
                    "page": doc["metadata"].get("page", 0),
                    "total_pages": doc["metadata"].get("total_pages", 0),
                    "chunk": doc["metadata"].get("chunk", 0),
                }
                
                # Add to batch
                batch.add_data_object(
                    data_object=properties,
                    class_name=self.index_name,
                    uuid=doc_id
                )
                document_ids.append(doc_id)
                
        logger.info(f"Added {len(documents)} documents to Weaviate")
        return document_ids
        
    def search(
        self, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on a query.
        
        Args:
            query: The search query
            limit: Maximum number of results
            filters: Optional filters for the search
            
        Returns:
            List of relevant documents or empty list on error
        """
        if not self.client:
            try:
                self.connect()
            except Exception as e:
                logger.error(f"Failed to connect to Weaviate: {e}")
                return []
        
        # Ensure schema exists before searching
        try:
            self.setup_schema()
        except Exception as e:
            logger.error(f"Failed to ensure schema exists: {e}")
            return []
            
        try:
            # Check if there are any objects in the class before searching
            class_count = self.client.query.aggregate(self.index_name).with_meta_count().do()
            count = class_count.get('data', {}).get('Aggregate', {}).get(self.index_name, [{}])[0].get('meta', {}).get('count', 0)
            
            if count == 0:
                logger.warning(f"No objects found in class {self.index_name}, search will return empty results")
                return []
            
            # Start building the query
            search_query = self.client.query.get(
                class_name=self.index_name,
                properties=["content", "source", "file_name", "page", "chunk", "total_pages"]
            )
            
            # Add vector search
            search_query = search_query.with_near_text({"concepts": [query]})
            
            # Add limit
            search_query = search_query.with_limit(limit)
            
            # Add filters if provided
            if filters:
                where_filter = {}
                for key, value in filters.items():
                    if isinstance(value, list):
                        where_filter[key] = {
                            "operator": "ContainsAny",
                            "valueText": value
                        }
                    else:
                        where_filter[key] = {
                            "operator": "Equal",
                            "valueText": value
                        }
                search_query = search_query.with_where(where_filter)
            
            # Execute the query
            results = search_query.do()
            
            # Process results
            documents = []
            if 'data' in results and 'Get' in results['data'] and self.index_name in results['data']['Get']:
                for item in results['data']['Get'][self.index_name]:
                    documents.append({
                        "text": item.get("content", ""),
                        "metadata": {
                            "source": item.get("source", ""),
                            "file_name": item.get("file_name", ""),
                            "page": item.get("page", 0),
                            "chunk": item.get("chunk", 0),
                            "total_pages": item.get("total_pages", 0),
                        },
                        "_distance": item.get("_additional", {}).get("distance", 1.0)
                    })
                    
            return documents
            
        except Exception as e:
            logger.error(f"Error searching in Weaviate: {e}")
            return []  # Return empty list instead of raising exception
            
    def delete_by_filter(
        self, 
        filters: Dict[str, Any]
    ) -> int:
        """
        Delete documents based on filters.
        
        Args:
            filters: Filters to match documents for deletion
            
        Returns:
            Number of deleted documents
        """
        if not self.client:
            self.connect()
            
        try:
            where_filter = {}
            for key, value in filters.items():
                if isinstance(value, list):
                    where_filter[key] = {
                        "operator": "ContainsAny",
                        "valueText": value
                    }
                else:
                    where_filter[key] = {
                        "operator": "Equal",
                        "valueText": value
                    }
                    
            result = self.client.batch.delete_objects(
                class_name=self.index_name,
                where=where_filter
            )
            
            return result.get("results", {}).get("successful", 0)
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
