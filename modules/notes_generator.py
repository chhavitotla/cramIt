from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os

# ---------------------------
# Gemini LLM
# ---------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

# ---------------------------
# Prompt
# ---------------------------
NOTES_PROMPT = """
You are a helpful AI study assistant named CramIt.

Read the academic text below and write clear, concise, and explanatory bullet-point notes.
Each point should summarize a key concept in simple language that helps a student understand the topic.
Avoid using question-answer format or just keywords. Make it informative and easy to revise from.

TEXT:
{chunk}

📌 Study Notes:
"""

prompt = PromptTemplate(
    input_variables=["chunk"],
    template=NOTES_PROMPT,
)

# ---------------------------
# Runnable Chain (LangChain 1.x)
# ---------------------------
notes_chain = prompt | llm


# ---------------------------
# Public API
# ---------------------------
def generate_notes_from_chunks(chunks):
    """
    Generates bullet-point study notes from text chunks.
    """
    notes = []

    for chunk in chunks:
        response = notes_chain.invoke({"chunk": chunk})
        notes.append(response.content.strip())

    return notes
