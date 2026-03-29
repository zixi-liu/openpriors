"""
Embedding & Chunking System

Chunks materials into ~400 token segments, embeds with OpenAI,
stores in SQLite, supports hybrid search (BM25 + vector).
Same pattern as OpenClaw's memory system.
"""

import hashlib
import json
import math
import os
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from core.config import get_db_path


# ============================================================
# Chunking
# ============================================================

CHUNK_TOKENS = 400
CHUNK_OVERLAP = 80
CHARS_PER_TOKEN = 4  # rough estimate


@dataclass
class Chunk:
    text: str
    start_line: int
    end_line: int
    hash: str


def chunk_text(content: str, chunk_tokens: int = CHUNK_TOKENS, overlap_tokens: int = CHUNK_OVERLAP) -> List[Chunk]:
    """Split content into overlapping chunks at line boundaries."""
    max_chars = max(32, chunk_tokens * CHARS_PER_TOKEN)
    overlap_chars = overlap_tokens * CHARS_PER_TOKEN

    lines = content.split("\n")
    chunks: List[Chunk] = []
    current_lines: List[str] = []
    current_chars = 0
    start_line = 1

    for i, line in enumerate(lines, 1):
        current_lines.append(line)
        current_chars += len(line) + 1  # +1 for newline

        if current_chars >= max_chars:
            text = "\n".join(current_lines)
            chunks.append(Chunk(
                text=text,
                start_line=start_line,
                end_line=i,
                hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            ))

            # Carry overlap lines forward
            overlap_text = ""
            overlap_lines: List[str] = []
            for ln in reversed(current_lines):
                if len(overlap_text) + len(ln) > overlap_chars:
                    break
                overlap_lines.insert(0, ln)
                overlap_text = "\n".join(overlap_lines)

            current_lines = overlap_lines
            current_chars = len(overlap_text)
            start_line = i - len(overlap_lines) + 1

    # Last chunk
    if current_lines:
        text = "\n".join(current_lines)
        if text.strip():
            chunks.append(Chunk(
                text=text,
                start_line=start_line,
                end_line=len(lines),
                hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            ))

    return chunks


# ============================================================
# Embedding
# ============================================================

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts using OpenAI."""
    from openai import AsyncOpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        from core.config import get_api_key
        api_key = get_api_key("openai")

    client = AsyncOpenAI(api_key=api_key)
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def embed_text(text: str) -> List[float]:
    """Embed a single text."""
    result = await embed_texts([text])
    return result[0]


# ============================================================
# Storage
# ============================================================

def _get_db() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            material_id TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            hash TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (material_id) REFERENCES materials(id)
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
        USING fts5(text, id UNINDEXED, material_id UNINDEXED)
    """)
    conn.commit()
    return conn


async def index_material(material_id: str, content: str):
    """Chunk and embed a material, store in SQLite."""
    from datetime import datetime

    chunks = chunk_text(content)
    if not chunks:
        return

    # Embed all chunks in one batch
    texts = [c.text for c in chunks]
    embeddings = await embed_texts(texts)

    conn = _get_db()
    now = datetime.now().isoformat()

    # Clear old chunks for this material
    conn.execute("DELETE FROM chunks WHERE material_id = ?", (material_id,))
    conn.execute("DELETE FROM chunks_fts WHERE material_id = ?", (material_id,))

    for chunk, embedding in zip(chunks, embeddings):
        chunk_id = f"{material_id}:{chunk.start_line}:{chunk.end_line}:{chunk.hash}"
        conn.execute(
            """INSERT OR REPLACE INTO chunks (id, material_id, start_line, end_line, hash, text, embedding, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (chunk_id, material_id, chunk.start_line, chunk.end_line,
             chunk.hash, chunk.text, json.dumps(embedding), now),
        )
        conn.execute(
            "INSERT INTO chunks_fts (text, id, material_id) VALUES (?, ?, ?)",
            (chunk.text, chunk_id, material_id),
        )

    conn.commit()
    conn.close()


async def index_prior(prior_id: str, material_id: str, principle: str, practice: str, source: str):
    """Embed a prior's key fields for search."""
    from datetime import datetime

    text = f"{principle}\n{practice}\n{source}"
    embedding = await embed_text(text)

    conn = _get_db()
    now = datetime.now().isoformat()
    chunk_id = f"prior:{prior_id}"

    conn.execute(
        """INSERT OR REPLACE INTO chunks (id, material_id, start_line, end_line, hash, text, embedding, created_at)
           VALUES (?, ?, 0, 0, ?, ?, ?, ?)""",
        (chunk_id, material_id, hashlib.sha256(text.encode()).hexdigest()[:16],
         text, json.dumps(embedding), now),
    )
    conn.execute(
        "INSERT OR REPLACE INTO chunks_fts (text, id, material_id) VALUES (?, ?, ?)",
        (text, chunk_id, material_id),
    )
    conn.commit()
    conn.close()


# ============================================================
# Hybrid Search
# ============================================================

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _bm25_rank_to_score(rank: float) -> float:
    """Convert FTS5 bm25 rank to 0-1 score. Same as OpenClaw."""
    if rank < 0:
        return -rank / (1 + -rank)
    return 1 / (1 + rank)


@dataclass
class SearchResult:
    chunk_id: str
    material_id: str
    text: str
    score: float
    source: str  # "vector", "keyword", "hybrid"


async def hybrid_search(
    query: str,
    max_results: int = 6,
    vector_weight: float = 0.7,
    text_weight: float = 0.3,
    min_score: float = 0.35,
) -> List[SearchResult]:
    """Search chunks using hybrid BM25 + vector similarity."""

    # Vector search
    query_embedding = await embed_text(query)
    conn = _get_db()

    all_chunks = conn.execute("SELECT id, material_id, text, embedding FROM chunks").fetchall()

    vector_results: Dict[str, SearchResult] = {}
    for row in all_chunks:
        chunk_embedding = json.loads(row["embedding"])
        score = _cosine_similarity(query_embedding, chunk_embedding)
        if score > 0.1:  # rough filter
            vector_results[row["id"]] = SearchResult(
                chunk_id=row["id"],
                material_id=row["material_id"],
                text=row["text"],
                score=score,
                source="vector",
            )

    # BM25 keyword search
    keyword_results: Dict[str, SearchResult] = {}
    try:
        # Tokenize and quote for FTS5
        tokens = query.strip().split()
        fts_query = " AND ".join(f'"{t}"' for t in tokens if t)
        if fts_query:
            rows = conn.execute(
                """SELECT chunks_fts.id, chunks_fts.material_id, chunks_fts.text, bm25(chunks_fts) as rank
                   FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?""",
                (fts_query, max_results * 4),
            ).fetchall()
            for row in rows:
                score = _bm25_rank_to_score(row["rank"])
                keyword_results[row["id"]] = SearchResult(
                    chunk_id=row["id"],
                    material_id=row["material_id"],
                    text=row["text"],
                    score=score,
                    source="keyword",
                )
    except Exception:
        pass  # FTS query might fail on certain inputs

    conn.close()

    # Merge: hybrid score = vector_weight * vector + text_weight * keyword
    merged: Dict[str, float] = {}
    all_ids = set(vector_results.keys()) | set(keyword_results.keys())

    for chunk_id in all_ids:
        v_score = vector_results[chunk_id].score if chunk_id in vector_results else 0.0
        k_score = keyword_results[chunk_id].score if chunk_id in keyword_results else 0.0
        merged[chunk_id] = (vector_weight * v_score) + (text_weight * k_score)

    # Sort by score, filter, limit
    sorted_ids = sorted(merged.keys(), key=lambda x: merged[x], reverse=True)

    results: List[SearchResult] = []
    for chunk_id in sorted_ids:
        if merged[chunk_id] < min_score:
            continue
        if len(results) >= max_results:
            break

        # Get the full result from whichever dict has it
        base = vector_results.get(chunk_id) or keyword_results[chunk_id]
        results.append(SearchResult(
            chunk_id=base.chunk_id,
            material_id=base.material_id,
            text=base.text,
            score=merged[chunk_id],
            source="hybrid",
        ))

    return results
