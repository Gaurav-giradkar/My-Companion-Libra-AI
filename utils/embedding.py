from __future__ import annotations

import hashlib
import math
import re

VECTOR_SIZE = 64
TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall((text or "").lower())


def _bucket_for(token: str) -> int:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") % VECTOR_SIZE


def get_embedding(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE

    for token in tokenize(text):
        vector[_bucket_for(token)] += 1.0

    return vector


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
