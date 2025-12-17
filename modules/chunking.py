# modules/chunking.py

from typing import List, Dict
import re
import tiktoken


class TextChunker:
    """
    Semantic + token-aware chunker for high-quality RAG systems.
    Optimized for Gemini / OpenAI embeddings.
    """

    def __init__(
        self,
        chunk_size: int = 450,
        chunk_overlap: int = 80,
        tokenizer_model: str = "gpt-4o-mini"  # tokenizer proxy only
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.encoding_for_model(tokenizer_model)

    # ---------- helpers ----------

    def _token_len(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def _split_sentences(self, text: str) -> List[str]:
        """
        Lightweight sentence splitter (no heavy NLP dependency).
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    # ---------- main API ----------

    def chunk_text(
        self,
        text: str,
        source: str,
        page_number: int | None = None
    ) -> List[Dict]:
        """
        Produces semantically coherent, overlapping chunks with rich metadata.
        """
        sentences = self._split_sentences(text)
        chunks = []

        current_chunk = []
        current_tokens = 0
        chunk_id = 0

        for sentence in sentences:
            sent_tokens = self._token_len(sentence)

            # if sentence alone is too large → hard cut
            if sent_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(
                        self._build_chunk(
                            chunk_id,
                            " ".join(current_chunk),
                            source,
                            page_number
                        )
                    )
                    chunk_id += 1
                    current_chunk = []
                    current_tokens = 0

                chunks.append(
                    self._build_chunk(
                        chunk_id,
                        sentence,
                        source,
                        page_number,
                        forced=True
                    )
                )
                chunk_id += 1
                continue

            # if adding sentence exceeds chunk size → finalize chunk
            if current_tokens + sent_tokens > self.chunk_size:
                chunks.append(
                    self._build_chunk(
                        chunk_id,
                        " ".join(current_chunk),
                        source,
                        page_number
                    )
                )
                chunk_id += 1

                # overlap via tail sentences
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + [sentence]
                current_tokens = self._token_len(" ".join(current_chunk))
            else:
                current_chunk.append(sentence)
                current_tokens += sent_tokens

        # flush remainder
        if current_chunk:
            chunks.append(
                self._build_chunk(
                    chunk_id,
                    " ".join(current_chunk),
                    source,
                    page_number
                )
            )

        return chunks

    # ---------- internals ----------

    def _get_overlap(self, sentences: List[str]) -> List[str]:
        """
        Carries over the last few sentences instead of raw tokens.
        """
        overlap = []
        tokens = 0

        for sent in reversed(sentences):
            sent_tokens = self._token_len(sent)
            if tokens + sent_tokens > self.chunk_overlap:
                break
            overlap.insert(0, sent)
            tokens += sent_tokens

        return overlap

    def _build_chunk(
        self,
        chunk_id: int,
        text: str,
        source: str,
        page_number: int | None,
        forced: bool = False
    ) -> Dict:
        return {
            "chunk_id": chunk_id,
            "text": text,
            "metadata": {
                "source": source,
                "page": page_number,
                "token_count": self._token_len(text),
                "forced_split": forced
            }
        }
