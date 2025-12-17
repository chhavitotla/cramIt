import streamlit as st
import requests

from modules.pdf_parser import PDFParser
from modules.chunking import TextChunker

from modules.notes_generator import generate_notes_from_chunks
from modules.flashcard_generator import generate_flashcards_from_chunks
from modules.question_generator import generate_questions_from_chunks

from modules.qa_engine import QAEngine


st.set_page_config(page_title="CramIt 📚", layout="wide")

# Backend URL
BACKEND_URL = "http://localhost:3000"  # Change to 3000

def login_user(email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",   # Updated
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code in (200, 201):
            try:
                return response.json()
            except ValueError:
                return {"error": f"Invalid JSON response: {response.text[:100]}"}
        else:
            return {"error": f"{response.status_code} - {response.text[:100]}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend on port 5000"}
    except Exception as e:
        return {"error": str(e)}


def register_user(email, password):
    try:
        print(f"Attempting to register: {email}")  # Debug
        response = requests.post(
            f"{BACKEND_URL}/register",   # Updated
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Response status: {response.status_code}")  # Debug
        print(f"Response text: {response.text}")  # Debug

        if response.status_code in (200, 201):
            try:
                return response.json()
            except ValueError:
                return {"error": f"Invalid JSON response: {response.text[:100]}"}
        else:
            return {"error": f"{response.status_code} - {response.text[:100]}"}

    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend on port 5000"}
    except Exception as e:
        return {"error": str(e)}

# Initialize auth state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None

# AUTH PAGE - Only shows if not logged in
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔐 Welcome to CramIt</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if login_email and login_password:
                result = login_user(login_email, login_password)
                if "message" in result:   # Updated: check for message
                    st.session_state.authenticated = True
                    st.session_state.user_token = result.get("email")  # store email as user identity
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result.get("error", "Login failed"))
    
    with tab2:
        st.subheader("Sign Up")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password (6+ chars)", type="password", key="reg_password")
        
        if st.button("Sign Up"):
            if reg_email and reg_password:
                result = register_user(reg_email, reg_password)
                if "message" in result:   # Updated: check for message
                    st.session_state.authenticated = True
                    st.session_state.user_token = result.get("email")  # store email as user identity
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result.get("error", "Registration failed"))

else:
    # LOGGED IN - Now show your actual CramIt app
    
    # Your existing CSS and imports (move these here)
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
    <style>
        html, body {
            font-family: 'American Typewriter', serif !important;
            color: #1E1E1E;
        }
        h1, h2, h3 {
            font-family: 'American Typewriter', serif !important;
            letter-spacing: 0.5px;
        }
        .accent {
            font-family: 'American Typewriter', serif !important;
            color: #FF5DA2;
        }
    </style>
    """, unsafe_allow_html=True)

    # Page settings
    st.set_page_config(page_title="CramIt 📚", layout="wide")

    # YOUR EXISTING SESSION STATE CODE
    if "chunks" not in st.session_state:
        st.session_state.chunks = []
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "saved_flashcards" not in st.session_state:
        st.session_state.saved_flashcards = []
    if "pdf_uploaded" not in st.session_state:
        st.session_state.pdf_uploaded = False

    # Add logout button to sidebar
    st.sidebar.title("👋 Welcome!")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_token = None
        # Clear all session data on logout
        for key in ['chunks', 'notes', 'flashcards', 'questions', 'saved_flashcards', 'pdf_uploaded']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # YOUR EXISTING SIDEBAR NAVIGATION
    st.sidebar.title("🧭 Navigate")
    page = st.sidebar.radio(
        "Choose a tool",
        ["🏠 Home", "📚 Notes", "🃏 Flashcards", "❓ Practice Questions", "💬 Ask Your PDF"],
        index=0
    )

    # ALL YOUR EXISTING PAGES - EXACTLY THE SAME
    if page == "🏠 Home":
        st.markdown("<h1 style='text-align: center;'>📚 CramIt</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Study like you meant to all along.</h3>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Forgot to study again?</h4>
                <p>Of course you did. Welcome back, legend.<br>No lectures. No judgment. Just vibes (and violence).</p>
                <p>🗂 Drop the PDF<br>📝 We'll turn it into notes, flashcards & "pls just help me" questions<br>🧠 Ask stuff like you paid attention all semester<br>🔥 Cram now, cry later</p>
                <p><em>This isn't studying.<br>It's survival.</em></p>
                <p>You bring the chaos.<br><strong>We'll make it look like a plan.</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 🗂️ File upload section
        uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"], label_visibility="collapsed")

        # 🧠 Submit button
        if uploaded_file is not None:
            if st.button("Let's Cram 🧃"):
                # Store file
                st.session_state["uploaded_file"] = uploaded_file

        # Initialize parser & chunker once
        if "pdf_parser" not in st.session_state:
            st.session_state.pdf_parser = PDFParser()

        if "text_chunker" not in st.session_state:
            st.session_state.text_chunker = TextChunker()

        with st.spinner("Reading and chunking your chaotic masterpiece..."):
            # Read PDF bytes
            pdf_bytes = uploaded_file.read()

            # Parse PDF → pages
            pages = st.session_state.pdf_parser.parse(
                pdf_bytes=pdf_bytes,
                source_name=uploaded_file.name
            )

            # Chunk pages
            chunks = st.session_state.text_chunker.chunk(pages)

        # Store results
        st.session_state.chunks = chunks
        st.session_state.pdf_uploaded = True

        st.success("✅ PDF uploaded and processed! Now go hit Notes, Flashcards, or Questions.")

    # -------------------- NOTES --------------------
    elif page == "📚 Notes":
        st.title("📝 Notes Generator")
        if not st.session_state.pdf_uploaded:
            st.warning("🗂️ Please upload a PDF first from the Home page.")
        else:
            if st.button("🧠 Generate Notes"):
                with st.spinner("Generating notes..."):
                    notes = generate_notes_from_chunks(st.session_state.chunks)
                st.session_state.notes = notes
                st.success("✅ Notes generated!")

            if st.session_state.notes:
                st.subheader("📚 AI-Generated Study Notes")
                for i, note in enumerate(st.session_state.notes[:5]):
                    with st.expander(f"🧠 Notes for Chunk {i+1}"):
                        st.markdown(note)

    # -------------------- FLASHCARDS --------------------
    elif page == "🃏 Flashcards":
        st.title("🃏 Flashcard Generator")
        
        if not st.session_state.pdf_uploaded:
            st.warning("🗂️ Please upload a PDF first from the Home page.")
        else:
            # Generate flashcards button
            if st.button("🎴 Generate Flashcards"):
                with st.spinner("Writing flashcards..."):
                    flashcards = generate_flashcards_from_chunks(st.session_state.chunks)
                    st.session_state.flashcards = flashcards
                st.success("✅ Flashcards ready!")

            # Display flashcards
            if st.session_state.flashcards:
                st.subheader("📚 Your Flashcards")
                
                for i, card in enumerate(st.session_state.flashcards):
                    question = card["question"]
                    answer = card["answer"]

                    st.markdown(
                        f"""
                        <div class="flashcard">
                            <p><strong>Q{i+1}: {question}</strong></p>
                            <p>💡 {answer}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Save button
                if st.button("💾 Save to My Memory"):
                    st.session_state.saved_flashcards.extend(st.session_state.flashcards)
                    st.success("✅ Flashcards saved to your memory!")

    # -------------------- QUESTIONS --------------------
    elif page == "❓ Practice Questions":
        st.title("❓ Practice Questions")
        if not st.session_state.pdf_uploaded:
            st.warning("🗂️ Please upload a PDF first from the Home page.")
        else:
            if st.button("🧪 Generate Questions"):
                with st.spinner("Thinking up some brain-busters..."):
                    questions = generate_questions_from_chunks(st.session_state.chunks)
                st.session_state.questions = questions
                st.success("✅ Questions generated!")

            if st.session_state.questions:
                st.subheader("🧠 Practice Questions")
                for i, q in enumerate(st.session_state.questions):
                    st.markdown(f"**Q{i+1}:** {q}")

    # -------------------- ASK YOUR PDF --------------------
    elif page == "💬 Ask Your PDF":
        st.title("💬 Ask Your PDF")

    if not st.session_state.pdf_uploaded:
        st.warning("🗂️ Please upload a PDF first from the Home page.")
    else:
        # Initialize QAEngine once
        if "qa_engine" not in st.session_state:
            st.session_state.qa_engine = QAEngine()

        user_question = st.text_input("Ask something from your PDF:")

        if user_question:
            with st.spinner("Thinking real hard..."):
                result = st.session_state.qa_engine.ask(user_question)

            # Answer
            st.markdown(f"### 📌 Answer")
            st.write(result.get("answer", "No answer generated."))

            # RAG Confidence (🔥 WOW factor)
            rag_conf = result.get("rag_confidence", 0.0)
            status = result.get("status", "unknown")

            if status == "pass":
                st.success(f"🧠 RAG Confidence: **{rag_conf}** — Well grounded")
            elif status == "weak":
                st.warning(f"⚠️ RAG Confidence: **{rag_conf}** — Partial grounding")
            else:
                st.error("❌ Answer not grounded in document")

            # Sources
            sources = result.get("sources", [])
            if sources:
                with st.expander("📚 View Source Evidence"):
                    for i, src in enumerate(sources, 1):
                        st.markdown(f"**Source {i}:** {src}")
