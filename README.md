# School Tutor Agent

AI tutor that helps students to revise exact topics from PDF documents of textbook chapters:
- Quickly revise topics
- Ask practice questions
- Memory mapping for last minute preparations
- Trick questions

## Features

- **PDF-Based Learning**: Upload textbook PDFs and chat about specific content
- **Context-Aware Responses**: AI only responds based on the content in your PDFs
- **Scalable Architecture**: Built with LangGraph and Weaviate vector database
- **Dockerized Setup**: Easy deployment with Docker Compose

## Architecture

The application uses a Retrieval-Augmented Generation (RAG) approach:
1. PDF documents are processed, chunked, and stored in Weaviate
2. User queries trigger semantic search in the vector database
3. Relevant context is retrieved and used to generate accurate responses
4. The LangGraph framework manages the conversation flow## Setup and Installation

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
   - Weaviate UI will be available at [http://localhost:9090](http://localhost:9090)

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
- PDF text extraction using LangChain's document loaders (PyPDF and PDFMiner)
- Text chunking with RecursiveCharacterTextSplitter for smart context preservation
- Vector embeddings using Weaviate's text2vec-transformers module
- Storage in Weaviate vector database with semantic search capabilities

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

## LangSmith Integration

This project integrates [LangSmith](https://smith.langchain.com/) for tracing, debugging, and analyzing the application's behavior.

### Features
- **Token Usage Tracking**: Monitor the number of tokens consumed by LLM calls
- **Graph Execution Tracing**: Visualize the flow of data through the LangGraph nodes
- **Query History**: Review past queries and their full context
- **Error Analysis**: Identify and debug failures in the retrieval or generation process

### Setup LangSmith

1. Sign up for a [LangSmith](https://smith.langchain.com/) account
2. Get your API key from the LangSmith dashboard
3. Add it to your `.env` file:
   ```
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   ```

When the application starts with a valid LangSmith API key, tracing will be automatically enabled and a link to your traces will be available in the sidebar.

## Acknowledgements

- Built with [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [Weaviate](https://weaviate.io/) for vector storage
- UI built with [Streamlit](https://streamlit.io/)
- Tracing and monitoring with [LangSmith](https://smith.langchain.com/)
