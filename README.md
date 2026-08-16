# Meridian Supply Chain RAG Assistant

A Retrieval-Augmented Generation (RAG) application for answering supply-chain and procurement questions using Meridian Components' internal PDF documents.


LIVE APP: https://meridian-supply-chain-rag.streamlit.app/
## Features

- PDF document ingestion
- Recursive character chunking
- OpenAI `text-embedding-3-small` embeddings
- Persistent ChromaDB vector store
- GPT-4o answer generation
- Source document and page display
- Cross-document question answering
- Guardrail against unsupported answers
- Streamlit interface

## Architecture

```text
PDFs
  ↓
PyPDFLoader
  ↓
RecursiveCharacterTextSplitter
  ↓
OpenAI text-embedding-3-small
  ↓
Persistent ChromaDB
  ↓
Similarity Search (Top-K)
  ↓
GPT-4o
  ↓
Answer + Sources
```

## Chunking Configuration

- Chunk size: **1000 characters**
- Chunk overlap: **150 characters**
- Retrieval: **Top 6 chunks by default**

These values balance context preservation with retrieval precision. The overlap helps prevent important sentences from being separated at chunk boundaries.

## Project Structure

```text
supplychain-rag/
├── app.py
├── ingest.py
├── rag.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── data/
│   ├── Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf
│   └── Meridian_Procurement_Policy_Handbook_v4.2.pdf
└── chroma_db/
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Edit `.env`:

```text
OPENAI_API_KEY=your_actual_key
```

Never commit `.env` to GitHub.

### 4. Add the PDFs

Place the Meridian PDFs in:

```text
data/
```

### 5. Build the vector database

```bash
python ingest.py
```

### 6. Run the application

```bash
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

## Recommended Test Questions

1. Which supplier had the highest spend in Q1, and what was its on-time delivery percentage?
2. How many line stoppages happened in Q1, what was the total downtime, and what caused them?
3. What is the approval authority for a purchase order worth ₹1.4 crore?
4. What are the four supplier classification categories, and what qualifies a supplier as Critical?
5. Kaveri Metals recorded 88.1% on-time delivery and 1,150 defects per million in Q1. Which policy clauses does this trigger, and what exactly must the buyer do?
6. Microcontrollers are imported with a 46-day lead time. Using the safety-stock policy, how many days of stock should be held?
7. Trident Circuit Boards had a defect rate of 640 parts per million. What is the cost consequence under the policy?
8. The microcontroller supplier is single-source. What does the sourcing policy require, and what is Meridian already doing about it?
9. What is the annual salary of the Head of Procurement?
10. What policy requirement applies to a Critical supplier's second source?

## Persistence Test

After running:

```bash
python ingest.py
```

the Chroma database is stored locally in:

```text
chroma_db/
```

Stop and restart Streamlit. The application should still be able to retrieve indexed information without rebuilding the database.

## Hallucination / Grounding Test

Ask a question whose answer is not present in either PDF, for example:

> What is the annual salary of the Head of Procurement?

The application should respond:

> The information is not available in the uploaded documents.

## Troubleshooting

### No API key

Check `.env` and make sure `OPENAI_API_KEY` is set.

### No documents found

Make sure the PDFs are inside the `data/` directory.

### Empty ChromaDB

Run:

```bash
python ingest.py
```

again after adding the PDFs.

### Retrieval quality is weak

Try increasing `top_k` in the Streamlit interface. Cross-document questions often benefit from retrieving 6 or more chunks.

## Security

Do not commit:

- `.env`
- OpenAI API keys
- private credentials

The `.gitignore` file is configured to prevent accidental commits of these files.

## Demo

Add the final 3-minute demonstration video link here.

## Assignment Notes

This implementation covers the core RAG requirements:

- PDF ingestion
- Recursive chunking
- OpenAI embeddings
- ChromaDB persistence
- Similarity retrieval
- GPT-4o generation
- Source attribution
- Cross-document reasoning
- Grounded-response guardrails
- Streamlit UI
