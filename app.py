import re
import streamlit as st

# =========================================================
# PDF IMPORT
# =========================================================

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# =========================================================
# YOUR BACKEND
# IMPORTANT:
# Your file is parallel.py
# NOT parallel_chain.py
# =========================================================

from parallel import (
    generate_study_material,
    chat_with_memory
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BrainBot | AI Study Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ==============================================
       MAIN APP
    ============================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 5% 5%,
                rgba(37, 99, 235, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 95% 5%,
                rgba(124, 58, 237, 0.22),
                transparent 30%
            ),
            #020617;
        color: #f8fafc;
    }


    /* ==============================================
       MAIN CONTAINER
    ============================================== */

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* ==============================================
       SIDEBAR
    ============================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #020617 0%,
                #030712 100%
            );

        border-right:
            1px solid rgba(148, 163, 184, 0.12);
    }


    /* ==============================================
       HEADINGS
    ============================================== */

    h1,
    h2,
    h3 {
        color: #f8fafc !important;
    }


    /* ==============================================
       BRAINBOT TITLE
    ============================================== */

    .brainbot-title {
        text-align: center;
        font-size: 58px;
        font-weight: 900;
        letter-spacing: -2px;

        background:
            linear-gradient(
                90deg,
                #38bdf8,
                #818cf8,
                #c084fc,
                #22d3ee
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        margin-top: 10px;
        margin-bottom: 5px;
    }


    .brainbot-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 35px;
    }


    /* ==============================================
       CARDS
    ============================================== */

    .brainbot-card {
        padding: 25px;

        border-radius: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.95),
                rgba(30, 41, 59, 0.75)
            );

        border:
            1px solid rgba(129, 140, 248, 0.20);

        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.20);

        margin-bottom: 20px;
    }


    /* ==============================================
       TEXT AREA
    ============================================== */

    textarea {
        background:
            rgba(2, 6, 23, 0.90) !important;

        color:
            #f8fafc !important;

        border:
            1px solid rgba(129, 140, 248, 0.30)
            !important;

        border-radius:
            18px !important;

        font-size:
            16px !important;

        line-height:
            1.7 !important;
    }


    textarea:focus {
        border-color:
            #818cf8 !important;

        box-shadow:
            0 0 0 3px rgba(129, 140, 248, 0.12),
            0 0 30px rgba(99, 102, 241, 0.12)
            !important;
    }


    /* ==============================================
       BUTTONS
    ============================================== */

    .stButton > button {
        border-radius:
            14px !important;

        min-height:
            45px;

        font-weight:
            700 !important;

        border:
            1px solid
            rgba(129, 140, 248, 0.22)
            !important;

        background:
            rgba(15, 23, 42, 0.90)
            !important;

        color:
            #f8fafc !important;

        transition:
            all 0.2s ease;
    }


    .stButton > button:hover {
        transform:
            translateY(-2px);

        border-color:
            rgba(129, 140, 248, 0.65)
            !important;

        box-shadow:
            0 10px 30px
            rgba(99, 102, 241, 0.20);
    }


    /* ==============================================
       PRIMARY BUTTON
    ============================================== */

    button[kind="primary"] {
        background:
            linear-gradient(
                90deg,
                #2563eb,
                #7c3aed,
                #9333ea
            ) !important;

        border:
            none !important;

        box-shadow:
            0 10px 35px
            rgba(124, 58, 237, 0.30);
    }


    /* ==============================================
       METRICS
    ============================================== */

    [data-testid="stMetric"] {
        background:
            rgba(15, 23, 42, 0.70);

        border:
            1px solid
            rgba(148, 163, 184, 0.12);

        padding:
            18px !important;

        border-radius:
            18px !important;
    }


    /* ==============================================
       FILE UPLOADER
    ============================================== */

    [data-testid="stFileUploader"] {
        background:
            rgba(15, 23, 42, 0.65);

        border-radius:
            18px;

        padding:
            10px;
    }


    /* ==============================================
       EXPANDERS
    ============================================== */

    [data-testid="stExpander"] {
        border:
            1px solid
            rgba(129, 140, 248, 0.18)
            !important;

        border-radius:
            16px !important;

        background:
            rgba(15, 23, 42, 0.60)
            !important;
    }


    /* ==============================================
       CHAT
    ============================================== */

    [data-testid="stChatMessage"] {
        border-radius:
            18px;

        margin-bottom:
            10px;

        border:
            1px solid
            rgba(148, 163, 184, 0.10);
    }


    /* ==============================================
       FOOTER
    ============================================== */

    .footer-text {
        text-align: center;
        color: #64748b;
        padding: 30px 0 10px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "study_material" not in st.session_state:
    st.session_state.study_material = ""

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = ""

if "final" not in st.session_state:
    st.session_state.final = ""

if "generated" not in st.session_state:
    st.session_state.generated = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "generation_mode" not in st.session_state:
    st.session_state.generation_mode = ""

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""

if "material_input" not in st.session_state:
    st.session_state.material_input = ""


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(uploaded_file):

    if PdfReader is None:

        st.error(
            "pypdf is not installed."
        )

        st.code(
            "pip install pypdf"
        )

        return ""

    try:

        reader = PdfReader(uploaded_file)

        pages = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                pages.append(page_text)

        extracted_text = "\n\n".join(pages)

        return extracted_text.strip()

    except Exception as e:

        st.error(
            f"PDF extraction failed: {e}"
        )

        return ""


# =========================================================
# QUIZ PARSER
# =========================================================

def parse_quiz(quiz_text):
    """
    Parse quiz output in formats such as:

    1. Question
    Answer: Answer

    2. Question
    Answer: Answer

    Also accepts:
    Q1. Question
    Question 1. Question
    """

    if not quiz_text or not quiz_text.strip():
        return []

    # Accept:
    # 1. Question
    # 1) Question
    # 1: Question
    # Q1. Question
    # Question 1. Question
    #
    # The question number is captured so that the following
    # question can be detected reliably.
    pattern = (
        r"(?im)"
        r"^\s*"
        r"(?:Q(?:uestion)?\s*)?"
        r"(\d+)"
        r"\s*[\.\):\-]\s*"
    )

    parts = re.split(pattern, quiz_text)

    questions = []

    # re.split() produces:
    # [text_before, number, content, number, content, ...]
    index = 1

    while index + 1 < len(parts):

        content = parts[index + 1].strip()

        if not content:
            index += 2
            continue

        # Find the answer marker.
        answer_match = re.search(
            r"(?is)"
            r"(?:^|\n)\s*"
            r"(?:Answer|Ans)"
            r"\s*:\s*"
            r"(.*)",
            content
        )

        if answer_match:
            question_text = content[:answer_match.start()].strip()
            answer_text = answer_match.group(1).strip()
        else:
            question_text = content
            answer_text = ""

        # Remove accidental markdown heading markers if the model adds them.
        question_text = re.sub(
            r"^\s*#+\s*",
            "",
            question_text
        ).strip()

        if question_text:
            questions.append(
                {
                    "number": len(questions) + 1,
                    "question": question_text,
                    "answer": answer_text
                }
            )

        index += 2

    return questions


# =========================================================
# SHOW QUIZ
# =========================================================

def show_quiz(
    quiz_text,
    requested_count
):

    questions = parse_quiz(
        quiz_text
    )

    actual_count = len(
        questions
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🎯 Requested",
            requested_count
        )

    with col2:

        st.metric(
            "🧠 Generated",
            actual_count
        )

    with col3:

        if actual_count == requested_count:

            st.metric(
                "✅ Status",
                "Exact"
            )

        elif actual_count < requested_count:

            st.metric(
                "⚠️ Status",
                "Incomplete"
            )

        else:

            st.metric(
                "⚠️ Status",
                "Too Many"
            )

    st.write("")

    if actual_count < requested_count:

        st.warning(
            f"BrainBot generated "
            f"{actual_count} questions, "
            f"but you requested "
            f"{requested_count}."
        )

    elif actual_count > requested_count:

        st.info(
            f"BrainBot generated "
            f"{actual_count} questions. "
            f"Requested: {requested_count}."
        )

    if not questions:

        st.error(
            "No quiz questions could be detected."
        )

        st.markdown(
            quiz_text
        )

        return

    st.success(
        f"🧠 Quiz ready — "
        f"{actual_count} questions generated."
    )

    st.write("")

    for item in questions:

        question_title = (
            f"🧠 Question "
            f"{item['number']}"
        )

        with st.expander(
            question_title,
            expanded=False
        ):

            st.markdown(
                f"### Question "
                f"{item['number']}"
            )

            st.markdown(
                item["question"]
            )

            if item["answer"]:

                st.divider()

                st.markdown(
                    "### 💡 Answer"
                )

                st.success(
                    item["answer"]
                )

            else:

                st.info(
                    "No separate answer "
                    "was detected."
                )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="brainbot-title">'
    '🧠 BrainBot'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brainbot-subtitle">'
    'Think • Learn • Practice • Master'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "📚 AI Study Assistant • "
    "PDF → Notes → Quiz → Chat"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "⚙️ BrainBot Settings"
    )

    st.divider()

    # -----------------------------------------------------
    # QUIZ SETTINGS
    # -----------------------------------------------------

    st.subheader(
        "🎯 Quiz Settings"
    )

    num_questions = st.slider(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=10,
        step=1
    )

    st.caption(
        f"🎯 BrainBot will try to "
        f"generate exactly "
        f"**{num_questions} questions.**"
    )

    st.divider()

    # -----------------------------------------------------
    # STUDY MODE
    # -----------------------------------------------------

    st.subheader(
        "🚀 Study Mode"
    )

    study_mode = st.radio(
        "Choose what to generate",
        [
            "📖 Study Notes",
            "🧠 Quiz Mode",
            "🚀 Complete Study Pack"
        ],
        index=2
    )

    st.divider()

    # -----------------------------------------------------
    # CHAT MEMORY
    # -----------------------------------------------------

    st.subheader(
        "🧠 Chat Memory"
    )

    st.metric(
        "Messages",
        len(
            st.session_state.chat_history
        )
    )

    if st.button(
        "🗑️ Clear Chat Memory",
        use_container_width=True
    ):

        st.session_state.chat_history = []

        st.success(
            "Chat memory cleared!"
        )

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # PRO TIPS
    # -----------------------------------------------------

    st.subheader(
        "💡 Pro Tips"
    )

    st.info(
        """
        📄 Upload a PDF

        📝 Paste your notes

        📖 Generate smart notes

        🧠 Create a quiz

        💬 Ask follow-up questions

        🚀 Use Complete Study Pack
        """
    )

    st.divider()

    st.caption(
        "BrainBot • AI Study Assistant"
    )


# =========================================================
# MAIN INPUT
# =========================================================

st.header(
    "📚 Feed BrainBot Your Knowledge"
)

st.write(
    "Upload a PDF or paste your study "
    "material below."
)


# =========================================================
# PDF UPLOAD
# =========================================================

st.subheader(
    "📄 Upload PDF"
)

uploaded_file = st.file_uploader(
    "Choose your PDF",
    type=["pdf"],
    help=(
        "BrainBot automatically extracts "
        "text from your PDF."
    )
)


if uploaded_file is not None:

    if (
        st.session_state.uploaded_file_name
        != uploaded_file.name
    ):

        with st.spinner(
            "📖 Extracting PDF text..."
        ):

            pdf_text = extract_pdf_text(
                uploaded_file
            )

        if pdf_text:

            st.session_state.study_material = (
                pdf_text
            )

            st.session_state.material_input = (
                pdf_text
            )

            st.session_state.uploaded_file_name = (
                uploaded_file.name
            )

            st.success(
                f"✅ PDF loaded: "
                f"{uploaded_file.name}"
            )

            st.info(
                f"📄 Extracted "
                f"approximately "
                f"**{len(pdf_text.split())} words**."
            )

        else:

            st.warning(
                "No readable text was found "
                "inside this PDF."
            )

            st.caption(
                "Scanned/image-only PDFs require OCR."
            )


# =========================================================
# TEXT INPUT
# =========================================================

st.subheader(
    "📝 Or Paste Study Material"
)

material_input = st.text_area(
    "Study Material",
    key="material_input",
    height=280,
    placeholder=(
        "Paste your chapter, lecture notes, "
        "documentation, article or study "
        "material here..."
    ),
    label_visibility="collapsed"
)


# Keep session state synchronized
if material_input.strip():

    st.session_state.study_material = (
        material_input
    )


# =========================================================
# MATERIAL INFORMATION
# =========================================================

material = (
    st.session_state.study_material
)

word_count = (
    len(material.split())
    if material.strip()
    else 0
)

character_count = len(
    material
)

st.write("")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📝 Words",
        word_count
    )

with col2:

    st.metric(
        "🔤 Characters",
        character_count
    )

with col3:

    st.metric(
        "🎯 Quiz Size",
        num_questions
    )

with col4:

    source = (
        "PDF"
        if st.session_state.uploaded_file_name
        else "Text"
    )

    st.metric(
        "📄 Source",
        source
    )


# =========================================================
# QUICK ACTIONS
# =========================================================

st.subheader(
    "⚡ Quick Actions"
)

quick1, quick2, quick3 = st.columns(3)


# ---------------------------------------------------------
# LOAD EXAMPLE
# ---------------------------------------------------------

with quick1:

    if st.button(
        "✨ Load Example",
        use_container_width=True
    ):

        example_text = """
Newton's Third Law of Motion states that
for every action there is an equal and
opposite reaction.

When object A exerts a force on object B,
object B simultaneously exerts a force
of equal magnitude and opposite direction
on object A.

These forces act on different objects,
so they do not cancel each other.

Examples include walking, swimming,
jumping, rocket propulsion and recoil.
"""

        st.session_state.study_material = (
            example_text.strip()
        )

        st.session_state.material_input = (
            example_text.strip()
        )

        st.session_state.uploaded_file_name = ""

        st.success(
            "✨ Example loaded!"
        )

        st.rerun()


# ---------------------------------------------------------
# CLEAR MATERIAL
# ---------------------------------------------------------

with quick2:

    if st.button(
        "🧹 Clear Material",
        use_container_width=True
    ):

        st.session_state.study_material = ""

        st.session_state.material_input = ""

        st.session_state.uploaded_file_name = ""

        st.session_state.notes = ""

        st.session_state.quiz = ""

        st.session_state.final = ""

        st.session_state.generated = False

        st.rerun()


# ---------------------------------------------------------
# SOURCE INFORMATION
# ---------------------------------------------------------

with quick3:

    if (
        st.session_state.uploaded_file_name
    ):

        st.success(
            "📄 PDF loaded"
        )

    else:

        st.info(
            "💡 Paste text or upload PDF"
        )


# =========================================================
# GENERATE
# =========================================================

st.write("")

if st.button(
    "🚀 CREATE MY STUDY EXPERIENCE",
    type="primary",
    use_container_width=True
):

    material = (
        st.session_state.study_material
    )

    if not material.strip():

        st.warning(
            "⚠️ Please upload a PDF "
            "or paste study material first."
        )

    else:

        with st.status(
            "🧠 BrainBot is working...",
            expanded=True
        ) as status:

            try:

                st.write(
                    "📚 Reading study material..."
                )

                st.write(
                    "🧠 Generating smart notes..."
                )

                st.write(
                    f"🎯 Generating "
                    f"{num_questions} quiz questions..."
                )

                st.write(
                    "✨ Building study experience..."
                )

                result = (
                    generate_study_material(
                        material,
                        num_questions
                    )
                )

                if not isinstance(
                    result,
                    dict
                ):

                    raise ValueError(
                        "parallel.py must return "
                        "a dictionary containing "
                        "notes, quiz and final."
                    )

                st.session_state.notes = (
                    result.get(
                        "notes",
                        ""
                    )
                )

                st.session_state.quiz = (
                    result.get(
                        "quiz",
                        ""
                    )
                )

                st.session_state.final = (
                    result.get(
                        "final",
                        ""
                    )
                )

                st.session_state.generated = True

                st.session_state.generation_mode = (
                    study_mode
                )

                status.update(
                    label="🎉 BrainBot finished!",
                    state="complete",
                    expanded=False
                )

            except Exception as e:

                status.update(
                    label="❌ Generation failed",
                    state="error",
                    expanded=True
                )

                st.error(
                    str(e)
                )

                st.exception(e)


# =========================================================
# RESULTS
# =========================================================

if st.session_state.generated:

    st.divider()

    st.header(
        "✨ Your BrainBot Learning Space"
    )

    st.caption(
        "Your material has been transformed "
        "into an interactive study experience."
    )

    result_tabs = st.tabs(
        [
            "📖 Smart Notes",
            "🧠 Interactive Quiz",
            "🚀 Complete Study Pack"
        ]
    )


    # =====================================================
    # SMART NOTES
    # =====================================================

    with result_tabs[0]:

        st.subheader(
            "📖 Smart Notes"
        )

        st.caption(
            "Clean explanations generated "
            "from your study material."
        )

        if (
            st.session_state.notes.strip()
        ):

            st.markdown(
                st.session_state.notes
            )

        else:

            st.info(
                "No notes were generated."
            )


    # =====================================================
    # QUIZ
    # =====================================================

    with result_tabs[1]:

        st.subheader(
            "🧠 Interactive Quiz"
        )

        st.caption(
            "Click a question to reveal "
            "its answer."
        )

        show_quiz(
            st.session_state.quiz,
            num_questions
        )


    # =====================================================
    # COMPLETE PACK
    # =====================================================

    with result_tabs[2]:

        st.subheader(
            "🚀 Complete Study Pack"
        )

        pack_tabs = st.tabs(
            [
                "📖 Notes",
                "🧠 Quiz"
            ]
        )

        with pack_tabs[0]:

            if (
                st.session_state.notes.strip()
            ):

                st.markdown(
                    st.session_state.notes
                )

            else:

                st.info(
                    "No notes available."
                )


        with pack_tabs[1]:

            show_quiz(
                st.session_state.quiz,
                num_questions
            )


# =========================================================
# CHAT
# =========================================================

st.divider()

st.header(
    "💬 Ask BrainBot Anything"
)

st.caption(
    "Ask questions about your notes, "
    "PDF or study material. "
    "BrainBot remembers your conversation."
)


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in (
    st.session_state.chat_history
):

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "💭 Ask BrainBot about your topic..."
)


if question:

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # -----------------------------------------------------
    # ASSISTANT
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🧠 BrainBot is thinking..."
        ):

            try:

                answer = (
                    chat_with_memory(
                        question=question,
                        chat_history=(
                            st.session_state
                            .chat_history
                        ),
                        study_material=(
                            st.session_state
                            .study_material
                        )
                    )
                )

                if not answer:

                    answer = (
                        "I couldn't generate "
                        "an answer."
                    )

                st.markdown(
                    answer
                )


                # Save user message
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": question
                    }
                )


                # Save assistant message
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                st.error(
                    "❌ BrainBot could not "
                    "answer your question."
                )

                st.exception(e)


# =========================================================
# FOOTER
# IMPORTANT:
# NO HTML HERE
# =========================================================

st.divider()

st.caption(
    "🧠 BrainBot"
)

st.markdown(
    "Think • Learn • Practice • Master"
)

st.caption(
    "Built with Python • LangChain • "
    "Hugging Face • Streamlit"
)