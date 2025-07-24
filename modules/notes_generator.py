from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Set up the Ollama LLM
llm = Ollama(model="llama3")  # Make sure 'ollama run llama3' is active

# Prompt template for explanatory bullet-point notes
NOTES_PROMPT = """
You are a helpful AI study assistant named CramIt.

Read the academic text below and write clear, concise, and explanatory bullet-point notes.
Each point should summarize a key concept in simple language that helps a student understand the topic.
Avoid using question-answer format or just keywords. Make it informative and easy to revise from.

TEXT:
{chunk}

📌 Study Notes:
"""


prompt = PromptTemplate(input_variables=["chunk"], template=NOTES_PROMPT)

# Chain to generate notes from one chunk
notes_chain = LLMChain(llm=llm, prompt=prompt)

def generate_notes_from_chunks(chunks):
    notes = []
    for chunk in chunks:
        response = notes_chain.run(chunk=chunk)
        notes.append(response.strip())
    return notes