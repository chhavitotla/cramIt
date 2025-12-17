import os
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
# LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.4,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

QUESTION_PROMPT = """
You are a helpful AI tutor generating practice questions for students.

From the academic text below, create 5 to 10 open-ended practice questions.
Vary the difficulty across:
- Knowledge (recall facts)
- Application (real-world use)
- Analysis (deep thinking)

TEXT:
{chunk}

FORMAT:
1. [Knowledge] ...
2. [Application] ...
3. [Analysis] ...
"""

prompt = PromptTemplate(
    input_variables=["chunk"],
    template=QUESTION_PROMPT,
)

question_chain = prompt | llm | StrOutputParser()


def generate_questions_from_chunks(chunks: List[str]) -> List[str]:
    questions = []

    for chunk in chunks:
        result = question_chain.invoke({"chunk": chunk})
        questions.append(result.strip())

    return questions
