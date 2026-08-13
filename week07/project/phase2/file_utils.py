import json
import os
from config import CHUNKS_DIR, SUMMARIES_DIR, TEXT_ENCODING


def list_chunks_files() -> list:
    if not os.path.isdir(CHUNKS_DIR):
        return []

    return sorted(
        os.path.join(CHUNKS_DIR, filename)
        for filename in os.listdir(CHUNKS_DIR)
        if filename.endswith(".json")
    )


def load_chunks_file(chunks_file_path: str) -> dict:
    with open(chunks_file_path, "r", encoding=TEXT_ENCODING) as file:
        chunks_data = json.load(file)

    chunks = chunks_data.get("chunks", [])

    if not isinstance(chunks, list) or not chunks:
        raise ValueError("The chunks file does not contain semantic chunks.")

    return chunks_data


def get_output_base_name(chunks_file_path: str) -> str:
    return os.path.splitext(os.path.basename(chunks_file_path))[0]


def save_partial_summaries(
    chunks_file_path: str,
    summarization_model: str,
    batches: list,
    map_summaries: list,
) -> str:
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    base_name = get_output_base_name(chunks_file_path)
    output_path = os.path.join(
        SUMMARIES_DIR,
        f"{base_name}_partial_summaries.json",
    )

    batch_details = [
        {
            "batch_id": batch["batch_id"],
            "source_chunk_numbers": batch["source_chunk_numbers"],
            "estimated_token_count": batch["estimated_token_count"],
        }
        for batch in batches
    ]

    output_data = {
        "source_chunks_file": chunks_file_path,
        "summarization_model": summarization_model,
        "total_batch_count": len(batches),
        "batches": batch_details,
        "partial_summaries": map_summaries,
    }

    with open(output_path, "w", encoding=TEXT_ENCODING) as file:
        json.dump(output_data, file, indent=2, ensure_ascii=False)

    return output_path


def save_full_summary(
    chunks_file_path: str,
    final_summary: str,
) -> str:
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    base_name = get_output_base_name(chunks_file_path)
    output_path = os.path.join(
        SUMMARIES_DIR,
        f"{base_name}_full_summary.txt",
    )

    with open(output_path, "w", encoding=TEXT_ENCODING) as file:
        file.write(final_summary.strip())

    return output_path
