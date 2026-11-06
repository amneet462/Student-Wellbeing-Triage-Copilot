"""
app/services/rag/vector_store.py
────────────────────────────────
Dual-store Vector Database Manager using ChromaDB.

Architecture:
- Isolates campus policies ('policies_store') from clinical wellness ('wellness_store').
- Persistent disk storage in `data/chroma_db/`.
- Preserves document titles, section tags, and categories for verbatim citations.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "chroma_db"

POLICIES_COLLECTION = "policies_store"
WELLNESS_COLLECTION = "wellness_store"


class DualVectorStore:
    """
    Manages two strictly isolated ChromaDB collections:
    1. policies_store: Campus regulations, extensions, fee aid, accommodations.
    2. wellness_store: CBT grounding exercises, breathing guides, sleep hygiene.
    """

    def __init__(self, persist_dir: Optional[Path | str] = None) -> None:
        self.persist_dir = Path(persist_dir) if persist_dir else DEFAULT_DB_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize the two isolated collections
        self.policies_collection = self.client.get_or_create_collection(
            name=POLICIES_COLLECTION,
            metadata={"hnsw:space": "cosine", "description": "University Policy & Academic Regulations"}
        )
        self.wellness_collection = self.client.get_or_create_collection(
            name=WELLNESS_COLLECTION,
            metadata={"hnsw:space": "cosine", "description": "CBT & Psychoeducation Wellness Guides"}
        )
        logger.info(
            "DualVectorStore initialized at '%s' | Policies: %d chunks | Wellness: %d chunks",
            self.persist_dir,
            self.policies_collection.count(),
            self.wellness_collection.count()
        )

    def add_chunks(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> int:
        """
        Adds or updates document chunks in the specified collection.
        """
        if collection_name == POLICIES_COLLECTION:
            col = self.policies_collection
        elif collection_name == WELLNESS_COLLECTION:
            col = self.wellness_collection
        else:
            raise ValueError(f"Unknown collection '{collection_name}'. Expected '{POLICIES_COLLECTION}' or '{WELLNESS_COLLECTION}'.")

        if not documents:
            return 0

        col.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info("Upserted %d chunks into '%s'. Total count: %d", len(documents), collection_name, col.count())
        return len(documents)

    def query_policies(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Query only the campus policies knowledge base."""
        return self._query_collection(self.policies_collection, query, n_results)

    def query_wellness(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Query only the CBT and wellness knowledge base."""
        return self._query_collection(self.wellness_collection, query, n_results)

    def _query_collection(
        self,
        collection: Any,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Generic similarity retrieval with distance-to-confidence scoring."""
        count = collection.count()
        if count == 0:
            return []

        actual_n = min(n_results, count)
        results = collection.query(
            query_texts=[query],
            n_results=actual_n,
            include=["documents", "metadatas", "distances"]
        )

        formatted: List[Dict[str, Any]] = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        for i, text in enumerate(docs):
            dist = dists[i] if i < len(dists) else 1.0
            # For cosine distance, similarity = 1 - distance
            similarity = max(0.0, min(1.0, 1.0 - dist))
            meta = metas[i] if i < len(metas) else {}
            formatted.append({
                "content": text,
                "metadata": meta,
                "distance": dist,
                "similarity_score": round(similarity, 4),
                "citation": f"[Source: {meta.get('doc_title', 'Policy Handbook')} {meta.get('section', '')}]".strip()
            })

        return formatted

    def get_stats(self) -> Dict[str, Any]:
        """Returns storage count statistics for monitoring."""
        return {
            "policies_chunk_count": self.policies_collection.count(),
            "wellness_chunk_count": self.wellness_collection.count(),
            "storage_path": str(self.persist_dir)
        }

    def clear(self) -> None:
        """Empties both collections (primarily used in testing)."""
        self.client.delete_collection(POLICIES_COLLECTION)
        self.client.delete_collection(WELLNESS_COLLECTION)
        self.policies_collection = self.client.get_or_create_collection(POLICIES_COLLECTION)
        self.wellness_collection = self.client.get_or_create_collection(WELLNESS_COLLECTION)

