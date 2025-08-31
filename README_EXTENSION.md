## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/vishal-soriya/school-tutor-agent.git
   cd school-tutor-agent
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Add your API keys to the `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Build and start the Docker containers:
   ```bash
   docker-compose up -d --build
   ```

5. Access the application at [http://localhost:8501](http://localhost:8501)

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vishal-soriya/school-tutor-agent.git
   cd school-tutor-agent
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   WEAVIATE_HOST=localhost
   WEAVIATE_PORT=8080
   ```

4. Start Weaviate using Docker:
   ```bash
   docker-compose up -d weaviate t2v-transformers
   ```

5. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Go to the "Study Materials" tab
2. Upload PDF textbooks or chapters
3. Process the documents (they'll be stored in Weaviate)
4. Switch to the "Chat" tab
5. Start asking questions about the content in your PDFs

## Technical Details

### Document Processing Pipeline
- PDF text extraction using PyMuPDF
- Text chunking with overlap for context preservation
- Vector embeddings using SentenceTransformers
- Storage in Weaviate vector database

### Retrieval Process
- User query is embedded and compared to document chunks
- Top matches are retrieved based on semantic similarity
- Retrieved context is provided to the LLM along with the query
- The LLM generates responses based only on the retrieved context

### Graph Flow
1. User Input → 
2. Retriever Node (gets context) →
3. Chatbot Node (generates response with context) →
4. Tool Node (if needed) →
5. Back to Chatbot Node

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Built with [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [Weaviate](https://weaviate.io/) for vector storage
- UI built with [Streamlit](https://streamlit.io/)
