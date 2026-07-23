# phase2_summary.py
import os
import json
from config import *
from utils import load_registry, ensure_directory
from nlp_core import ollama_generate

def pack_chunks(chunks):
    """Combines neighboring semantic chunks based on token limits."""
    batches = []
    current_batch = []
    current_tokens = 0

    for chunk in chunks:
        chunk_tokens = chunk['token_count']
        
        if current_tokens + chunk_tokens > MAX_SUMMARIZATION_TOKENS and current_tokens >= MIN_SUMMARIZATION_TOKENS:
            batches.append(current_batch)
            current_batch = [chunk['text']]
            current_tokens = chunk_tokens
        else:
            current_batch.append(chunk['text'])
            current_tokens += chunk_tokens

    if current_batch:
        batches.append(current_batch)

    return batches

def map_summarize(batches):
    """Summarizes each packed batch independently."""
    partial_summaries = []
    for i, batch in enumerate(batches):
        batch_text = "\n\n".join(batch)
        prompt = (
            "Summarize the following text accurately. "
            "Preserve important events, chronological order, and facts. "
            "Remove minor details and repetition. Return only the summary.\n\n"
            f"Text:\n{batch_text}"
        )
        print(f"Generating partial summary {i+1}/{len(batches)}...")
        summary = ollama_generate(prompt, SUMMARIZATION_MODEL)
        partial_summaries.append(summary)
    return partial_summaries

def reduce_summarize(partial_summaries):
    """Combines partial summaries into one coherent final summary."""
    combined_text = "\n\n".join(partial_summaries)
    prompt = (
        "Combine the following partial summaries into one coherent, comprehensive final summary. "
        "Retain all critical information without adding unsupported facts.\n\n"
        f"Partial Summaries:\n{combined_text}"
    )
    print("Generating final reduced summary...")
    return ollama_generate(prompt, SUMMARIZATION_MODEL)

def process_file_phase2(filepath):
    """Executes the summarization phase for a completed text file."""
    filename = os.path.basename(filepath)
    registry = load_registry(REGISTRY_FILE)
    record = registry.get(filename, {})
    
    if record.get("processing_status") != "completed":
        print(f"Skipping Phase 2 for {filename}: Phase 1 incomplete.")
        return False

    chunks_file = record.get("chunks_file")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)

    print(f"Starting Phase 2 for {filename}. Packing chunks...")
    batches = pack_chunks(chunks_data['chunks'])
    
    partial_summaries = map_summarize(batches)
    final_summary = reduce_summarize(partial_summaries)
    
    ensure_directory(SUMMARIES_DIR)
    summary_path = os.path.join(SUMMARIES_DIR, f"{os.path.splitext(filename)[0]}_summary.txt")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(final_summary)
        
    print(f"Phase 2 complete. Final summary saved to {summary_path}.")
    return True