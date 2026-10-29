
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from embeddings import get_embeddings


def search(
    question,
    chunks,
    embeddings,
    client,
    embedding_model,
    top_k=8
):
    """Question ke sabse relevant PDF chunks return karta hai."""

    if not chunks or embeddings.size == 0:
        return []

    question_embedding = get_embeddings(
        client,
        [question],
        embedding_model
    )

    scores = cosine_similarity(
        question_embedding,
        embeddings
    )[0]

    count = min(top_k, len(chunks))

    indices = np.argsort(scores)[::-1][:count]

    return [
        chunks[int(index)]
        for index in indices
    ]
