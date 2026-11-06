"""
tests/test_vector_store.py
──────────────────────────
Unit and integration tests for Dual-Store Vector Database.
Tests:
  1. Ingestion completeness (all 10 knowledge docs parsed and embedded).
  2. Strict collection isolation (policies != wellness).
  3. Citation metadata integrity (doc_title, section, source_file).
  4. Semantic retrieval relevance (extension policy query -> Extenuating Circumstances).
  5. Somatic wellness retrieval relevance (panic/breathing query -> Box Breathing / Grounding).
"""

from __future__ import annotations

import pytest
from app.services.rag.vector_store import (
    DualVectorStore,
    POLICIES_COLLECTION,
    WELLNESS_COLLECTION,
)


@pytest.fixture(scope="module")
def vector_store() -> DualVectorStore:
    """Fixture providing initialized DualVectorStore instance."""
    return DualVectorStore()


class TestDualVectorStoreIngestion:
    """Tests verifying vector store initialization and chunk counts."""

    def test_collections_exist_and_populated(self, vector_store: DualVectorStore) -> None:
        """Verify that both policies and wellness collections hold ingested chunks."""
        stats = vector_store.get_stats()
        assert stats["policies_chunk_count"] > 30, "Policies store should contain at least 30 chunks."
        assert stats["wellness_chunk_count"] > 25, "Wellness store should contain at least 25 chunks."

    def test_chunk_metadata_integrity(self, vector_store: DualVectorStore) -> None:
        """Verify that stored chunks retain all required citation metadata."""
        sample_res = vector_store.query_policies("coursework extension", n_results=1)
        assert len(sample_res) > 0
        chunk = sample_res[0]
        meta = chunk["metadata"]
        assert "doc_title" in meta
        assert "section" in meta
        assert "source_file" in meta
        assert "category" in meta
        assert meta["category"] == "CAMPUS_POLICY"
        assert chunk["citation"].startswith("[Source:")


class TestCollectionIsolation:
    """Tests verifying strict isolation between university policy and wellness stores."""

    def test_policies_query_never_returns_wellness_chunks(self, vector_store: DualVectorStore) -> None:
        """Querying policies store must never retrieve CBT or wellness content."""
        results = vector_store.query_policies("grounding exercises for panic attack", n_results=5)
        for r in results:
            assert r["metadata"]["category"] == "CAMPUS_POLICY", (
                f"Cross-contamination detected! Found category {r['metadata']['category']} in policies store."
            )

    def test_wellness_query_never_returns_policy_chunks(self, vector_store: DualVectorStore) -> None:
        """Querying wellness store must never retrieve university regulatory policies."""
        results = vector_store.query_wellness("regulations regarding coursework penalty and 48 hour deadline", n_results=5)
        for r in results:
            assert r["metadata"]["category"] == "WELLNESS_CBT", (
                f"Cross-contamination detected! Found category {r['metadata']['category']} in wellness store."
            )


class TestSemanticRetrievalAccuracy:
    """Tests verifying that semantic queries retrieve accurate policy & wellness answers."""

    def test_extension_query_retrieves_extenuating_circumstances(self, vector_store: DualVectorStore) -> None:
        """Querying extension deadlines must retrieve Extenuating Circumstances Policy."""
        results = vector_store.query_policies("How do I apply for an extension on my assignment deadline?", n_results=3)
        assert len(results) > 0
        top_hit = results[0]
        assert "Extenuating Circumstances" in top_hit["metadata"]["doc_title"]
        assert top_hit["similarity_score"] > 0.40

    def test_hardship_query_retrieves_financial_aid(self, vector_store: DualVectorStore) -> None:
        """Querying rent or emergency money must retrieve Student Hardship Fund regulations."""
        results = vector_store.query_policies("I cannot afford my rent this month and have no money for food", n_results=3)
        assert len(results) > 0
        doc_titles = [r["metadata"]["doc_title"] for r in results]
        assert any("Hardship" in t or "Financial" in t for t in doc_titles)

    def test_breathing_query_retrieves_box_breathing(self, vector_store: DualVectorStore) -> None:
        """Querying acute hyperventilation or panic must retrieve breathing protocols."""
        results = vector_store.query_wellness("I am hyperventilating, heart is pounding, and I feel dizzy with panic", n_results=3)
        assert len(results) > 0
        top_hit = results[0]
        assert "Breathing" in top_hit["metadata"]["doc_title"] or "Grounding" in top_hit["metadata"]["doc_title"]
        assert top_hit["similarity_score"] > 0.40

    def test_imposter_query_retrieves_cognitive_reframing(self, vector_store: DualVectorStore) -> None:
        """Querying imposter syndrome or failure thoughts must retrieve CBT reframing guide."""
        results = vector_store.query_wellness("I feel like an imposter who doesn't belong at university and will fail", n_results=3)
        assert len(results) > 0
        doc_titles = [r["metadata"]["doc_title"] for r in results]
        assert any("Cognitive" in t or "Reframing" in t for t in doc_titles)

