# phase1_prep.py
import os
import json
import numpy as np
from config import *
from utils import calculate_file_hash, calculate_text_hash, load_registry, save_registry, ensure_directory, approximate_tokens
from nlp_core import extract_sentences, generate_embedding, normalize_vector, cosine_distance

def calculate_breakpoints(distances, percentile):
    """Calculates breakpoints where meaningful topic changes are detected."""
    if not distances:
        return []
    threshold = np.percentile(distances, percentile)
    return [i for i, dist in enumerate(distances) if dist > threshold]

def build_semantic_chunks(sentences, breakpoints):
    """Groups sentences between breakpoints into semantic chunks."""
    chunks = []
    current_chunk_sentences = []
    start_pos = 0
    chunk_index = 1

    for i, sentence in enumerate(sentences):
        current_chunk_sentences.append(sentence)
        if i in breakpoints or i == len(sentences) - 1:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                "chunk_number": chunk_index,
                "first_sentence_position": start_pos,
                "final_sentence_position": i,
                "sentence_count": len(current_chunk_sentences),
                "character_count": len(chunk_text),
                "token_count": approximate_tokens(chunk_text),
                "text": chunk_text
            })
            chunk_index += 1
            start_pos = i + 1
            current_chunk_sentences = []
            
    return chunks

def process_file_phase1(filepath, stanza_pipeline):
    """Executes the data preparation phase for a single text file."""
    if not os.path.exists(filepath) or not filepath.endswith('.txt'):
        print(f"Skipping {filepath}: Invalid or missing file.")
        return False

    file_size = os.path.getsize(filepath)
    if file_size == 0:
        print(f"Skipping {filepath}: File is empty.")
        return False

    filename = os.path.basename(filepath)
    input_sha256 = calculate_file_hash(filepath)
    registry = load_registry(REGISTRY_FILE)
    record = registry.get(filename, {})

    chunks_file_path = os.path.join(CHUNKS_DIR, f"{os.path.splitext(filename)[0]}_chunks.json")
    
    is_complete = (
        record.get("processing_status") == "completed" and
        record.get("input_sha256") == input_sha256 and
        record.get("embedding_model") == EMBEDDING_MODEL and
        record.get("breakpoint_percentile") == BREAKPOINT_PERCENTILE and
        record.get("buffer_size") == BUFFER_SIZE and
        os.path.exists(record.get("chunks_file", ""))
    )

    if is_complete:
        with open(record["chunks_file"], 'r', encoding='utf-8') as f:
            saved_chunks_text = f.read()
            if calculate_text_hash(saved_chunks_text) == record.get("chunks_sha256"):
                print(f"Phase 1 complete for {filename}: Valid saved chunks loaded.")
                return True

    print(f"Running complete data-preparation phase for {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    sentences = extract_sentences(stanza_pipeline, text)
    embeddings = []
    
    for i in range(len(sentences)):
        start_idx = max(0, i - BUFFER_SIZE)
        end_idx = min(len(sentences), i + BUFFER_SIZE + 1)
        context_window = " ".join(sentences[start_idx:end_idx])
        raw_emb = generate_embedding(context_window, EMBEDDING_MODEL)
        embeddings.append(normalize_vector(raw_emb))

    distances = []
    for i in range(len(embeddings) - 1):
        distances.append(cosine_distance(embeddings[i], embeddings[i+1]))

    breakpoints = calculate_breakpoints(distances, BREAKPOINT_PERCENTILE)
    semantic_chunks = build_semantic_chunks(sentences, breakpoints)

    ensure_directory(CHUNKS_DIR)
    
    chunks_data = {
        "source_filename": filename,
        "input_sha256": input_sha256,
        "processing_settings": {
            "embedding_model": EMBEDDING_MODEL,
            "breakpoint_percentile": BREAKPOINT_PERCENTILE,
            "buffer_size": BUFFER_SIZE,
            "chunking_version": CHUNKING_VERSION
        },
        "total_sentence_count": len(sentences),
        "total_chunk_count": len(semantic_chunks),
        "chunks": semantic_chunks
    }
    
    chunks_json_str = json.dumps(chunks_data, indent=2)
    chunks_sha256 = calculate_text_hash(chunks_json_str)

    with open(chunks_file_path, 'w', encoding='utf-8') as f:
        f.write(chunks_json_str)

    registry[filename] = {
        "input_sha256": input_sha256,
        "processing_status": "completed",
        "embedding_model": EMBEDDING_MODEL,
        "breakpoint_percentile": BREAKPOINT_PERCENTILE,
        "buffer_size": BUFFER_SIZE,
        "chunking_version": CHUNKING_VERSION,
        "chunks_file": chunks_file_path,
        "chunks_sha256": chunks_sha256
    }
    
    save_registry(REGISTRY_FILE, registry)
    print(f"Phase 1 successfully finished for {filename}.")
    return True