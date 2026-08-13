def estimate_tokens(text: str) -> int:
    # A fast, heuristic-based token estimation 
    # (1 token ~= 4 characters or 0.75 words)
    return len(text.split()) + (len(text) // 4) // 2


def build_semantic_chunks(sentences: list, breakpoints: list) -> list:
    chunks = []
    current_chunk = []
    start_pos = 0
    chunk_index = 1

    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence)

        # Split if we hit a breakpoint or the last sentence
        if i in breakpoints or i == len(sentences) - 1:
            chunk_text = " ".join(current_chunk)

            chunks.append(
                {
                    "chunk_number": chunk_index,
                    "first_sentence_position": start_pos,
                    "final_sentence_position": i,
                    "sentence_count": len(current_chunk),
                    "character_count": len(chunk_text),
                    "estimated_token_count": estimate_tokens(chunk_text),
                    "text": chunk_text,
                }
            )

            chunk_index += 1
            start_pos = i + 1
            current_chunk = []

    return chunks
