# SupplyDesk Conversational AI

A production-ready, Retrieval-Augmented Generation (RAG) application for answering supply-chain and procurement questions. SupplyDesk leverages **Google Gemini 2.5 Flash** and **ChromaDB** to allow users to interact seamlessly with internal documents using a context-aware conversational chat interface.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)

## Features

- **Context-Aware Chat Interface**: A conversational UI with memory (session state), allowing users to ask natural follow-up questions.
- **Google Gemini Integrations**: Powered by `gemini-2.5-flash` for high-speed generation and `models/gemini-embedding-001` for embeddings.
- **Optimized Document Ingestion**: Deduplicated vector ingestion into persistent ChromaDB using stable cryptographic chunk hashing.
- **Intelligent Chunking**: Recursive character splitting (1000 size / 150 overlap) ensuring robust semantic boundaries.
- **Transparent Sourcing**: Every answer includes expandable citations linked to specific pages of the source documents.
- **Resource Caching**: Streamlit resource caching guarantees blazing fast app navigation and low API latency.

## Architecture

```text
PDF Documents
      ↓
PyPDFLoader & Recursive Text Splitter
      ↓
Stable MD5 Deduplication
      ↓
Google Gemini Embeddings
      ↓
Persistent ChromaDB Vector Store
      ↓
Similarity Search (Dynamic Top-K) + Chat History
      ↓
Gemini 2.5 Flash
      ↓
Context-Aware Answer + Source Citations
```

## Setup & Installation

### 1. Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Credentials

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```
> **Note**: Never commit your `.env` file. It is explicitly ignored in `.gitignore`.

### 4. Add Knowledge Base Documents

Place your PDF documents into the `data/` directory (create it if it doesn't exist). Alternatively, you can upload them directly via the Streamlit UI once the app is running.

## Usage

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

### Production Optimization Notes

- **Caching**: The database connections and LLM models are cached globally via `@st.cache_resource`, ensuring high throughput.
- **Deduplication**: When new documents are added or the "Index Documents" button is clicked, SupplyDesk calculates MD5 hashes of all chunks to prevent redundant vector database entries.
- **UI State**: Interaction history is managed through `st.session_state` preserving multi-turn conversations safely across Streamlit re-runs.

## Troubleshooting

- **No API key found:** Check `.env` and ensure `GEMINI_API_KEY` is set correctly. For Streamlit Cloud deployments, add it to the Secrets management console.
- **Empty Knowledge Base:** If the bot cannot find any information, ensure PDFs are uploaded and click "Index Documents" on the sidebar.
- **Retrieval Quality:** If the answers lack context, increase the "Retrieved chunks" slider in the UI to widen the semantic search radius.
