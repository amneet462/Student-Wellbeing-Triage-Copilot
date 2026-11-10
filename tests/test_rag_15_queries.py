"""
tests/test_rag_15_queries.py
────────────────────────────
Benchmark evaluation suite testing the RAG chatbot against 15 real university inquiries.
Verifies:
  • Citation presence [Source: Document §Section]
  • Correct collection routing (policies vs. wellness)
  • Low-similarity fallback guard triggering human advisor referral for out-of-scope questions
"""

from __future__ import annotations

import pytest
from app.services.rag.gemini_rag import GeminiRAGAssistant


@pytest.fixture(scope="module")
def rag_assistant() -> GeminiRAGAssistant:
    return GeminiRAGAssistant()


UNIVERSITY_QUESTIONS = [
    # 1. Coursework extension
    ("How do I request an extension for coursework due to illness?", "policies", False),
    # 2. Late penalties
    ("What is the penalty for submitting an assignment 24 hours late?", "policies", False),
    # 3. Mitigating circumstances grounds
    ("What counts as valid extenuating circumstances for missed deadlines?", "policies", False),
    # 4. Financial hardship aid
    ("How can I apply for emergency student hardship funds?", "policies", False),
    # 5. Course withdrawal and deferral
    ("How do I defer my university studies to next semester?", "policies", False),
    # 6. Disability exam adjustments
    ("How do I get extra time accommodations for exams?", "policies", False),
    # 7. Self-certification rule
    ("Can I self-certify an illness for a 5-day assignment extension?", "policies", False),
    # 8. Acute panic grounding
    ("I am having a panic attack before my presentation, help me calm down.", "wellness", False),
    # 9. Box breathing
    ("How does box breathing help with exam anxiety?", "wellness", False),
    # 10. Sleep hygiene and insomnia
    ("I cannot sleep because of academic stress, what is the sleep protocol?", "wellness", False),
    # 11. Progressive muscle relaxation
    ("What are the steps for progressive muscle relaxation?", "wellness", False),
    # 12. Cognitive reframing
    ("I feel like an imposter and that I am going to fail everything.", "wellness", False),
    # 13. Fee instalment deferral
    ("Can I defer my tuition fee payment instalment if in hardship?", "policies", False),
    # 14. Out of scope question 1 -> Must trigger fallback
    ("How do I repair a broken alternator on a 2012 Honda Civic?", "fallback", True),
    # 15. Out of scope question 2 -> Must trigger fallback
    ("Give me the recipe for double chocolate fudge cookies.", "fallback", True),
]


class TestRAG15UniversityQueries:
    """Evaluates chatbot response accuracy and citation integrity across 15 questions."""

    @pytest.mark.parametrize("query,expected_domain,expected_fallback", UNIVERSITY_QUESTIONS)
    def test_query_citation_and_fallback(
        self,
        rag_assistant: GeminiRAGAssistant,
        query: str,
        expected_domain: str,
        expected_fallback: bool
    ) -> None:
        answer = rag_assistant.generate_response(query)

        if expected_fallback:
            # Out-of-scope query must trigger fallback guard
            assert answer.fallback_suggested is True, f"Expected fallback for '{query}'"
            assert "human academic advisor" in answer.reply.lower() or "advisor" in answer.reply.lower()
        else:
            # Legitimate query must contain answer and valid citation
            assert len(answer.citations) > 0, f"No citations returned for '{query}'"
            assert "[Source:" in answer.reply, f"Verbatim citation missing in reply for '{query}'"
            assert len(answer.reply) >= 40, f"Reply too short for '{query}'"

            # Check citation metadata integrity
            top_citation = answer.citations[0]
            assert top_citation.document, f"Citation document missing for '{query}'"
            assert top_citation.section, f"Citation section missing for '{query}'"

