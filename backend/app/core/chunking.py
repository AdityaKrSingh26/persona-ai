import tiktoken

# cl100k_base matches the tokenizer used by text-embedding-3-small, keeping token counts accurate
ENCODER = tiktoken.get_encoding("cl100k_base")


def _hard_split(tokens: list[int], chunk_size: int, overlap: int) -> list[list[int]]:
    """Split a token list that exceeds chunk_size into overlapping chunks.

    Handles the v1.0 bug where a single oversized paragraph was never split,
    potentially exceeding the embedding model's input limit.
    """
    out: list[list[int]] = []
    step = chunk_size - overlap
    start = 0
    while start < len(tokens):
        out.append(tokens[start : start + chunk_size])
        start += step
    return out


def chunk_text(
    text: str,
    chunk_size: int = 400,
    overlap: int = 50,
    split_on: str = "\n\n",
) -> list[str]:
    """Chunk text into overlapping token windows.

    Splits on paragraph boundaries first (split_on), then falls back to
    hard token-level splitting for any segment that alone exceeds chunk_size.
    The overlap carry ensures semantic continuity across chunk boundaries.
    """
    segments = [s.strip() for s in text.split(split_on) if s.strip()]
    token_chunks: list[list[int]] = []
    current: list[int] = []

    for seg in segments:
        seg_tokens = ENCODER.encode(seg)

        if len(seg_tokens) > chunk_size:
            # Single oversized segment — hard split to guarantee we stay within limit
            if current:
                token_chunks.append(current)
                current = []
            token_chunks.extend(_hard_split(seg_tokens, chunk_size, overlap))
            continue

        if len(current) + len(seg_tokens) > chunk_size and current:
            token_chunks.append(current)
            current = current[-overlap:]  # carry overlap forward for semantic continuity

        current.extend(seg_tokens)

    if current:
        token_chunks.append(current)

    return [ENCODER.decode(c) for c in token_chunks]
