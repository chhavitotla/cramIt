from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = Ollama(model="llama3")

FLASHCARD_PROMPT = """
You are a flashcard bot. Read the text below and extract **one** flashcard with the format:

Q: [Question here]
A: [Answer here]

Do not write anything else.

Text:
{chunk}
"""

prompt = PromptTemplate(input_variables=["chunk"], template=FLASHCARD_PROMPT)
flashcard_chain = LLMChain(llm=llm, prompt=prompt)

def generate_flashcards_from_chunks(chunks):
    flashcards = []
    for chunk in chunks:
        response = flashcard_chain.run(chunk=chunk)
        lines = response.strip().split("\n")
        question = ""
        answer = ""
        for line in lines:
            if line.strip().lower().startswith("q:"):
                question = line.replace("Q:", "").strip()
            elif line.strip().lower().startswith("a:"):
                answer = line.replace("A:", "").strip()
        if question and answer:
            flashcards.append({"question": question, "answer": answer})
    return flashcards