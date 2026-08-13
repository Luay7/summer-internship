from phase2.batching import build_token_batches
from phase2.file_utils import (
    list_chunks_files,
    load_chunks_file,
    save_partial_summaries,
    save_full_summary,
)
from phase2.summarization import (
    SUMMARIZATION_MODEL,
    map_summarize,
    reduce_summarize,
)


def process_chunks_file(chunks_file_path: str) -> bool:
    print(f"Starting Phase 2 for {chunks_file_path}...")

    try:
        chunks_data = load_chunks_file(chunks_file_path)
        batches = build_token_batches(chunks_data["chunks"])

        print(f"Created {len(batches)} summarization batches.")

        map_summaries = map_summarize(batches)
        final_summary = reduce_summarize(map_summaries)

        partial_output_path = save_partial_summaries(
            chunks_file_path,
            SUMMARIZATION_MODEL,
            batches,
            map_summaries,
        )
        full_output_path = save_full_summary(
            chunks_file_path,
            final_summary,
        )

        print(f"Partial summaries saved to: {partial_output_path}")
        print(f"Full summary saved to: {full_output_path}")
        print(f"Phase 2 successfully completed for {chunks_file_path}.")
        return True

    except Exception as error:
        print(f"Phase 2 failed for {chunks_file_path}: {error}")
        return False


def run_phase2() -> bool:
    chunks_files = list_chunks_files()

    if not chunks_files:
        print("No chunks files were found for Phase 2.")
        return False

    successful_count = 0

    for chunks_file_path in chunks_files:
        if process_chunks_file(chunks_file_path):
            successful_count += 1

    print(
        f"Phase 2 completed: {successful_count} of "
        f"{len(chunks_files)} files succeeded."
    )

    return successful_count == len(chunks_files)
