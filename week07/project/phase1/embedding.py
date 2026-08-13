import numpy as np
import ollama
from config import (
    EMBEDDING_MODEL,
    BREAKPOINT_PERCENTILE,
    BUFFER_SIZE,
    OLLAMA_KEEP_ALIVE,
)

def build_context_windows(sentences: list) -> list:
    windows = []
    n = len(sentences)

    for i in range(n):
        # Create a window that includes the current sentence plus surrounding ones based on BUFFER_SIZE
        start = max(0, i - BUFFER_SIZE)
        end = min(n, i + BUFFER_SIZE + 1)
        windows.append(" ".join(sentences[start:end]))

    return windows

def generate_and_normalize_embeddings(windows: list) -> np.ndarray:
    if not windows:
        return np.array([])

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=windows,
        truncate=False,
        keep_alive=OLLAMA_KEEP_ALIVE,
    )

    if "embeddings" not in response or not response["embeddings"]:
        raise ValueError("Invalid embedding response from Ollama.")

    embeddings = np.array(response["embeddings"], dtype=np.float32)

    if embeddings.ndim != 2 or len(embeddings) != len(windows):
        raise ValueError("Embedding count does not match the number of context windows.")

    # Normalize the embeddings to unit length for accurate cosine similarity calculation
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Prevent division by zero in case of an empty or malformed embedding vector
    norms[norms == 0] = 1e-10

    return embeddings / norms

def detect_breakpoints(embeddings: np.ndarray) -> list:
    if len(embeddings) < 2:
        return []

    # Calculate cosine similarity between each sentence and the immediately following one
    similarities = np.sum(embeddings[:-1] * embeddings[1:], axis=1)
    
    # Clip values to correct minor floating point inaccuracies from numpy
    similarities = np.clip(similarities, -1.0, 1.0)
    
    # Convert similarity to distance (higher distance = weaker semantic connection = good place to split)
    distances = 1.0 - similarities

    # Determine the cutoff threshold dynamically based on the configured percentile
    threshold = np.percentile(distances, BREAKPOINT_PERCENTILE)

    # Return the indices where the distance exceeds our calculated threshold
    return [
        i
        for i, distance in enumerate(distances)
        if distance > threshold
    ]
