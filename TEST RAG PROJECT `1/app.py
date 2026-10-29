
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from streamlit.errors import StreamlitSecretNotFoundError

from pdf_reader import read_pdf
from embeddings import make_chunks, get_embeddings
from rag import search
from paper_generator import generate_paper

load_dotenv()

st.set_page_config(
    page_title="AI Test Paper Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Test Paper Generator")
st.caption(
    "Generate practice papers from PDF books and custom topics "
    "using OpenRouter AI."
)

api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
if not api_key:
    try:
        api_key = str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
    except StreamlitSecretNotFoundError:
        pass

model = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4.1-mini"
).strip()
embedding_model = os.getenv(
    "OPENROUTER_EMBEDDING_MODEL",
    "openai/text-embedding-3-small"
).strip()

if not api_key:
    st.error(
        "OPENROUTER_API_KEY missing. "
        "Set it in the .env file or Streamlit secrets."
    )
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

st.sidebar.header("Paper Settings")

board = st.sidebar.selectbox(
    "Board",
    [
        "Sindh Board / Karachi Board",
        "Federal Board",
        "Punjab Board",
        "Other / Custom"
    ]
)

class_name = st.sidebar.selectbox(
    "Class",
    [
        "Class 9",
        "Class 10",
        "Class 11 (First Year)",
        "Class 12 (Second Year)",
        "Other"
    ]
)

if class_name == "Other":
    class_name = st.sidebar.text_input(
        "Enter class or level",
        "Other class"
    )

subject = st.sidebar.text_input(
    "Subject",
    "Biology"
)

language = st.sidebar.selectbox(
    "Paper Language",
    ["English", "Urdu", "Roman Urdu"]
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Balanced", "Easy", "Medium", "Difficult"]
)

total_marks = st.sidebar.number_input(
    "Target Total Marks",
    min_value=10,
    max_value=300,
    value=50,
    step=5
)

duration = st.sidebar.number_input(
    "Duration (minutes)",
    min_value=15,
    max_value=360,
    value=120,
    step=15
)

st.sidebar.subheader("MCQs")

mcq_count = st.sidebar.number_input(
    "Number of MCQs",
    min_value=0,
    max_value=100,
    value=10
)

mcq_marks = st.sidebar.number_input(
    "Marks per MCQ",
    min_value=1,
    max_value=5,
    value=1
)

st.sidebar.subheader("Short Questions")

short_count = st.sidebar.number_input(
    "Short Questions to Include",
    min_value=0,
    max_value=60,
    value=8
)

short_attempt = st.sidebar.number_input(
    "Short Questions to Attempt",
    min_value=0,
    max_value=60,
    value=5
)

short_marks = st.sidebar.number_input(
    "Marks per Short Question",
    min_value=1,
    max_value=20,
    value=2
)

st.sidebar.subheader("Long Questions")

long_count = st.sidebar.number_input(
    "Long Questions to Include",
    min_value=0,
    max_value=30,
    value=4
)

long_attempt = st.sidebar.number_input(
    "Long Questions to Attempt",
    min_value=0,
    max_value=30,
    value=2
)

long_marks = st.sidebar.number_input(
    "Marks per Long Question",
    min_value=1,
    max_value=30,
    value=5
)

uploaded_file = st.file_uploader(
    "Upload textbook, notes or syllabus PDF",
    type=["pdf"]
)

topics = st.text_area(
    "Additional Topics / Chapters",
    placeholder=(
        "Example: Cell structure, photosynthesis, "
        "genetics and important definitions."
    )
)

instructions = st.text_area(
    "Custom Instructions",
    placeholder=(
        "Example: Focus on Chapters 2 and 3. "
        "Include conceptual questions and numericals."
    )
)

include_key = st.checkbox(
    "Generate separate answer key",
    value=True
)

show_context = st.checkbox(
    "Show retrieved PDF content",
    value=False
)

if st.button(
    "✨ Generate Complete Test Paper",
    type="primary",
    use_container_width=True
):
    if not subject.strip():
        st.error("Please enter a subject.")

    elif not uploaded_file and not topics.strip():
        st.error(
            "Please upload a PDF or enter additional topics."
        )

    elif short_attempt > short_count:
        st.error(
            "Short questions to attempt cannot exceed "
            "the number included."
        )

    elif long_attempt > long_count:
        st.error(
            "Long questions to attempt cannot exceed "
            "the number included."
        )

    elif mcq_count + short_count + long_count == 0:
        st.error("Please select at least one question type.")

    else:
        try:
            pdf_text = ""
            context = ""

            if uploaded_file:
                with st.spinner("Reading your PDF..."):
                    pdf_text = read_pdf(uploaded_file)

                if not pdf_text.strip():
                    st.error(
                        "No readable text found. "
                        "Scanned PDFs need OCR first."
                    )
                    st.stop()

                chunks = make_chunks(pdf_text)

                if chunks:
                    with st.spinner(
                        "Creating embeddings and searching PDF..."
                    ):
                        embeddings = get_embeddings(
                            client,
                            chunks,
                            embedding_model
                        )

                        query = (
                            f"Board: {board}\n"
                            f"Class: {class_name}\n"
                            f"Subject: {subject}\n"
                            f"Topics: {topics}\n"
                            f"Instructions: {instructions}"
                        )

                        relevant_chunks = search(
                            query,
                            chunks,
                            embeddings,
                            client,
                            embedding_model,
                            top_k=8
                        )

                        context = "\n\n".join(
                            relevant_chunks
                        )

            settings = {
                "board": board,
                "class_name": class_name,
                "subject": subject.strip(),
                "language": language,
                "difficulty": difficulty,
                "total_marks": int(total_marks),
                "duration": int(duration),
                "mcq_count": int(mcq_count),
                "mcq_marks": int(mcq_marks),
                "short_count": int(short_count),
                "short_attempt": int(short_attempt),
                "short_marks": int(short_marks),
                "long_count": int(long_count),
                "long_attempt": int(long_attempt),
                "long_marks": int(long_marks),
                "topics": topics.strip(),
                "instructions": instructions.strip(),
                "include_key": include_key
            }

            with st.spinner(
                "AI is generating your complete paper..."
            ):
                paper, answer_key = generate_paper(
                    client,
                    model,
                    settings,
                    context
                )

            st.session_state["paper"] = paper
            st.session_state["answer_key"] = answer_key
            st.session_state["include_key"] = include_key
            st.session_state["pdf_context"] = context

            st.success("Your practice paper is ready!")

        except Exception as error:
            st.error(f"Generation failed: {error}")
            st.info(
                "Check your OpenRouter key, model IDs, "
                "API credits and internet connection. "
                "Also verify that your selected embedding "
                "model supports the embeddings endpoint."
            )

if "paper" in st.session_state:
    tab1, tab2 = st.tabs(
        ["📝 Question Paper", "🔑 Answer Key"]
    )

    with tab1:
        st.markdown(st.session_state["paper"])

        st.download_button(
            "Download Question Paper",
            data=st.session_state["paper"],
            file_name="question_paper.md",
            mime="text/markdown"
        )

    with tab2:
        if st.session_state.get("include_key", False):
            st.markdown(
                st.session_state.get("answer_key", "")
            )

            st.download_button(
                "Download Answer Key",
                data=st.session_state.get("answer_key", ""),
                file_name="answer_key.md",
                mime="text/markdown"
            )
        else:
            st.info("Answer key generation was disabled.")

    if show_context and st.session_state.get("pdf_context"):
        with st.expander("View retrieved PDF content"):
            st.text(st.session_state["pdf_context"])
