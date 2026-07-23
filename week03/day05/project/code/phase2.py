import hashlib
import json
import os
import re

import ollama

from config import (
    TEXT_ENCODING,
    REGISTRY_PATH,
    SUMMARIES_DIR,
    SUMMARIZATION_MODEL,
    MIN_SUMMARIZATION_TOKENS,
    MAX_SUMMARIZATION_TOKENS,
    OLLAMA_KEEP_ALIVE,
)


def estimate_tokens(text: str) -> int:
    return len(text.split()) + (len(text) // 4) // 2


def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()

    with open(filepath, "rb") as file:
        for block in iter(lambda: file.read(4096), b""):
            hasher.update(block)

    return hasher.hexdigest()


def load_registry() -> dict:
    if not os.path.exists(REGISTRY_PATH):
        return {}

    try:
        with open(
            REGISTRY_PATH,
            "r",
            encoding=TEXT_ENCODING,
        ) as file:
            registry = json.load(file)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "The processing registry contains invalid JSON."
        ) from error
    except OSError as error:
        raise RuntimeError(
            "The processing registry could not be read."
        ) from error

    if not isinstance(registry, dict):
        raise ValueError(
            "The processing registry must contain a JSON object."
        )

    return registry


def get_response_text(response) -> str:
    response_text = getattr(response, "response", None)

    if response_text is None:
        try:
            response_text = response["response"]
        except (KeyError, TypeError) as error:
            raise ValueError(
                "Ollama response does not contain generated text."
            ) from error

    response_text = str(response_text).strip()

    if not response_text:
        raise ValueError("Ollama returned an empty response.")

    return response_text


def generate_text(prompt: str) -> str:
    try:
        response = ollama.generate(
            model=SUMMARIZATION_MODEL,
            prompt=prompt,
            stream=False,
            keep_alive=OLLAMA_KEEP_ALIVE,
        )
    except Exception as error:
        raise RuntimeError(
            f"Text generation failed using "
            f"'{SUMMARIZATION_MODEL}'."
        ) from error

    return get_response_text(response)


def split_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+",
            text.strip(),
        )
        if sentence.strip()
    ]


def split_oversized_text(text: str) -> list[str]:
    sentences = split_sentences(text)

    if not sentences:
        return [text]

    segments = []
    current_segment = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)

        if (
            current_segment
            and current_tokens + sentence_tokens
            > MAX_SUMMARIZATION_TOKENS
        ):
            segments.append(" ".join(current_segment))
            current_segment = []
            current_tokens = 0

        if sentence_tokens > MAX_SUMMARIZATION_TOKENS:
            segments.append(sentence)
            continue

        current_segment.append(sentence)
        current_tokens += sentence_tokens

    if current_segment:
        segments.append(" ".join(current_segment))

    return segments


def prepare_chunk_units(chunks: list) -> list[str]:
    units = []

    for chunk in chunks:
        chunk_text = str(chunk.get("text", "")).strip()

        if not chunk_text:
            continue

        chunk_tokens = chunk.get(
            "estimated_token_count",
            estimate_tokens(chunk_text),
        )

        if chunk_tokens > MAX_SUMMARIZATION_TOKENS:
            units.extend(split_oversized_text(chunk_text))
        else:
            units.append(chunk_text)

    return units


def rebalance_last_batch(
    batches: list[list[str]],
) -> list[list[str]]:
    if len(batches) < 2:
        return batches

    previous_batch = batches[-2]
    final_batch = batches[-1]

    previous_tokens = sum(
        estimate_tokens(text)
        for text in previous_batch
    )
    final_tokens = sum(
        estimate_tokens(text)
        for text in final_batch
    )

    if final_tokens >= MIN_SUMMARIZATION_TOKENS:
        return batches

    if (
        previous_tokens + final_tokens
        <= MAX_SUMMARIZATION_TOKENS
    ):
        batches[-2] = previous_batch + final_batch
        batches.pop()
        return batches

    while len(previous_batch) > 1:
        candidate = previous_batch[-1]
        candidate_tokens = estimate_tokens(candidate)

        remaining_previous_tokens = (
            previous_tokens - candidate_tokens
        )

        if (
            final_tokens + candidate_tokens
            > MAX_SUMMARIZATION_TOKENS
        ):
            break

        if (
            remaining_previous_tokens
            < MIN_SUMMARIZATION_TOKENS
        ):
            break

        previous_batch.pop()
        final_batch.insert(0, candidate)

        previous_tokens = remaining_previous_tokens
        final_tokens += candidate_tokens

        if final_tokens >= MIN_SUMMARIZATION_TOKENS:
            break

    return batches


def pack_text_units(units: list[str]) -> list[list[str]]:
    batches = []
    current_batch = []
    current_tokens = 0

    for unit in units:
        unit = unit.strip()

        if not unit:
            continue

        unit_tokens = estimate_tokens(unit)

        if (
            current_batch
            and current_tokens + unit_tokens
            > MAX_SUMMARIZATION_TOKENS
        ):
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

        current_batch.append(unit)
        current_tokens += unit_tokens

        if current_tokens >= MAX_SUMMARIZATION_TOKENS:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

    if current_batch:
        batches.append(current_batch)

    return rebalance_last_batch(batches)


def pack_chunks(chunks: list) -> list[list[str]]:
    units = prepare_chunk_units(chunks)
    return pack_text_units(units)


def map_summarize(
    batches: list[list[str]],
) -> list[str]:
    partial_summaries = []

    for index, batch in enumerate(batches, start=1):
        batch_text = "\n\n".join(batch)

        prompt = (
            "Summarize the following source text accurately. "
            "Use only the supplied source text. "
            "Preserve important events and facts. "
            "Preserve chronological order when relevant. "
            "Avoid adding unsupported information. "
            "Remove repetition and minor details. "
            "Return only the partial summary.\n\n"
            f"Source Text:\n{batch_text}"
        )

        print(
            f"  Generating partial summary "
            f"{index} of {len(batches)}..."
        )

        partial_summaries.append(
            generate_text(prompt)
        )

    return partial_summaries


def reduce_group(
    summaries: list[str],
    final_step: bool,
) -> str:
    if final_step:
        instruction = (
            "Combine the following ordered partial summaries "
            "into one coherent final summary. "
        )
    else:
        instruction = (
            "Combine the following ordered partial summaries "
            "into one coherent intermediate summary. "
        )

    prompt = (
        instruction
        + "Preserve the original information order. "
        + "Retain important information from all summaries. "
        + "Remove repeated information. "
        + "Avoid adding unsupported facts. "
        + "Return only the summary.\n\n"
        + "Partial Summaries:\n"
        + "\n\n".join(summaries)
    )

    return generate_text(prompt)


def prepare_reduce_units(
    summaries: list[str],
) -> list[str]:
    units = []

    for summary in summaries:
        summary = summary.strip()

        if not summary:
            continue

        if (
            estimate_tokens(summary)
            > MAX_SUMMARIZATION_TOKENS
        ):
            units.extend(
                split_oversized_text(summary)
            )
        else:
            units.append(summary)

    return units


def reduce_summarize(
    partial_summaries: list[str],
) -> str:
    current_summaries = [
        summary.strip()
        for summary in partial_summaries
        if summary.strip()
    ]

    if not current_summaries:
        raise ValueError(
            "No partial summaries were generated."
        )

    if len(current_summaries) == 1:
        return current_summaries[0]

    reduce_round = 1

    while len(current_summaries) > 1:
        if reduce_round > 20:
            raise RuntimeError(
                "Reduce processing exceeded the maximum "
                "number of rounds."
            )

        reduce_units = prepare_reduce_units(
            current_summaries
        )
        reduce_batches = pack_text_units(reduce_units)

        if not reduce_batches:
            raise RuntimeError(
                "No valid Reduce batches were created."
            )

        print(
            f"  Performing Reduce round "
            f"{reduce_round}..."
        )

        next_level = []

        for batch in reduce_batches:
            final_step = len(reduce_batches) == 1

            next_level.append(
                reduce_group(
                    batch,
                    final_step=final_step,
                )
            )

        current_summaries = next_level
        reduce_round += 1

    return current_summaries[0]


def process_file(filepath: str) -> bool:
    filename = os.path.basename(filepath)

    try:
        registry = load_registry()
    except Exception as error:
        print(
            f"Skipping Phase 2 for {filename}: {error}"
        )
        return False

    record = registry.get(filename, {})

    if record.get("processing_status") != "completed":
        print(
            f"Skipping Phase 2 for {filename}: "
            "Phase 1 incomplete or failed."
        )
        return False

    chunks_file = record.get("chunks_file")

    if not chunks_file or not os.path.isfile(chunks_file):
        print(
            f"Skipping Phase 2 for {filename}: "
            "Semantic chunks file missing."
        )
        return False

    expected_chunks_hash = record.get("chunks_sha256")

    if (
        not expected_chunks_hash
        or calculate_file_hash(chunks_file)
        != expected_chunks_hash
    ):
        print(
            f"Skipping Phase 2 for {filename}: "
            "Semantic chunks integrity check failed."
        )
        return False

    try:
        with open(
            chunks_file,
            "r",
            encoding=TEXT_ENCODING,
        ) as file:
            chunks_data = json.load(file)
    except UnicodeDecodeError:
        print(
            f"Skipping Phase 2 for {filename}: "
            "Chunks file is not valid UTF-8."
        )
        return False
    except (json.JSONDecodeError, OSError) as error:
        print(
            f"Skipping Phase 2 for {filename}: "
            f"Could not load chunks data: {error}"
        )
        return False

    chunks = chunks_data.get("chunks")

    if not isinstance(chunks, list) or not chunks:
        print(
            f"Skipping Phase 2 for {filename}: "
            "No semantic chunks were found."
        )
        return False

    print(
        f"Starting Phase 2 summarization "
        f"for {filename}..."
    )

    try:
        batches = pack_chunks(chunks)

        if not batches:
            raise ValueError(
                "No summarization batches were created."
            )

        partial_summaries = map_summarize(batches)

        if not partial_summaries:
            raise ValueError(
                "No partial summaries were generated."
            )

        os.makedirs(
            SUMMARIES_DIR,
            exist_ok=True,
        )

        base_name = os.path.splitext(filename)[0]

        partials_path = os.path.join(
            SUMMARIES_DIR,
            f"{base_name}_partial_summaries.txt",
        )

        with open(
            partials_path,
            "w",
            encoding=TEXT_ENCODING,
        ) as file:
            file.write(
                "\n\n---\n\n".join(
                    partial_summaries
                )
            )

        final_summary = reduce_summarize(
            partial_summaries
        )

        summary_path = os.path.join(
            SUMMARIES_DIR,
            f"{base_name}_summary.txt",
        )

        with open(
            summary_path,
            "w",
            encoding=TEXT_ENCODING,
        ) as file:
            file.write(final_summary)

    except Exception as error:
        print(
            f"Phase 2 failed for {filename}: {error}"
        )
        return False

    print(
        f"Phase 2 successfully completed "
        f"for {filename}. Outputs saved."
    )
    return True
