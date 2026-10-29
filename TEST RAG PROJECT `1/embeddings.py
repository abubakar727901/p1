import numpy as np


def make_chunks(text, size=1800, overlap=250):
    text = (text or "").strip()

    if not text:
        return []

    if size <= overlap:
        raise ValueError("Chunk size must be greater than overlap.")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def get_embeddings(client, texts, model="openai/text-embedding-3-small"):
    if not texts:
        return np.empty((0, 0))

    all_embeddings = []
    batch_size = 32

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        response = client.embeddings.create(
            model=model,
            input=batch
        )

        all_embeddings.extend(
            [item.embedding for item in response.data]
        )

    return np.array(all_embeddings)