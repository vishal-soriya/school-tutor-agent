"""
PDF Upload UI component for the Streamlit application.
"""
import os
import streamlit as st

from src.langgraph.document_processing.document_processor import DocumentProcessor
from src.langgraph.document_processing.vector_store import WeaviateVectorStore

def render_pdf_upload_ui():
    """
    Render the PDF upload UI component.
    """
    st.subheader("Upload Study Materials")
    
    # Create document processor
    vector_store = WeaviateVectorStore(
        host=os.getenv("WEAVIATE_HOST", "localhost"),
        port=os.getenv("WEAVIATE_PORT", "8080")
    )
    doc_processor = DocumentProcessor(vector_store=vector_store)
    
    # Upload multiple files
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader"
    )
    
    if uploaded_files:
        # Initialize session state for document tracking if not exists
        if "processed_docs" not in st.session_state:
            st.session_state.processed_docs = []
            
        # Process button
        if st.button("Process Documents", key="process_docs_btn"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Connect to vector store first to validate connection
                vector_store.connect()
                # Ensure the schema exists
                vector_store.setup_schema()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Update progress
                        progress = (i + 0.5) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {uploaded_file.name}...")
                        
                        # Process file
                        doc_ids = doc_processor.process_uploaded_pdf(
                            uploaded_file,
                            connect_vector_store=False  # Already connected above
                        )
                        
                        # Add to processed documents
                        st.session_state.processed_docs.append({
                            "name": uploaded_file.name,
                            "chunks": len(doc_ids)
                        })
                    except Exception as file_error:
                        st.error(f"Error processing {uploaded_file.name}: {str(file_error)}")
                        continue
                    
                    # Update progress again
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                
                # Finalize
                progress_bar.progress(1.0)
                status_text.text("Processing complete!")
                st.success(f"Successfully processed {len(uploaded_files)} documents")
                
            except Exception as e:
                st.error(f"Error processing documents: {str(e)}")
                
    # Display processed documents
    if "processed_docs" in st.session_state and st.session_state.processed_docs:
        st.subheader("Processed Documents")
        
        for doc in st.session_state.processed_docs:
            st.write(f"📄 {doc['name']} - {doc['chunks']} chunks")
            
        if st.button("Clear All Documents", key="clear_docs_btn"):
            # Clear from vector store
            try:
                vector_store.connect()
                # Delete all documents (no filter means all)
                vector_store.delete_by_filter({})
                st.session_state.processed_docs = []
                st.success("All documents cleared from the database")
            except Exception as e:
                st.error(f"Error clearing documents: {str(e)}")
    
    # Show connection status
    with st.expander("Vector Database Status"):
        if st.button("Check Connection", key="check_connection_btn"):
            try:
                vector_store.connect()
                if vector_store.client.is_ready():
                    st.success("Successfully connected to Weaviate")
                else:
                    st.error("Weaviate is not ready")
            except Exception as e:
                st.error(f"Error connecting to Weaviate: {str(e)}")
                st.info("Make sure Weaviate is running in Docker")
