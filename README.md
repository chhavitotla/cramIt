# 🎓 CramIt – Gen Z AI Study Assistant

CramIt is a quirky, AI-powered study assistant that transforms academic PDFs into study notes, flashcards, and answers using local LLMs. It's built with Python, Streamlit, LangChain, and Ollama, and designed with a fun, Gen Z-friendly aesthetic.

---

## 🚀 Features

- 📝 Bullet-point Study Notes from academic PDFs
- 🃏 Flashcard Generation for active recall
- ❓ RAG-based Question Answering using local LLMs (via Ollama)
- 🎨 Stylish UI with custom pastel themes and typewriter fonts
- ⚡ In-memory processing – no file saves, no data stored

---

## 🧠 Tech Stack

- **Frontend**: Streamlit
- **LLM Framework**: LangChain
- **PDF Parsing**: PyMuPDF (`pymupdf`)
- **Vector Store**: ChromaDB
- **Tokenization**: `tiktoken`
- **Local LLMs**: Ollama (e.g., LLaMA 3, Mistral)

---

## 🗂️ Project Structure

CramIt/
├── app.py                  # Main Streamlit app
├── modules/                # All processing logic
│   ├── chunking.py
│   ├── flashcard_generator.py
│   ├── notes_generator.py
│   ├── pdf_parser.py
│   ├── qa_engine.py
│   └── question_generator.py
├── styles/                 # UI styling
│   ├── fonts.css
│   └── theme.css
├── .streamlit/             # Streamlit theme config
│   └── config.toml
├── .env                    # Local environment variables (not committed)
├── .gitignore              # Ignore cache/env files
├── requirements.txt        # Python dependencies
└── README.md               # This file