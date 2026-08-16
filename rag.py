import os
import streamlit as st

from dotenv import load_dotenv
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_chroma import Chroma

load_dotenv()


# ---------------------------------------------------------
# GEMINI API KEY
# ---------------------------------------------------------

def get_gemini_api_key():
    """Get Gemini API key from local .env or Streamlit Cloud secrets."""

    # Local .env
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    # Streamlit Cloud
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        if api_key:
            return api_key
    except Exception:
        pass

    raise ValueError(
        "GEMINI_API_KEY is not configured. "
        "Add it to .env locally or Streamlit Cloud Secrets."
    )


GEMINI_API_KEY = get_gemini_api_key()


# ---------------------------------------------------------
# CHROMA CONFIGURATION
# ---------------------------------------------------------

VECTOR_STORE_DIR = "chroma_db"
SUPPLY_CHAIN_COLLECTION_ID = "supply_chain_documents_db"


# ---------------------------------------------------------
# EMBEDDINGS
# ---------------------------------------------------------

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY,
)


# ---------------------------------------------------------
# VECTOR DATABASE
# ---------------------------------------------------------

chroma_instance = Chroma(
    collection_name=SUPPLY_CHAIN_COLLECTION_ID,
    embedding_function=embedding_model,
    persist_directory=VECTOR_STORE_DIR,
)


# ---------------------------------------------------------
# RETRIEVER
# ---------------------------------------------------------

doc_retriever = chroma_instance.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)


# ---------------------------------------------------------
# GEMINI LLM
# ---------------------------------------------------------

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)


# ---------------------------------------------------------
# ASK QUESTION
# ---------------------------------------------------------

def ask_question(question):
    """
    Retrieve relevant documents and generate an answer
    using Gemini.
    """

    documents = doc_retriever.invoke(question)

    if not documents:
        return (
            "I could not find relevant information in the "
            "Meridian Supply Chain documents.",
            [],
        )

    # Build context
    context_parts = []

    for doc in documents:
        source = doc.metadata.get(
            "source_file",
            "Unknown document"
        )

        page = doc.metadata.get(
            "page",
            "Unknown page"
        )

        context_parts.append(
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{doc.page_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Prompt
    prompt = f"""
You are a Supply Chain document assistant.

Answer the user's question ONLY using the provided
Meridian Supply Chain documents.

Do not invent information.

If the answer is not available in the documents,
say:

"I could not find this information in the provided
Meridian Supply Chain documents."

Be concise and professional.

Always mention the relevant supplier, number, policy,
date, or other specific value when available.

USER QUESTION:
{question}

DOCUMENT CONTEXT:
{context}
"""

    # Generate answer
    response = gemini_llm.invoke(prompt)

    answer = response.content

    # Normalize response
    if isinstance(answer, list):
        text_parts = []

        for item in answer:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            else:
                text_parts.append(str(item))

        answer = "\n".join(text_parts)

    # Sources
    sources = []

    seen = set()

    for doc in documents:
        source_file = doc.metadata.get(
            "source_file",
            "Unknown document"
        )

        page = doc.metadata.get(
            "page",
            "Unknown page"
        )

        key = (source_file, page)

        if key not in seen:
            seen.add(key)

            sources.append(
                {
                    "file": source_file,
                    "page": page,
                }
            )

    return answer, sources