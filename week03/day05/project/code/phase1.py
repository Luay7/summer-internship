import os
import json
import hashlib
import re

import numpy as np
import stanza
import ollama

from config import (
    TEXT_ENCODING,
    REGISTRY_PATH,
    CHUNKS_DIR,
    STANZA_LANGUAGE,
    STANZA_USE_GPU,
    EMBEDDING_MODEL,
    BREAKPOINT_PERCENTILE,
    BUFFER_SIZE,
    CHUNKING_VERSION,
    OLLAMA_KEEP_ALIVE,
)


_STANZA_PIPELINE = None


def get_stanza_pipeline():
    global _STANZA_PIPELINE

    if _STANZA_PIPELINE is None:
        try:
            _STANZA_PIPELINE = stanza.Pipeline(
                lang=STANZA_LANGUAGE,
                processors="tokenize",
                use_gpu=STANZA_USE_GPU,
                verbose=False,
                download_method=None,
            )
        except Exception as error:
            raise RuntimeError(
                "Could not load the local Stanza tokenizer. "
                "Make sure the required Stanza model is installed."
            ) from error

    return _STANZA_PIPELINE


def estimate_tokens(text: str) -> int:
    return len(text.split()) + (len(text) // 4) // 2


def calculate_file_hash(filepath: str) -> str:
    h = hashlib.sha256()

    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            h.update(byte_block)

    return h.hexdigest()


def calculate_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode(TEXT_ENCODING)).hexdigest()


def load_registry() -> dict:
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding=TEXT_ENCODING) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    return {}


def save_registry(registry_data: dict):
    with open(REGISTRY_PATH, "w", encoding=TEXT_ENCODING) as f:
        json.dump(registry_data, f, indent=2)


def prepare_paragraph_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not text:
        return ""

    raw_paragraphs = re.split(r"\n[ \t]*\n+", text)
    paragraphs = []

    for paragraph in raw_paragraphs:
        paragraph = re.sub(r"[ \t]*\n[ \t]*", " ", paragraph)
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()

        if paragraph:
            paragraphs.append(paragraph)

    return "\n\n".join(paragraphs)


def extract_sentences(text: str) -> list:
    pipeline = get_stanza_pipeline()
    doc = pipeline(text)
    sentences = []

    for sentence in doc.sentences:
        clean_sentence = re.sub(r"[ \t]+", " ", sentence.text).strip()

        if clean_sentence:
            sentences.append(clean_sentence)

    return sentences


def build_context_windows(sentences: list) -> list:
    windows = []
    n = len(sentences)

    for i in range(n):
        start = max(0, i - BUFFER_SIZE)
        end = min(n, i + BUFFER_SIZE + 1)
        windows.append(" ".join(sentences[start:end]))

    return windows


def generate_and_normalize_embeddings(windows: list) -> np.ndarray:
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=windows,
        truncate=False,
        keep_alive=OLLAMA_KEEP_ALIVE,
    )

    if "embeddings" not in response or not response["embeddings"]:
        raise ValueError("Invalid embedding response.")

    embeddings = np.array(response["embeddings"], dtype=np.float32)

    if embeddings.ndim != 2 or len(embeddings) != len(windows):
        raise ValueError("Embedding count does not match context windows.")

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)

    if np.any(norms == 0):
        raise ValueError("Zero norm detected in embeddings.")

    return embeddings / norms


def detect_breakpoints(embeddings: np.ndarray) -> list:
    if len(embeddings) < 2:
        return []

    similarities = np.sum(
        embeddings[:-1] * embeddings[1:],
        axis=1,
    )
    similarities = np.clip(similarities, -1.0, 1.0)
    distances = 1.0 - similarities

    threshold = np.percentile(
        distances,
        BREAKPOINT_PERCENTILE,
    )

    return [
        i
        for i, distance in enumerate(distances)
        if distance > threshold
    ]


def build_semantic_chunks(
    sentences: list,
    breakpoints: list,
) -> list:
    chunks = []
    current_chunk = []
    start_pos = 0
    chunk_index = 1

    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence)

        if i in breakpoints or i == len(sentences) - 1:
            chunk_text = " ".join(current_chunk)

            chunks.append(
                {
                    "chunk_number": chunk_index,
                    "first_sentence_position": start_pos,
                    "final_sentence_position": i,
                    "sentence_count": len(current_chunk),
                    "character_count": len(chunk_text),
                    "estimated_token_count": estimate_tokens(
                        chunk_text
                    ),
                    "text": chunk_text,
                }
            )

            chunk_index += 1
            start_pos = i + 1
            current_chunk = []

    return chunks


def process_file(filepath: str) -> bool:
    if not os.path.exists(filepath) or not filepath.endswith(".txt"):
        print(
            f"Skipping {filepath}: "
            "Invalid file type or missing file."
        )
        return False

    if os.path.getsize(filepath) == 0:
        print(f"Skipping {filepath}: File is empty.")
        return False

    filename = os.path.basename(filepath)
    input_sha256 = calculate_file_hash(filepath)
    registry = load_registry()
    record = registry.get(filename, {})

    chunks_file_path = os.path.join(
        CHUNKS_DIR,
        f"{os.path.splitext(filename)[0]}_chunks.json",
    )

    is_complete = (
        record.get("processing_status") == "completed"
        and record.get("input_sha256") == input_sha256
        and record.get("embedding_model") == EMBEDDING_MODEL
        and record.get("breakpoint_percentile")
        == BREAKPOINT_PERCENTILE
        and record.get("buffer_size") == BUFFER_SIZE
        and record.get("chunking_version") == CHUNKING_VERSION
        and os.path.exists(record.get("chunks_file", ""))
    )

    if is_complete:
        try:
            with open(
                record["chunks_file"],
                "r",
                encoding=TEXT_ENCODING,
            ) as f:
                saved_text = f.read()

            if (
                calculate_text_hash(saved_text)
                == record.get("chunks_sha256")
            ):
                print(
                    f"Phase 1 validated for {filename}. "
                    "Loading saved chunks."
                )
                return True
        except Exception:
            pass

    print(
        f"Starting Phase 1 data preparation for {filename}..."
    )

    registry[filename] = {
        "processing_status": "pending"
    }
    save_registry(registry)

    try:
        with open(
            filepath,
            "r",
            encoding=TEXT_ENCODING,
        ) as f:
            raw_text = f.read()
    except UnicodeDecodeError:
        print(
            f"Error: {filepath} is not a valid UTF-8 text file."
        )
        registry[filename]["processing_status"] = "failed"
        save_registry(registry)
        return False

    try:
        prepared_text = prepare_paragraph_text(raw_text)

        if not prepared_text:
            raise ValueError(
                "File contains no valid text after preparation."
            )

        sentences = extract_sentences(prepared_text)
        windows = build_context_windows(sentences)
        embeddings = generate_and_normalize_embeddings(windows)
        breakpoints = detect_breakpoints(embeddings)
        semantic_chunks = build_semantic_chunks(
            sentences,
            breakpoints,
        )

        os.makedirs(CHUNKS_DIR, exist_ok=True)

        chunks_data = {
            "source_filename": filename,
            "input_sha256": input_sha256,
            "processing_settings": {
                "embedding_model": EMBEDDING_MODEL,
                "breakpoint_percentile": BREAKPOINT_PERCENTILE,
                "buffer_size": BUFFER_SIZE,
                "chunking_version": CHUNKING_VERSION,
            },
            "total_sentence_count": len(sentences),
            "total_chunk_count": len(semantic_chunks),
            "chunks": semantic_chunks,
        }

        chunks_json_str = json.dumps(
            chunks_data,
            indent=2,
            ensure_ascii=False,
        )
        chunks_sha256 = calculate_text_hash(
            chunks_json_str
        )

        with open(
            chunks_file_path,
            "w",
            encoding=TEXT_ENCODING,
        ) as f:
            f.write(chunks_json_str)

        registry[filename] = {
            "input_sha256": input_sha256,
            "processing_status": "completed",
            "embedding_model": EMBEDDING_MODEL,
            "breakpoint_percentile": BREAKPOINT_PERCENTILE,
            "buffer_size": BUFFER_SIZE,
            "chunking_version": CHUNKING_VERSION,
            "chunks_file": chunks_file_path,
            "chunks_sha256": chunks_sha256,
        }

        save_registry(registry)

        print(
            f"Phase 1 successfully completed for {filename}."
        )
        return True

    except Exception as error:
        print(f"Phase 1 failed for {filename}: {error}")
        registry[filename]["processing_status"] = "failed"
        save_registry(registry)
        return False
