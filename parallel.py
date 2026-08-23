import os

from dotenv import load_dotenv

from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint
)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

try:
    import streamlit as st
except ImportError:
    st = None


# =========================================================
# GET HUGGING FACE TOKEN
# =========================================================

def get_hf_token():
    """
    Get Hugging Face token.

    Local:
        Uses HF_TOKEN from .env

    Streamlit Cloud:
        Uses HF_TOKEN from Streamlit Secrets
    """

    token = None

    # Streamlit Cloud / Streamlit Secrets
    if st is not None:
        try:
            token = st.secrets.get("HF_TOKEN")
        except Exception:
            token = None

    # Local .env fallback
    if not token:
        token = os.getenv("HF_TOKEN")

    if not token:
        raise ValueError(
            "HF_TOKEN not found. "
            "Add HF_TOKEN to your .env file locally "
            "or Streamlit Secrets when deploying."
        )

    return token


HF_TOKEN = get_hf_token()


# =========================================================
# HUGGING FACE MODELS
# =========================================================

llm_notes = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-8B",
    task="conversational",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=1200
)

model_notes = ChatHuggingFace(
    llm=llm_notes
)


llm_quiz = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-8B",
    task="conversational",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=1500
)

model_quiz = ChatHuggingFace(
    llm=llm_quiz
)


llm_chat = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-8B",
    task="conversational",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=1000
)

model_chat = ChatHuggingFace(
    llm=llm_chat
)


# =========================================================
# OUTPUT PARSER
# =========================================================

parser = StrOutputParser()


# =========================================================
# NOTES PROMPT
# =========================================================

notes_prompt = PromptTemplate(
    template="""
You are an AI study assistant.

Create clear, simple and useful study notes from the
following study material.

Requirements:

- Use simple language.
- Keep important concepts.
- Use headings and bullet points.
- Explain difficult concepts briefly.
- Include important definitions.
- Include important examples if present.
- Do not add unrelated information.
- Make the notes useful for exam revision.

Study Material:

{text}
""",
    input_variables=["text"]
)


# =========================================================
# QUIZ PROMPT
# =========================================================

quiz_prompt = PromptTemplate(
    template="""
You are an AI quiz generator.

Generate EXACTLY {num_questions} question-answer pairs
from the study material below.

Requirements:

- Generate exactly {num_questions} questions.
- Questions must be based only on the provided material.
- Keep questions clear and useful for revision.
- Use a mixture of conceptual and factual questions.
- Provide the answer immediately after each question.
- Do not add explanations outside the questions.

Use EXACTLY this format:

1. Question here
Answer: Answer here

2. Question here
Answer: Answer here

Continue until exactly {num_questions} questions
have been generated.

Study Material:

{text}
""",
    input_variables=[
        "text",
        "num_questions"
    ]
)


# =========================================================
# PARALLEL NOTES + BASIC QUIZ CHAIN
# =========================================================
#
# This demonstrates RunnableParallel.
#
# The actual generate_study_material() function below
# uses the requested number of questions.
#

parallel_chain = RunnableParallel(
    {
        "notes": notes_prompt | model_notes | parser,
        "quiz": (
            PromptTemplate(
                template="""
Generate 5 short question-answer pairs from this material.

Format:

1. Question
Answer: ...

2. Question
Answer: ...

3. Question
Answer: ...

4. Question
Answer: ...

5. Question
Answer: ...

Study Material:

{text}
""",
                input_variables=["text"]
            )
            | model_quiz
            | parser
        )
    }
)


# =========================================================
# FINAL MERGE PROMPT
# =========================================================

merge_prompt = PromptTemplate(
    template="""
Create a complete study document using the notes and quiz
provided below.

## STUDY NOTES

{notes}

## QUIZ

{quiz}

Keep the notes and quiz clearly separated.

Do not remove important information.
""",
    input_variables=[
        "notes",
        "quiz"
    ]
)


merge_chain = (
    merge_prompt
    | model_notes
    | parser
)


# =========================================================
# GENERATE STUDY MATERIAL
# =========================================================

def generate_study_material(
    text,
    num_questions=5
):
    """
    Generate study notes, quiz and complete study pack.

    Parameters
    ----------
    text : str
        User's study material.

    num_questions : int
        Number of quiz questions requested.

    Returns
    -------
    dict
        {
            "notes": "...",
            "quiz": "...",
            "final": "..."
        }
    """

    if not text or not text.strip():
        raise ValueError(
            "Study material cannot be empty."
        )

    try:
        num_questions = int(num_questions)
    except (TypeError, ValueError):
        num_questions = 5

    num_questions = max(
        1,
        min(num_questions, 20)
    )

    # -----------------------------------------------------
    # Generate notes and quiz
    # -----------------------------------------------------

    notes = (
        notes_prompt
        | model_notes
        | parser
    ).invoke(
        {
            "text": text
        }
    )

    quiz = (
        quiz_prompt
        | model_quiz
        | parser
    ).invoke(
        {
            "text": text,
            "num_questions": num_questions
        }
    )

    # -----------------------------------------------------
    # Create complete study pack
    # -----------------------------------------------------

    final = merge_chain.invoke(
        {
            "notes": notes,
            "quiz": quiz
        }
    )

    return {
        "notes": notes,
        "quiz": quiz,
        "final": final
    }


# =========================================================
# CHAT PROMPT
# =========================================================

chat_prompt = PromptTemplate(
    template="""
You are BrainBot, an intelligent and friendly AI study
assistant.

Your job is to help a student understand their study
material.

STUDY MATERIAL:

{study_material}

PREVIOUS CONVERSATION:

{history}

STUDENT QUESTION:

{question}

Instructions:

- Answer clearly and accurately.
- Use simple language.
- Explain difficult concepts step by step.
- Use examples when useful.
- Prefer information from the study material.
- If the answer is not available in the study material,
  clearly say that.
- Do not invent facts.
- Do not repeat the entire study material.
- Keep the response focused on the student's question.

Answer:
""",
    input_variables=[
        "study_material",
        "history",
        "question"
    ]
)


# =========================================================
# CHAT WITH MEMORY
# =========================================================

def chat_with_memory(
    question,
    chat_history=None,
    study_material=""
):
    """
    Chat with BrainBot using previous conversation
    and the current study material.
    """

    if not question or not question.strip():
        return "Please enter a question."

    if chat_history is None:
        chat_history = []

    # -----------------------------------------------------
    # Convert chat history into text
    # -----------------------------------------------------

    history_parts = []

    for message in chat_history:

        if not isinstance(message, dict):
            continue

        role = message.get(
            "role",
            "user"
        )

        content = message.get(
            "content",
            ""
        )

        if content:
            history_parts.append(
                f"{role.capitalize()}: {content}"
            )

    history_text = "\n".join(
        history_parts
    )

    if not history_text:
        history_text = "No previous conversation."

    if not study_material:
        study_material = (
            "No study material has been provided yet."
        )

    # -----------------------------------------------------
    # Run chat chain
    # -----------------------------------------------------

    chat_chain = (
        chat_prompt
        | model_chat
        | parser
    )

    answer = chat_chain.invoke(
        {
            "study_material": study_material,
            "history": history_text,
            "question": question
        }
    )

    return answer


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    sample_text = """
    Support Vector Machines are supervised learning
    algorithms used for classification, regression and
    outlier detection.

    SVMs are effective in high-dimensional spaces.
    They use support vectors to make predictions.
    Different kernel functions can be used.
    """

    result = generate_study_material(
        sample_text,
        5
    )

    print("\n================ NOTES ================\n")
    print(result["notes"])

    print("\n================ QUIZ ================\n")
    print(result["quiz"])

    print("\n================ FINAL ================\n")
    print(result["final"])