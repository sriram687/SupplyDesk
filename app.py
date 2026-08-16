import streamlit as st
from pathlib import Path

from ingest import process_and_embed_documents
from rag import ask_question

st.set_page_config(
    page_title="Meridian Supply Chain RAG",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Meridian Supply Chain RAG Assistant")
st.caption("Ask questions using the Meridian Supply Chain Review and Procurement Policy.")

st.sidebar.header("Document Management")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
)

if st.sidebar.button("Index Documents", type="primary"):
    if not uploaded_files:
        st.sidebar.warning("Upload at least one PDF first.")
    else:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        for uploaded_file in uploaded_files:
            file_path = data_dir / uploaded_file.name
            if not file_path.exists():
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

        with st.spinner("Extracting, chunking, embedding, and indexing..."):
            file_count, chunk_count = process_and_embed_documents()

        st.sidebar.success(
            f"Indexed {file_count} PDF(s) and {chunk_count} chunks."
        )

st.divider()

st.subheader("Ask a question")

question = st.text_area(
    "Question",
    placeholder="Example: Which supplier had the highest spend in Q1?",
    height=100,
)

top_k = st.slider("Retrieved chunks", min_value=3, max_value=10, value=6)

if st.button("Ask", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching the knowledge base..."):
            try:
                answer, sources = ask_question(question, top_k=top_k)

                st.subheader("Answer")
                st.write(answer)

                st.subheader("Sources")
                if sources:
                    for source in sources:
                        page = source.get("page")
                        page_text = (
                            f"Page {int(page) + 1}"
                            if isinstance(page, int)
                            else f"Page {page}"
                        )
                        st.write(f"📄 **{source['file']}** — {page_text}")
                else:
                    st.info("No source metadata was returned.")

            except Exception as exc:
                st.error(f"Error: {exc}")
                st.info("Make sure the API key is configured and documents have been indexed.")
