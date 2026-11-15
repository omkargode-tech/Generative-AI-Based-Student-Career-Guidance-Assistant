import streamlit as st
import chromadb

from config import CHROMA_PATH, COLLECTION_NAME, TOP_K
from embeddings import get_embedding_function
from knowledge_base import role_to_document


@st.cache_resource
def get_collection():
    """Create or connect to the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=get_embedding_function(),
    )


def index_career_roles(collection, roles):
    """Add the starter career records to ChromaDB the first time it is used."""
    if collection.count() > 0:
        return

    documents = [role_to_document(role) for role in roles]
    ids = [role["id"] for role in roles]
    metadatas = [
        {
            "role_id": role["id"],
            "role": role["role"],
            "industries": ", ".join(role.get("industries", [])),
        }
        for role in roles
    ]

    # Chroma uses the configured Sentence Transformers function to embed documents.
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


def retrieve_roles(collection, profile_text, top_k=TOP_K):
    """Find career records that are semantically relevant to a student profile."""
    total_records = collection.count()
    if total_records == 0:
        return []

    results = collection.query(
        query_texts=[profile_text],
        n_results=min(top_k, total_records),
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return matches
