# modules/rag_evaluator.py

from typing import List, Dict
import numpy as np


class RAGEvaluator:
    """
    Evaluates RAG answer quality using retrieval grounding signals.
    This is NOT LLM-based judging — it's system-level evaluation.
    """

    def __init__(self, min_chunks: int = 2):
        self.min_chunks = min_chunks

    def evaluate(
        self,
        retrieved_chunks: List[Dict],
        answer: str
    ) -> Dict:
        """
        Returns a confidence score + diagnostics.
        """

        if not retrieved_chunks:
            return self._fail("No chunks retrieved")

        num_chunks = len(retrieved_chunks)

        avg_chunk_length = np.mean([
            len(chunk["text"].split())
            for chunk in retrieved_chunks
        ])

        source_diversity = len({
            chunk["metadata"].get("page", chunk["metadata"].get("source"))
            for chunk in retrieved_chunks
        })


        # Heuristic confidence score
        confidence = min(
            1.0,
            (num_chunks / self.min_chunks) * 0.4
            + (source_diversity / num_chunks) * 0.4
            + (avg_chunk_length / 200) * 0.2
        )

        return {
            "confidence_score": round(confidence, 2),
            "num_chunks_used": num_chunks,
            "source_diversity": source_diversity,
            "status": "pass" if confidence >= 0.6 else "weak"
        }

    def _fail(self, reason: str) -> Dict:
        return {
            "confidence_score": 0.0,
            "status": "fail",
            "reason": reason
        }
