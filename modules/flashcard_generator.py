from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

FLASHCARD_PROMPT = """
You are a flashcard bot.

Create flashcard from the text below.

FORMAT:
Q: question
A: answer

TEXT:
{chunk}
"""

prompt = PromptTemplate.from_template(FLASHCARD_PROMPT)
flashcard_chain = prompt | llm

def generate_flashcards_from_chunks(chunks):
    flashcards = []

    for chunk in chunks:
        response = flashcard_chain.invoke({"chunk": chunk})
        text = response.content.strip().split("\n")

        question, answer = "", ""
        for line in text:
            if line.lower().startswith("q:"):
                question = line[2:].strip()
            elif line.lower().startswith("a:"):
                answer = line[2:].strip()

        if question and answer:
            flashcards.append({
                "question": question,
                "answer": answer
            })

    return flashcards
