"""
Very lightweight retrieval (RAG-like) for course/assignment info without requiring
external embeddings or paid APIs.

Approach:
- Given question text, retrieve relevant "course notes" snippets from a small corpus.
- Portfolio-friendly because it demonstrates the pattern.
"""

from __future__ import annotations
from dataclasses import dataclass
import re
from typing import List, Tuple


def tokenize(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return set([t for t in text.split() if len(t) > 2])


@dataclass(frozen=True)
class MiniRetriever:
    docs: List[Tuple[str, str]]  # (doc_id, doc_text)

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[str, str]]:
        q = tokenize(query)
        scored = []
        for doc_id, doc in self.docs:
            d = tokenize(doc)
            score = len(q.intersection(d))
            scored.append((score, doc_id, doc))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [(doc_id, doc) for score, doc_id, doc in scored[:k] if score > 0]
