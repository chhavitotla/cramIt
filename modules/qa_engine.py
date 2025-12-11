from langchain.vectorstores import FAISS  # Vector store for retrieval
from langchain.embeddings import OllamaEmbeddings  # To embed text chunks
from langchain.chains import RetrievalQA  # Chain combining retrieval + LLM
from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain.docstore.document import Document  # Wrap chunks as documents
from langchain.prompts import PromptTemplate  # Custom prompt for the LLM

#  Load embedder and LLM
embedding_model = OllamaEmbeddings(model="llama3")  # Generates vector embeddings
llm = Ollama(model="llama3")  # LLM that answers questions

#  Custom prompt template for the QA engine
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    You are a helpful assistant answering questions based on the provided PDF content.
    Only use the context below to answer the question accurately and concisely.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
)

def build_qa_engine(chunks):
    #  Wrap each text chunk as a LangChain Document
    docs = [Document(page_content=chunk) for chunk in chunks]

    #  Embed documents and store in FAISS vector DB
    vectorstore = FAISS.from_documents(docs, embedding_model)

    #  Create retriever to fetch relevant chunks using vector similarity
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    #  Build Retrieval-Augmented Generation (RAG) chain:
    #     - Retrieves top 3 relevant chunks from retriever
    #     - Sends them + the question to the LLM using a custom prompt
    #     - LLM generates a final answer
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": custom_prompt},
        return_source_documents=True
    )

    return qa_chain