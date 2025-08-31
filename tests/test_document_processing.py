"""
Integration test for document processing pipeline.
"""
import os
import logging
import argparse
from dotenv import load_dotenv

from src.langgraph.document_processing.document_processor import DocumentProcessor
from src.langgraph.document_processing.vector_store import WeaviateVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_pdf_processing(pdf_path, chunk_size=1000, chunk_overlap=200):
    """
    Test the PDF processing pipeline.
    
    Args:
        pdf_path: Path to a PDF file
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    logger.info(f"Testing PDF processing with {pdf_path}")
    
    # Set up the vector store
    vector_store = WeaviateVectorStore(
        host=os.getenv("WEAVIATE_HOST", "localhost"),
        port=os.getenv("WEAVIATE_PORT", "8080"),
    )
    
    # Set up the document processor
    doc_processor = DocumentProcessor(
        vector_store=vector_store,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    try:
        # Process the PDF
        logger.info("Testing PDF extraction and chunking...")
        doc_ids = doc_processor.process_pdf(pdf_path)
        logger.info(f"Successfully processed PDF into {len(doc_ids)} chunks")
        
        # Test search
        logger.info("Testing vector search...")
        query = "What is the main topic of this document?"
        results = doc_processor.search_documents(query, limit=3)
        
        logger.info(f"Found {len(results)} results for query: {query}")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}:")
            logger.info(f"  Page: {result['metadata']['page']}")
            logger.info(f"  Chunk: {result['metadata'].get('chunk', 'N/A')}")
            logger.info(f"  Text preview: {result['text'][:100]}...")
            
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test PDF processing pipeline')
    parser.add_argument('pdf_path', help='Path to a PDF file')
    parser.add_argument('--chunk-size', type=int, default=1000, help='Chunk size')
    parser.add_argument('--chunk-overlap', type=int, default=200, help='Chunk overlap')
    
    args = parser.parse_args()
    
    success = test_pdf_processing(args.pdf_path, args.chunk_size, args.chunk_overlap)
    
    if success:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
        exit(1)
