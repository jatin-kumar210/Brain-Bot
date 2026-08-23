# 📚 AI Notes & Quiz Generator

> Transform long study material into concise notes and revision questions using AI.
>
> demo link : https://brain-bot-erdznkqpacpj5chk84xxuv.streamlit.app/

<div align="center">

🚀 **Powered by LangChain + Hugging Face + Streamlit**

📝 Smart Notes &nbsp;&nbsp; • &nbsp;&nbsp;
🧠 Automatic Quiz &nbsp;&nbsp; • &nbsp;&nbsp;
⚡ Parallel Chains

</div>

---

## ✨ What is this?

**AI Notes & Quiz Generator** is an AI-powered study assistant that converts
long educational content into:

- 📝 Short and simple study notes
- 🧠 5 revision questions with answers
- 📚 A combined study document
- ⬇️ Downloadable study material

The project demonstrates how **LangChain RunnableParallel** can execute
multiple independent chains using the same input.

---

## ⚡ How It Works

```text
                     ┌───────────────┐
                     │               │
                     │  Notes Chain  │
                     │               │
                     └───────┬───────┘
                             │
                             ▼
Input Text ───────────────► RunnableParallel
                             ▲
                             │
                     ┌───────┴───────┐
                     │               │
                     │   Quiz Chain  │
                     │               │
                     └───────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │  Merge Chain  │
                     └───────┬───────┘
                             │
                             ▼
                  📚 Final Study Material
