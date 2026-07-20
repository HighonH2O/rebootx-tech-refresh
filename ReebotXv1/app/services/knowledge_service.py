"""ChromaDB-backed vector store for compatibility knowledge retrieval.

This is the RAG layer — it embeds knowledge documents, stores them in
ChromaDB, and retrieves the most relevant ones for a given upgrade query.

Uses ChromaDB's built-in default embedding function (all-MiniLM-L6-v2)
so the system works without Ollama for embeddings.
"""

import logging
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

logger = logging.getLogger(__name__)

KNOWLEDGE_COLLECTION = "compatibility_knowledge"


class KnowledgeService:
    """Manages the ChromaDB vector store for knowledge retrieval."""

    def __init__(self) -> None:
        Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=KNOWLEDGE_COLLECTION,
            embedding_function=self.embedding_fn,
            metadata={"description": "RebootX compatibility and upgrade knowledge"},
        )

    @property
    def document_count(self) -> int:
        """Total number of documents in the collection."""
        return self.collection.count()

    def reset_collection(self) -> None:
        """Clear all documents so the collection can be re-synced from disk."""
        try:
            self.client.delete_collection(KNOWLEDGE_COLLECTION)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=KNOWLEDGE_COLLECTION,
            embedding_function=self.embedding_fn,
            metadata={"description": "RebootX compatibility and upgrade knowledge"},
        )
        logger.info("Knowledge collection reset")

    def ingest_documents(self, documents: list[dict]) -> int:
        """Upsert validated knowledge documents into ChromaDB.

        Args:
            documents: List of {id, text, metadata} dicts from the loader.

        Returns:
            Number of documents successfully ingested.
        """
        if not documents:
            return 0

        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]

        # ChromaDB metadata values must be str, int, float, or bool
        metadatas = []
        for doc in documents:
            meta = {}
            for key, value in doc["metadata"].items():
                if isinstance(value, (str, int, float, bool)):
                    meta[key] = value
                elif isinstance(value, list):
                    meta[key] = ",".join(str(v) for v in value)
                else:
                    meta[key] = str(value)
            metadatas.append(meta)

        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
        logger.info("Ingested %d documents into ChromaDB", len(ids))
        return len(ids)

    def retrieve(
        self,
        query: str,
        technology_type: str | None = None,
        n_results: int = 5,
    ) -> list[dict]:
        """Semantic similarity search over the knowledge base.

        Args:
            query: Natural language query string.
            technology_type: Optional filter (e.g., "database", "python").
            n_results: Number of results to return.

        Returns:
            List of {text, metadata, distance} dicts, sorted by relevance.
        """
        if self.collection.count() == 0:
            logger.warning("Knowledge base is empty — no documents to retrieve")
            return []

        where_filter = None
        if technology_type:
            where_filter = {"technology_type": technology_type}

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count()),
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("ChromaDB query failed: %s", exc)
            return []

        docs = []
        if results["documents"] and results["documents"][0]:
            for text, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                docs.append({
                    "text": text,
                    "metadata": meta,
                    "distance": dist,
                })

        return docs
