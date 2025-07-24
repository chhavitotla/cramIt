from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = Ollama(model="llama3")

QUESTION_PROMPT = """
You are a helpful AI tutor generating practice questions for students.

From the academic text below, create 5 to 10 open-ended practice questions. Vary the difficulty across:
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

prompt = PromptTemplate(input_variables=["chunk"], template=QUESTION_PROMPT)
question_chain = LLMChain(llm=llm, prompt=prompt)

def generate_questions_from_chunks(chunks):
    questions = []
    for chunk in chunks:
        result = question_chain.run(chunk=chunk)
        questions.append(result.strip())
    return questions