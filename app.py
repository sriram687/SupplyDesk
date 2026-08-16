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

st.subheader("Chat with your Data")

top_k = st.slider("Retrieved chunks", min_value=3, max_value=10, value=6)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("Sources"):
                for source in msg["sources"]:
                    page = source.get("page")
                    page_text = f"Page {int(page) + 1}" if isinstance(page, int) else f"Page {page}"
                    st.write(f"📄 **{source['file']}** — {page_text}")

# Chat input
if question := st.chat_input("Example: Which supplier had the highest spend in Q1?"):
    # Render user message immediately
    with st.chat_message("user"):
        st.write(question)
    
    # Store user message
    st.session_state.messages.append({"role": "user", "content": question})

    # Prepare chat history
    history_parts = []
    for m in st.session_state.messages[:-1]: # exclude the latest
        history_parts.append(f"{m['role'].capitalize()}: {m['content']}")
    chat_history_str = "\n".join(history_parts)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            try:
                answer, sources = ask_question(question, top_k=top_k, chat_history=chat_history_str)
                st.write(answer)
                
                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            page = source.get("page")
                            page_text = f"Page {int(page) + 1}" if isinstance(page, int) else f"Page {page}"
                            st.write(f"📄 **{source['file']}** — {page_text}")
                else:
                    st.info("No source metadata was returned.")
                
                # Store assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "sources": sources
                })
            except Exception as exc:
                st.error(f"Error: {exc}")
                st.info("Make sure the API key is configured and documents have been indexed.")
