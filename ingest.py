import os
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PDF_DATA_DIRECTORY = Path("data")
VECTOR_STORE_DIR = "chroma_db"
SUPPLY_CHAIN_COLLECTION_ID = "supply_chain_documents_db"


def process_and_embed_documents():
    """Load PDFs, split them into chunks, create Gemini embeddings, and store them in Chroma."""

    pdf_paths = sorted(PDF_DATA_DIRECTORY.glob("*.pdf"))

    if not pdf_paths:
        raise FileNotFoundError(
            "No PDF files found in the data/ directory."
        )

    extracted_pages = []

    # Load PDFs
    for pdf_path in pdf_paths:

        print(f"Reading: {pdf_path.name}")

        pdf_reader = PyPDFLoader(str(pdf_path))
        pdf_pages = pdf_reader.load()

        for single_page in pdf_pages:
            single_page.metadata["source_file"] = pdf_path.name

        extracted_pages.extend(pdf_pages)

    print(f"Loaded {len(extracted_pages)} pages.")

    # Split documents
    text_chunker = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    document_chunks = text_chunker.split_documents(extracted_pages)

    print(f"Created {len(document_chunks)} chunks.")

    # Gemini embeddings
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    # ChromaDB
    chroma_instance = Chroma(
        collection_name=SUPPLY_CHAIN_COLLECTION_ID,
        embedding_function=embedding_model,
        persist_directory=VECTOR_STORE_DIR,
    )

    # Generate stable IDs for deduplication
    chunk_ids = []
    for chunk in document_chunks:
        source = chunk.metadata.get("source_file", "unknown")
        page = chunk.metadata.get("page", 0)
        content_hash = hashlib.md5(chunk.page_content.encode('utf-8')).hexdigest()
        chunk_ids.append(f"{source}_page{page}_{content_hash}")

    chroma_instance.add_documents(document_chunks, ids=chunk_ids)

    print("Embeddings created and stored in ChromaDB.")

    return len(pdf_paths), len(document_chunks)


if __name__ == "__main__":
    files_processed, chunks_stored = process_and_embed_documents()

    print(f"Processed {files_processed} PDF(s).")
    print(f"Stored {chunks_stored} chunks in ChromaDB.")