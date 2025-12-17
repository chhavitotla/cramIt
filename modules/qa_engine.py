import os
from typing import List, Dict

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from langchain_chroma import Chroma

from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough

from modules.rag_evaluator import RAGEvaluator
class QAEngine:
    """
    Production-grade RAG Question Answering Engine using:
    - Gemini (LLM)
    - ChromaDB (vector store)
    - MMR retrieval
    - System-level RAG evaluation
    """

    def __init__(self, persist_dir: str = "chroma_db"):
        try:
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found")

            # LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.2,
                google_api_key=self.api_key,
            )

            # Embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self.api_key,
            )

            # Vector store
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
            )

            # Retriever (MMR)
            self.retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 6,
                    "fetch_k": 20,
                    "lambda_mult": 0.7,
                },
            )

            self.qa_chain = self._build_qa_chain()

            # RAG evaluator
            self.evaluator = RAGEvaluator(min_chunks=2)

        except Exception as e:
            raise RuntimeError(f"[QAEngine Init Error] {str(e)}")

    def _build_qa_chain(self):
        """
        Pure LCEL-based RAG chain (2025 safe)
        """

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an academic assistant.

Answer the question ONLY using the context below.
If the answer is not present in the context, say:
"I could not find this information in the provided document."

Context:
{context}

Question:
{question}

Answer (clear, concise, grounded):
""",
        )

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
        )

        return chain

    def ask(self, question: str) -> Dict:
        """
        Ask a question over the document corpus.
        """

        if not question or not question.strip():
            return {
                "answer": "Please provide a valid question.",
                "sources": [],
                "rag_confidence": 0.0,
                "status": "fail",
            }

        try:
            llm_response = self.qa_chain.invoke(question)
            answer = llm_response.content.strip()

            # retrieve docs separately for evaluator + sources
            source_docs: List[Document] = self.retriever.invoke(question)

            sources = self._extract_sources(source_docs)

            retrieved_chunks = [
                {"text": doc.page_content, "metadata": doc.metadata}
                for doc in source_docs
            ]

            eval_result = self.evaluator.evaluate(
                retrieved_chunks=retrieved_chunks,
                answer=answer,
            )

            return {
                "answer": answer,
                "sources": sources,
                "rag_confidence": eval_result.get("confidence_score", 0.0),
                "status": eval_result.get("status", "fail"),
            }

        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "rag_confidence": 0.0,
                "status": "fail",
            }

    @staticmethod
    def _extract_sources(docs: List[Document]) -> List[str]:
        """
        Extract readable source snippets for UI display
        """
        sources = []
        for doc in docs:
            text = doc.page_content.strip()
            if text:
                sources.append(text[:300] + "...")
        return sources
