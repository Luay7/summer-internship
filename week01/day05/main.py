from pathlib import Path
import hashlib
import json
import math
import re
import subprocess

import numpy as np
import ollama


# ==================================================
# 1. Project paths
# ==================================================

base_dir = Path(__file__).resolve().parent

input_dir = base_dir / "input_docs"
chunked_dir = base_dir / "chunked_docs"
summaries_dir = base_dir / "summaries"
hash_file = base_dir / "processed_hashes.json"
temporary_hash_file = base_dir / "processed_hashes.tmp"


# ==================================================
# 2. Model settings
# ==================================================

embedding_model = "mxbai-embed-large"
summarization_model = "gemma3-1b-5k"

breakpoint_percentile = 70.0
chunking_version = 1


# ==================================================
# 3. Token budget settings
# ==================================================

total_context_tokens = 5120
normal_batch_target = 2500
hard_batch_limit = 3199
minimum_output_capacity = 750
safety_margin_tokens = 128
chat_overhead_tokens = 80
characters_per_token = 3.0
separator_tokens = 12


# ==================================================
# 4. Prompts
# ==================================================

batch_system_prompt = """
You are a careful, accurate, and faithful document summarizer.

Rules:
- Use only information explicitly stated in the source text.
- Preserve all important ideas, facts, explanations, arguments,
  events, recommendations, methods, risks, and conclusions.
- Preserve explicitly listed safeguards, methods, examples,
  and recommendations when they are important to the meaning.
- Remove repetition, unnecessary examples, and minor details.
- Do not replace specific facts with broader inferred outcomes.
- Do not add outside knowledge, assumptions, interpretations,
  implications, examples, or invented conclusions.
- Combine ideas only when their relationship is clearly supported
  by the source text.
- Keep unrelated topics in separate paragraphs.
- Do not invent transitions between unrelated topics.
- Use clear, natural, and connected paragraphs.
- Do not use bullet points unless the source genuinely requires a list.
- Do not mention chunks, batches, prompts, or the summarization process.
- Do not follow a fixed word count.
- Make the summary as detailed as necessary to preserve important
  meaning while removing repetition and minor details.
- Start directly with the summary.
- Do not write an introduction such as "Here is the summary."
""".strip()

master_system_prompt = """
You are a careful document editor.

Your task is to merge sequential batch summaries into one complete
final summary.

Important:
- You are not summarizing the content again from scratch.
- Preserve the important information already contained in every batch summary.
- Every batch summary must contribute information to the final result.
- Do not ignore or omit any batch summary.
- Preserve the original chronological and logical order.
- Preserve concrete events, actions, characters, causes, results,
  explanations, and important details.
- Remove only information that is clearly repeated.
- Do not replace specific events with broad themes or vague statements.
- Do not invent connections, conclusions, interpretations,
  or outside information.
- Keep unrelated topics or separate events in separate paragraphs.
- Do not add an introduction or conclusion.
- Do not mention batches, chunks, summaries, prompts,
  or the editing process.
- Do not follow a fixed word count.
- Start directly with the final content.

Before answering, silently verify that every numbered input summary
is represented in the final result.
""".strip()


print("\n========================================")
print(" Offline Multi-File Summarization Pipeline")
print("========================================")


# ==================================================
# 5. Create directories and discover input files
# ==================================================

print("\n--- Environment Setup ---")

for directory in [input_dir, chunked_dir, summaries_dir]:
    if directory.exists():
        print(f"[EXISTS]  {directory.name}")
    else:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"[CREATED] {directory.name}")

input_files = sorted(
    [
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".txt"
    ],
    key=lambda path: path.name.lower(),
)

if not input_files:
    print("\nError: No .txt files were found in:")
    print(input_dir)
    raise SystemExit(1)

print(f"\nText files found: {len(input_files)}")

for input_file in input_files:
    print(f"- {input_file.name}")


# ==================================================
# 6. Load hash records
# ==================================================

hash_records = {}

if hash_file.exists():
    try:
        hash_records = json.loads(
            hash_file.read_text(encoding="utf-8")
        )

        if not isinstance(hash_records, dict):
            print(
                "Warning: processed_hashes.json has an invalid "
                "structure. A new record will be used."
            )
            hash_records = {}

    except json.JSONDecodeError:
        print(
            "Warning: processed_hashes.json is corrupted. "
            "A new record will be used."
        )
        hash_records = {}


# This list stores only lightweight metadata and paths.
# The chunks are loaded or created during phase one.
documents = []
chunking_success_count = 0
chunking_failure_count = 0
cache_hit_count = 0
cache_miss_count = 0


# ==================================================
# 7. PHASE ONE: semantic chunking for every file
# ==================================================

print("\n========================================")
print(" PHASE ONE: SEMANTIC CHUNKING")
print("========================================")

for file_index, input_file in enumerate(input_files, start=1):
    print("\n----------------------------------------")
    print(
        f"Chunking file {file_index}/{len(input_files)}: "
        f"{input_file.name}"
    )
    print("----------------------------------------")

    file_stem = input_file.stem

    chunks_output_file = (
        chunked_dir / f"{file_stem}_chunks.txt"
    )

    batch_summaries_file = (
        summaries_dir / f"{file_stem}_batch_summaries.txt"
    )

    final_summary_file = (
        summaries_dir / f"{file_stem}_summary.txt"
    )

    try:
        input_bytes = input_file.read_bytes()
        text = input_bytes.decode("utf-8").strip()

    except UnicodeDecodeError:
        print("[SKIPPED] The file is not valid UTF-8 text.")
        chunking_failure_count += 1
        continue

    except OSError as error:
        print(f"[SKIPPED] Could not read the file: {error}")
        chunking_failure_count += 1
        continue

    if not text:
        print("[SKIPPED] The file is empty.")
        chunking_failure_count += 1
        continue

    input_hash = hashlib.sha256(input_bytes).hexdigest()

    chunk_signature_data = {
        "input_sha256": input_hash,
        "embedding_model": embedding_model,
        "breakpoint_percentile": breakpoint_percentile,
        "chunking_version": chunking_version,
        "paragraph_split_method": "blank-line-paragraphs",
    }

    chunk_signature_json = json.dumps(
        chunk_signature_data,
        sort_keys=True,
        ensure_ascii=False,
    )

    chunk_signature = hashlib.sha256(
        chunk_signature_json.encode("utf-8")
    ).hexdigest()

    previous_record = hash_records.get(input_file.name, {})

    can_reuse_chunks = (
        previous_record.get("chunk_signature") == chunk_signature
        and chunks_output_file.exists()
    )

    chunks = []

    if can_reuse_chunks:
        cached_chunk_text = chunks_output_file.read_text(
            encoding="utf-8"
        ).strip()

        chunks = [
            chunk.strip()
            for chunk in re.split(
                r"===== CHUNK \d+ =====",
                cached_chunk_text,
            )
            if chunk.strip()
        ]

        if chunks:
            print("[CACHE HIT] Reusing saved semantic chunks.")
            print(f"Cached chunks loaded: {len(chunks)}")
            cache_hit_count += 1

        else:
            print(
                "Warning: The cached chunk file is empty or invalid. "
                "Chunking will run again."
            )
            can_reuse_chunks = False

    if not can_reuse_chunks:
        cache_miss_count += 1
        print("[CACHE MISS] Semantic chunking is required.")

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

        if not paragraphs:
            print("[SKIPPED] No usable paragraphs were found.")
            chunking_failure_count += 1
            continue

        print(f"Paragraphs found: {len(paragraphs)}")

        if len(paragraphs) == 1:
            chunks = paragraphs
            print(
                "Only one paragraph was found. "
                "The embedding model was not needed."
            )

        else:
            print(
                f"Creating paragraph embeddings with: "
                f"{embedding_model}"
            )

            try:
                embedding_response = ollama.embed(
                    model=embedding_model,
                    input=paragraphs,
                    truncate=False,
                    # Keep it loaded throughout the whole chunking phase.
                    keep_alive="30m",
                )

            except Exception as error:
                print(f"[SKIPPED] Embedding failed: {error}")
                chunking_failure_count += 1
                continue

            embeddings = np.array(
                embedding_response.embeddings,
                dtype=np.float32,
            )

            distances = []

            for index in range(len(embeddings) - 1):
                first_vector = embeddings[index]
                second_vector = embeddings[index + 1]

                denominator = (
                    np.linalg.norm(first_vector)
                    * np.linalg.norm(second_vector)
                )

                if denominator == 0:
                    similarity = 0.0
                else:
                    similarity = float(
                        np.dot(first_vector, second_vector)
                        / denominator
                    )

                distances.append(1.0 - similarity)

            distance_threshold = float(
                np.percentile(
                    distances,
                    breakpoint_percentile,
                )
            )

            print(
                f"Breakpoint threshold: "
                f"{distance_threshold:.4f}"
            )

            chunks = []
            current_chunk = [paragraphs[0]]

            for index, distance in enumerate(distances):
                print(
                    f"Paragraph {index + 1} -> {index + 2}: "
                    f"distance = {distance:.4f}"
                )

                if distance > distance_threshold:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [paragraphs[index + 1]]
                else:
                    current_chunk.append(paragraphs[index + 1])

            chunks.append("\n\n".join(current_chunk))

        chunks_file_content = ""

        for chunk_index, chunk in enumerate(chunks, start=1):
            chunks_file_content += (
                f"===== CHUNK {chunk_index} =====\n"
                f"{chunk}\n\n"
            )

        chunks_output_file.write_text(
            chunks_file_content.strip() + "\n",
            encoding="utf-8",
        )

        hash_records[input_file.name] = {
            "input_sha256": input_hash,
            "chunk_signature": chunk_signature,
            "embedding_model": embedding_model,
            "breakpoint_percentile": breakpoint_percentile,
            "chunking_version": chunking_version,
            "chunks_file": str(
                chunks_output_file.relative_to(base_dir)
            ),
        }

        temporary_hash_file.write_text(
            json.dumps(
                hash_records,
                ensure_ascii=False,
                indent=4,
            ),
            encoding="utf-8",
        )

        temporary_hash_file.replace(hash_file)

        print(f"Semantic chunks created: {len(chunks)}")
        print(f"Chunks saved at:\n{chunks_output_file}")
        print("Hash record updated.")

    documents.append(
        {
            "input_file": input_file,
            "chunks_output_file": chunks_output_file,
            "batch_summaries_file": batch_summaries_file,
            "final_summary_file": final_summary_file,
        }
    )

    chunking_success_count += 1


# Unload the embedding model only after every file has finished phase one.
print("\n--- Finishing the Chunking Phase ---")

embedding_stop_result = subprocess.run(
    ["ollama", "stop", embedding_model],
    capture_output=True,
    text=True,
    check=False,
)

if embedding_stop_result.returncode == 0:
    print("Embedding model unloaded from memory.")
else:
    print(
        "Embedding model was already unloaded or was not loaded."
    )

print(
    f"Chunking phase complete: "
    f"{chunking_success_count} ready, "
    f"{chunking_failure_count} skipped."
)
print(f"Cache hits: {cache_hit_count}")
print(f"Cache misses: {cache_miss_count}")

if not documents:
    print("\nNo valid documents are available for summarization.")
    raise SystemExit(1)


# ==================================================
# 8. PHASE TWO: summarize every processed file
# ==================================================

print("\n========================================")
print(" PHASE TWO: SUMMARIZATION")
print("========================================")

summary_success_count = 0
summary_failure_count = 0

try:
    for document_index, document in enumerate(documents, start=1):
        input_file = document["input_file"]
        chunks_output_file = document["chunks_output_file"]
        batch_summaries_file = document["batch_summaries_file"]
        final_summary_file = document["final_summary_file"]

        print("\n----------------------------------------")
        print(
            f"Summarizing file {document_index}/{len(documents)}: "
            f"{input_file.name}"
        )
        print("----------------------------------------")

        try:
            chunked_text = chunks_output_file.read_text(
                encoding="utf-8"
            ).strip()

            chunks = [
                chunk.strip()
                for chunk in re.split(
                    r"===== CHUNK \d+ =====",
                    chunked_text,
                )
                if chunk.strip()
            ]

            if not chunks:
                print("[SKIPPED] No valid chunks were found.")
                summary_failure_count += 1
                continue

            print(f"Chunks found: {len(chunks)}")

            chunks_with_tokens = []
            oversized_chunk_found = False

            print("\n--- Estimated Chunk Sizes ---")

            for chunk_index, chunk in enumerate(chunks, start=1):
                estimated_tokens = max(
                    1,
                    math.ceil(
                        len(chunk) / characters_per_token
                    ),
                )

                print(
                    f"Chunk {chunk_index}: approximately "
                    f"{estimated_tokens} tokens"
                )

                if estimated_tokens > hard_batch_limit:
                    print(
                        f"[SKIPPED] Chunk {chunk_index} exceeds "
                        f"the hard limit of {hard_batch_limit} tokens."
                    )
                    print(
                        "Secondary splitting for oversized chunks "
                        "has not been added yet."
                    )
                    oversized_chunk_found = True
                    break

                chunks_with_tokens.append(
                    {
                        "number": chunk_index,
                        "text": chunk,
                        "estimated_tokens": estimated_tokens,
                    }
                )

            if oversized_chunk_found:
                summary_failure_count += 1
                continue

            batches = []
            current_batch = []
            current_batch_tokens = 0

            print("\n--- Building Batches ---")

            for chunk_data in chunks_with_tokens:
                chunk_number = chunk_data["number"]
                chunk_tokens = chunk_data["estimated_tokens"]

                extra_separator_tokens = (
                    separator_tokens if current_batch else 0
                )

                new_total = (
                    current_batch_tokens
                    + extra_separator_tokens
                    + chunk_tokens
                )

                if new_total <= hard_batch_limit:
                    current_batch.append(chunk_data)
                    current_batch_tokens = new_total

                    if current_batch_tokens <= normal_batch_target:
                        print(
                            f"Chunk {chunk_number} added normally. "
                            f"Batch size: {current_batch_tokens} tokens"
                        )
                    else:
                        print(
                            f"Chunk {chunk_number} added using "
                            f"the flexible area. "
                            f"Batch size: {current_batch_tokens} tokens"
                        )

                else:
                    batches.append(current_batch)
                    print(
                        f"Batch {len(batches)} closed at "
                        f"{current_batch_tokens} tokens."
                    )

                    current_batch = [chunk_data]
                    current_batch_tokens = chunk_tokens

                    print(
                        f"Chunk {chunk_number} started a new batch."
                    )

            if current_batch:
                batches.append(current_batch)
                print(
                    f"Batch {len(batches)} closed at "
                    f"{current_batch_tokens} tokens."
                )

            print(f"\nTotal batches created: {len(batches)}")

            for batch_index, batch in enumerate(batches, start=1):
                chunk_numbers = [
                    str(item["number"]) for item in batch
                ]

                batch_tokens = sum(
                    item["estimated_tokens"] for item in batch
                )

                batch_tokens += (
                    max(0, len(batch) - 1) * separator_tokens
                )

                print(
                    f"Batch {batch_index}: chunks "
                    f"{', '.join(chunk_numbers)} "
                    f"({batch_tokens} estimated tokens)"
                )

            batch_summaries = []
            saved_batch_summaries = []
            summarization_failed = False

            print("\n--- Batch Summarization ---")

            for batch_index, batch in enumerate(batches, start=1):
                batch_parts = []

                for chunk_data in batch:
                    batch_parts.append(
                        f"[CHUNK {chunk_data['number']}]\n"
                        f"{chunk_data['text']}"
                    )

                batch_text = "\n\n".join(batch_parts)

                batch_user_prompt = f"""
Summarize the consecutive document content below.

The chunk labels only identify text boundaries.
They are not part of the source and must not appear in the result.

Preserve the important information accurately.
Keep independent topics in separate paragraphs.
Do not invent relationships between them.

Document content:
{batch_text}

Summary:
""".strip()

                estimated_prompt_tokens = math.ceil(
                    (
                        len(batch_system_prompt)
                        + len(batch_user_prompt)
                    )
                    / characters_per_token
                )

                estimated_prompt_tokens += chat_overhead_tokens

                available_output_tokens = (
                    total_context_tokens
                    - estimated_prompt_tokens
                    - safety_margin_tokens
                )

                print(
                    f"\nSummarizing batch "
                    f"{batch_index}/{len(batches)}..."
                )
                print(
                    f"Estimated complete prompt: "
                    f"{estimated_prompt_tokens} tokens"
                )
                print(
                    f"Available output capacity: "
                    f"{available_output_tokens} tokens"
                )

                if available_output_tokens < minimum_output_capacity:
                    print(
                        f"[SKIPPED] This batch leaves fewer than "
                        f"{minimum_output_capacity} output tokens."
                    )
                    summarization_failed = True
                    break

                response = ollama.chat(
                    model=summarization_model,
                    messages=[
                        {
                            "role": "system",
                            "content": batch_system_prompt,
                        },
                        {
                            "role": "user",
                            "content": batch_user_prompt,
                        },
                    ],
                    options={
                        "num_ctx": total_context_tokens,
                        "num_predict": available_output_tokens,
                        "temperature": 0.0,
                        "seed": 42,
                    },
                    # Keep Gemma loaded across all batches and files.
                    keep_alive="30m",
                )

                batch_summary = response.message.content.strip()

                if not batch_summary:
                    print("[SKIPPED] The model returned an empty summary.")
                    summarization_failed = True
                    break

                batch_summaries.append(batch_summary)
                saved_batch_summaries.append(
                    f"===== BATCH SUMMARY {batch_index} =====\n"
                    f"{batch_summary}"
                )

                actual_prompt_tokens = getattr(
                    response,
                    "prompt_eval_count",
                    None,
                )

                actual_output_tokens = getattr(
                    response,
                    "eval_count",
                    None,
                )

                print(
                    f"Batch {batch_index} summarized successfully."
                )

                if actual_prompt_tokens is not None:
                    print(
                        f"Actual prompt tokens: "
                        f"{actual_prompt_tokens}"
                    )

                if actual_output_tokens is not None:
                    print(
                        f"Actual generated tokens: "
                        f"{actual_output_tokens}"
                    )

                if (
                    actual_prompt_tokens is not None
                    and actual_output_tokens is not None
                ):
                    actual_total_tokens = (
                        actual_prompt_tokens
                        + actual_output_tokens
                    )

                    print(
                        f"Actual total context used: "
                        f"{actual_total_tokens}/"
                        f"{total_context_tokens}"
                    )

            if summarization_failed:
                summary_failure_count += 1
                continue

            batch_summaries_file.write_text(
                "\n\n".join(saved_batch_summaries) + "\n",
                encoding="utf-8",
            )

            print(
                "\nBatch summaries saved at:"
                f"\n{batch_summaries_file}"
            )

            print("\n--- Final Summary Stage ---")

            if len(batch_summaries) == 1:
                final_summary = batch_summaries[0]
                print("Only one batch was required.")
                print("No second model call is needed.")

            else:
                labeled_summaries = ""

                for summary_index, summary in enumerate(
                    batch_summaries,
                    start=1,
                ):
                    labeled_summaries += (
                        f"[BATCH SUMMARY {summary_index}]\n"
                        f"{summary}\n\n"
                    )

                master_user_prompt = f"""
Merge the following {len(batch_summaries)} sequential summaries into
one complete final summary.

Requirements:
- Include the important information from all {len(batch_summaries)}
  summaries.
- Keep their original order.
- Remove only genuine repetition.
- Do not shorten the content so aggressively that events or details
  from any summary disappear.
- Use clear paragraphs and natural transitions only when the
  relationship is already supported by the input.

Sequential summaries:
{labeled_summaries}

Final merged summary:
""".strip()

                estimated_master_prompt_tokens = math.ceil(
                    (
                        len(master_system_prompt)
                        + len(master_user_prompt)
                    )
                    / characters_per_token
                )

                estimated_master_prompt_tokens += (
                    chat_overhead_tokens
                )

                available_master_output_tokens = (
                    total_context_tokens
                    - estimated_master_prompt_tokens
                    - safety_margin_tokens
                )

                print(
                    f"Estimated final-stage prompt: "
                    f"{estimated_master_prompt_tokens} tokens"
                )
                print(
                    f"Available final output capacity: "
                    f"{available_master_output_tokens} tokens"
                )

                if (
                    available_master_output_tokens
                    < minimum_output_capacity
                ):
                    print(
                        "[SKIPPED] The batch summaries leave "
                        "insufficient room for the final output."
                    )
                    print(
                        "Recursive summarization will be added later."
                    )
                    summary_failure_count += 1
                    continue

                final_response = ollama.chat(
    model=summarization_model,
    messages=[
        {
            "role": "system",
            "content": master_system_prompt,
        },
        {
            "role": "user",
            "content": master_user_prompt,
        },
    ],
    options={
        "num_ctx": total_context_tokens,
        "num_predict": available_master_output_tokens,
        "temperature": 0.0,
        "seed": 42,
    },
    keep_alive=0,
)

                final_summary = (
                    final_response.message.content.strip()
                )

                if not final_summary:
                    print(
                        "[SKIPPED] The model returned an empty "
                        "final summary."
                    )
                    summary_failure_count += 1
                    continue

                actual_master_prompt_tokens = getattr(
                    final_response,
                    "prompt_eval_count",
                    None,
                )

                actual_master_output_tokens = getattr(
                    final_response,
                    "eval_count",
                    None,
                )

                if actual_master_prompt_tokens is not None:
                    print(
                        f"Actual final prompt tokens: "
                        f"{actual_master_prompt_tokens}"
                    )

                if actual_master_output_tokens is not None:
                    print(
                        f"Actual final generated tokens: "
                        f"{actual_master_output_tokens}"
                    )

            final_summary_file.write_text(
                final_summary + "\n",
                encoding="utf-8",
            )

            print("\n--- Final Summary Result ---")
            print(final_summary)
            print(
                "\nFinal summary saved successfully at:"
                f"\n{final_summary_file}"
            )

            summary_success_count += 1

        except Exception as error:
            print(
                f"[SKIPPED] Unexpected summarization error: "
                f"{error}"
            )
            summary_failure_count += 1
            continue

finally:
    # Unload Gemma only after every document has completed phase two.
    print("\n--- Finishing the Summarization Phase ---")

    summary_stop_result = subprocess.run(
        ["ollama", "stop", summarization_model],
        capture_output=True,
        text=True,
        check=False,
    )

    if summary_stop_result.returncode == 0:
        print("Summarization model unloaded from memory.")
    else:
        print(
            "Summarization model was already unloaded "
            "or was not loaded."
        )


# ==================================================
# 9. Final report
# ==================================================

print("\n========================================")
print(" PIPELINE COMPLETED")
print("========================================")
print(f"Input files discovered: {len(input_files)}")
print(f"Files ready after chunking: {chunking_success_count}")
print(f"Chunking files skipped: {chunking_failure_count}")
print(f"Summaries created: {summary_success_count}")
print(f"Summarization files skipped: {summary_failure_count}")
print("\nRun 'ollama ps' to confirm that both models are unloaded.")


