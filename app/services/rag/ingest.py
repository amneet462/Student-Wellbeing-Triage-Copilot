"""
app/services/rag/ingest.py
──────────────────────────
Document ingestion and chunking pipeline for Dual-Store RAG.

Scans:
  • `data/policies/*.md`  -> `policies_store`
  • `data/wellness/*.md`  -> `wellness_store`

Chunking & Metadata Strategy:
  - Preserves Markdown section headings (e.g. '§4.2 Application Procedure').
  - Chunks text into ~500 character blocks with 50 character overlap.
  - Attaches: `doc_title`, `section`, `source_file`, `category`.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.services.rag.vector_store import (
    DualVectorStore,
    POLICIES_COLLECTION,
    WELLNESS_COLLECTION,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
POLICIES_DIR = DATA_DIR / "policies"
WELLNESS_DIR = DATA_DIR / "wellness"


def split_text_into_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Recursively splits a text block into manageable chunks with overlap."""
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Attempt to split at paragraph or sentence boundary
        split_point = text.rfind("\n", start, end)
        if split_point == -1 or split_point <= start:
            split_point = text.rfind(". ", start, end)
        if split_point == -1 or split_point <= start:
            split_point = end

        chunk = text[start:split_point].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1, split_point - chunk_overlap)

    return chunks


def parse_markdown_document(file_path: Path, category: str) -> List[Dict[str, Any]]:
    """
    Parses a markdown document, extracting document title and section headers.
    Returns list of chunk objects with full metadata.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Document Title from first H1
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else file_path.stem.replace("_", " ").title()

    # Split by section headers (### §... or ## ...)
    section_pattern = re.compile(r"(?=###?\s+§?[0-9A-Za-z])")
    raw_sections = section_pattern.split(content)

    chunks_data: List[Dict[str, Any]] = []

    for s_idx, raw_sec in enumerate(raw_sections):
        raw_sec = raw_sec.strip()
        if not raw_sec:
            continue

        # Extract section heading if present
        header_match = re.match(r"^###?\s+(.+)$", raw_sec, re.MULTILINE)
        section_name = header_match.group(1).strip() if header_match else f"Section {s_idx + 1}"

        # Clean markdown formatting from text for embedding
        cleaned_body = re.sub(r"^###?\s+.+$", "", raw_sec, flags=re.MULTILINE).strip()
        if not cleaned_body:
            continue

        # Split long sections into chunks
        text_chunks = split_text_into_chunks(cleaned_body, chunk_size=500, chunk_overlap=50)

        for c_idx, text_chunk in enumerate(text_chunks):
            chunk_id = f"{file_path.stem}_{s_idx}_{c_idx}"
            chunks_data.append({
                "id": chunk_id,
                "content": f"{doc_title} — {section_name}\n\n{text_chunk}",
                "metadata": {
                    "source_file": file_path.name,
                    "doc_title": doc_title,
                    "section": section_name,
                    "category": category,
                    "chunk_index": c_idx,
                }
            })

    return chunks_data


def ingest_all_documents(
    store: DualVectorStore | None = None,
    policies_dir: Path | None = None,
    wellness_dir: Path | None = None
) -> Tuple[int, int]:
    """
    Ingests all policies and wellness documents into the dual vector store.
    Returns (policies_count, wellness_count).
    """
    vector_store = store or DualVectorStore()
    p_dir = policies_dir or POLICIES_DIR
    w_dir = wellness_dir or WELLNESS_DIR

    total_policies = 0
    total_wellness = 0

    # 1. Ingest Policies
    if p_dir.exists():
        policy_files = list(p_dir.glob("*.md"))
        logger.info("Found %d policy files in '%s'.", len(policy_files), p_dir)
        for p_file in policy_files:
            chunks = parse_markdown_document(p_file, category="CAMPUS_POLICY")
            if chunks:
                docs = [c["content"] for c in chunks]
                metas = [c["metadata"] for c in chunks]
                ids = [c["id"] for c in chunks]
                vector_store.add_chunks(POLICIES_COLLECTION, docs, metas, ids)
                total_policies += len(chunks)
    else:
        logger.warning("Policies directory not found at '%s'.", p_dir)

    # 2. Ingest Wellness
    if w_dir.exists():
        wellness_files = list(w_dir.glob("*.md"))
        logger.info("Found %d wellness files in '%s'.", len(wellness_files), w_dir)
        for w_file in wellness_files:
            chunks = parse_markdown_document(w_file, category="WELLNESS_CBT")
            if chunks:
                docs = [c["content"] for c in chunks]
                metas = [c["metadata"] for c in chunks]
                ids = [c["id"] for c in chunks]
                vector_store.add_chunks(WELLNESS_COLLECTION, docs, metas, ids)
                total_wellness += len(chunks)
    else:
        logger.warning("Wellness directory not found at '%s'.", w_dir)

    logger.info("Ingestion complete. Total Policies Chunks: %d | Total Wellness Chunks: %d", total_policies, total_wellness)
    return total_policies, total_wellness


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Ingesting all knowledge base documents into ChromaDB...")
    p_count, w_count = ingest_all_documents()
    print(f"Successfully ingested {p_count} policy chunks and {w_count} wellness chunks!")

