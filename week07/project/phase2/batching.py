from config import MAX_TOKENS_PER_BATCH


def estimate_tokens(text: str) -> int:
    return len(text.split()) + (len(text) // 4) // 2


def get_chunk_token_count(chunk: dict) -> int:
    token_count = chunk.get("estimated_token_count", 0)

    if isinstance(token_count, int) and token_count > 0:
        return token_count

    return estimate_tokens(chunk.get("text", ""))


def create_batch(
    batch_id: int,
    texts: list,
    token_count: int,
    chunk_numbers: list,
) -> dict:
    return {
        "batch_id": batch_id,
        "source_chunk_numbers": chunk_numbers,
        "text": "\n\n".join(texts),
        "estimated_token_count": token_count,
    }


def build_token_batches(chunks: list) -> list:
    if MAX_TOKENS_PER_BATCH <= 0:
        raise ValueError("MAX_TOKENS_PER_BATCH must be greater than zero.")

    if not chunks:
        raise ValueError("No semantic chunks were provided for batching.")

    batches = []
    current_texts = []
    current_chunk_numbers = []
    current_token_count = 0
    batch_id = 1

    for position, chunk in enumerate(chunks, start=1):
        chunk_text = chunk.get("text", "").strip()

        if not chunk_text:
            raise ValueError(f"Semantic chunk {position} contains no text.")

        chunk_token_count = get_chunk_token_count(chunk)
        chunk_number = chunk.get("chunk_number", position)

        if (
            current_texts
            and current_token_count + chunk_token_count > MAX_TOKENS_PER_BATCH
        ):
            batches.append(
                create_batch(
                    batch_id,
                    current_texts,
                    current_token_count,
                    current_chunk_numbers,
                )
            )
            batch_id += 1
            current_texts = []
            current_chunk_numbers = []
            current_token_count = 0

        current_texts.append(chunk_text)
        current_chunk_numbers.append(chunk_number)
        current_token_count += chunk_token_count

    if current_texts:
        batches.append(
            create_batch(
                batch_id,
                current_texts,
                current_token_count,
                current_chunk_numbers,
            )
        )

    return batches
