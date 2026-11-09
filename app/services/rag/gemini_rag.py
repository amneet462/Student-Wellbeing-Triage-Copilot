"""
app/services/rag/gemini_rag.py
──────────────────────────────
Citation-Backed Dual-Store RAG Chatbot with Google Gemini (Free Tier).

Features:
  • Routes student queries intelligently between policies_store and wellness_store.
  • Uses Google Gemini free-tier (gemini-1.5-flash / gemini-2.0-flash) with 0 credit card required.
  • Strict token conservation: retrieves top 2-3 chunks, limits max output tokens (350).
  • Prompt engineered to ALWAYS enforce verbatim citations: [Source: <Document> §<Section>].
  • Zero-cost local deterministic fallback if API key is not configured or offline.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.rag.vector_store import (
    DualVectorStore,
    POLICIES_COLLECTION,
    WELLNESS_COLLECTION,
)

logger = logging.getLogger(__name__)

# Prompt forcing exact document names and section numbers
SYSTEM_PROMPT = (
    "You are an empathetic, highly dependable Student Wellbeing & Academic Regulations Copilot.\n"
    "Your duty is to support university students with accurate, policy-compliant guidance.\n\n"
    "STRICT RULES:\n"
    "1. You MUST ALWAYS cite the exact document names and section numbers in your answer.\n"
    "   Use the format: [Source: Document Title §Section Number]\n"
    "2. Base your response strictly on the provided verified context below. Do not fabricate rules.\n"
    "3. Keep your response concise, clear, and actionable (under 200 words) to respect the student's cognitive load.\n"
    "4. If the question cannot be answered from the provided documents, politely state that and advise "
    "   the student to consult their departmental academic advisor or university student services."
)


@dataclass
class RAGCitation:
    document: str
    section: str
    page: Optional[int] = None
    excerpt: Optional[str] = None


@dataclass
class RAGAnswer:
    reply: str
    citations: List[RAGCitation] = field(default_factory=list)
    fallback_suggested: bool = False
    model_used: str = "local-retriever"
    tokens_estimated: int = 0


class GeminiRAGAssistant:
    """
    Dual-Store RAG Assistant powered by Google Gemini and ChromaDB.
    """

    def __init__(
        self,
        vector_store: Optional[DualVectorStore] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self.vector_store = vector_store or DualVectorStore()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._genai_client = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._genai_client = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=SYSTEM_PROMPT,
                )
                logger.info("Gemini RAG Assistant initialized with model '%s'.", self.model_name)
            except Exception as exc:
                logger.warning("Failed to configure Google Gemini API: %s. Using local synthesis fallback.", exc)
                self._genai_client = None
        else:
            logger.info("No GEMINI_API_KEY provided. Operating in deterministic local retrieval mode (0 tokens).")

    def _route_query(self, query: str, category: Optional[str] = None) -> str:
        """Determines whether query belongs to policies or wellness collection."""
        cat = (category or "").upper()
        if cat in ("EMOTIONAL_DISTRESS", "WELLNESS_CBT", "WELLNESS"):
            return WELLNESS_COLLECTION
        if cat in ("ACADEMIC_STRESS", "ADMINISTRATIVE_ISSUES", "FINANCIAL_PROBLEMS", "CAMPUS_POLICY"):
            return POLICIES_COLLECTION

        q = query.lower()
        wellness_keywords = ["panic", "breath", "anxious", "anxiety", "grounding", "sleep", "insomnia", "relax", "cbt", "calm", "heart"]
        if any(kw in q for kw in wellness_keywords):
            return WELLNESS_COLLECTION

        return POLICIES_COLLECTION

    def _retrieve_context(self, query: str, target_collection: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """Retrieve most relevant chunks from the selected store."""
        if target_collection == WELLNESS_COLLECTION:
            return self.vector_store.query_wellness(query, n_results=n_results)
        return self.vector_store.query_policies(query, n_results=n_results)

    def generate_response(self, query: str, category: Optional[str] = None) -> RAGAnswer:
        """
        Executes citation-backed RAG pipeline:
          1. Selects collection based on query intent.
          2. Retrieves top 2-3 chunks from ChromaDB.
          3. Synthesizes response with Google Gemini (or local synthesizer) citing exact sources.
        """
        target_store = self._route_query(query, category)
        chunks = self._retrieve_context(query, target_store, n_results=2)

        # If primary store gave poor results, check other store as fallback
        if not chunks or (chunks and chunks[0]["similarity_score"] < 0.25):
            alternate_store = WELLNESS_COLLECTION if target_store == POLICIES_COLLECTION else POLICIES_COLLECTION
            alt_chunks = self._retrieve_context(query, alternate_store, n_results=2)
            if alt_chunks and (not chunks or alt_chunks[0]["similarity_score"] > chunks[0]["similarity_score"]):
                chunks = alt_chunks
                target_store = alternate_store

        # Build citation objects
        citations: List[RAGCitation] = []
        for c in chunks:
            meta = c.get("metadata", {})
            citations.append(
                RAGCitation(
                    document=meta.get("doc_title", "University Regulations"),
                    section=meta.get("section", "General Guidance"),
                    page=meta.get("chunk_index", 1),
                    excerpt=c.get("content", "")[:140] + "...",
                )
            )

        # Check if similarity is too low
        if not chunks or chunks[0]["similarity_score"] < 0.20:
            return RAGAnswer(
                reply=(
                    "I searched our university regulations and wellbeing guides, but could not find a specific "
                    "policy directly matching your question. To ensure you receive accurate and up-to-date guidance, "
                    "please contact your departmental academic advisor or visit the Student Services Hub."
                ),
                citations=citations,
                fallback_suggested=True,
                model_used="low-similarity-fallback",
                tokens_estimated=40,
            )

        # ── Branch A: Google Gemini Free Tier ─────────────────────────────────
        if self._genai_client is not None:
            try:
                context_blocks = "\n\n---\n\n".join(
                    f"Document: {c['metadata'].get('doc_title')}\nSection: {c['metadata'].get('section')}\nContent: {c['content']}"
                    for c in chunks
                )
                user_content = (
                    f"VERIFIED KNOWLEDGE BASE CHUNKS:\n{context_blocks}\n\n"
                    f"STUDENT QUESTION:\n{query}\n\n"
                    f"Provide an answer citing the exact document title and section number."
                )

                # Minimize token consumption: 350 max tokens, temperature 0.2
                response = self._genai_client.generate_content(
                    user_content,
                    generation_config={
                        "max_output_tokens": 350,
                        "temperature": 0.2,
                    },
                )
                reply_text = response.text.strip() if response and response.text else ""
                if reply_text:
                    return RAGAnswer(
                        reply=reply_text,
                        citations=citations,
                        fallback_suggested=False,
                        model_used=self.model_name,
                        tokens_estimated=len(user_content.split()) + len(reply_text.split()),
                    )
            except Exception as exc:
                logger.warning("Gemini API call failed (%s). Falling back to local synthesis.", exc)

        # ── Branch B: Deterministic Local Synthesis (0 tokens, 100% free) ─────
        top_chunk = chunks[0]
        doc_title = top_chunk["metadata"].get("doc_title", "University Policy Handbook")
        section = top_chunk["metadata"].get("section", "Section 1.0")
        snippet = top_chunk["content"].split("\n\n")[-1].strip()

        # Build clean, citation-backed answer
        if target_store == WELLNESS_COLLECTION:
            reply = (
                f"According to the **{doc_title}** ({section}), here is the recommended technique:\n\n"
                f"{snippet}\n\n"
                f"Take slow, gentle breaths while following these steps to help your nervous system regulate."
            )
        else:
            reply = (
                f"According to official university academic regulations under **{doc_title}** ({section}):\n\n"
                f"{snippet}\n\n"
                f"You can review the full guidance or submit supporting requests directly via your student portal."
            )

        # Ensure citation string is appended if not present
        citation_tag = f"[Source: {doc_title} {section}]"
        if citation_tag not in reply:
            reply += f"\n\n{citation_tag}"

        return RAGAnswer(
            reply=reply,
            citations=citations,
            fallback_suggested=False,
            model_used="local-chroma-retriever",
            tokens_estimated=0,
        )
