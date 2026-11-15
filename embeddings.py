import streamlit as st
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from config import EMBEDDING_MODEL


@st.cache_resource(show_spinner="Loading the local embedding model...")
def get_embedding_function():
    """Create a cached Chroma embedding function backed by Sentence Transformers."""
    return SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
        device="cpu",
        normalize_embeddings=True,
    )
