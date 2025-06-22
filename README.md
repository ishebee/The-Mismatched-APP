# Mismatched - The Memory App

A personalized chatbot built using Retrieval-Augmented Generation (RAG) that allows you to store and retrieve memories conversationally. Inspired by a deeply personal story, this project was born from a blend of technology and emotion — combining a heartfelt journey with modern AI techniques like LangChain, ChromaDB, and Google Sheets integration.

---

## 💡 Inspiration

Have you ever watched *Mismatched* on Netflix? In Season 3, Dimple builds a “DadBot” to preserve her father’s personality, voice, and memories. That emotional arc struck a chord with me. Around the same time, I found myself reminiscing about a girl I truly loved — someone I had a deep connection with but couldn't be with due to life’s circumstances. That’s when it hit me:

**What if I could preserve our shared memories into a chatbot that could speak like I would? Or like she would remember them?**

This project is my tribute to that idea. Not just a chatbot — but a living archive of moments, captured and accessible through conversation.

---

## 🔍 Project Overview

This RAG-based chatbot acts as a digital memory keeper. It fetches and semantically matches user prompts with the most relevant memory data, making every response feel contextual, personalized, and emotional.

All memories are stored in a **Google Sheet**, allowing dynamic updates and a collaborative way to feed it more experiences over time — without hardcoding or database maintenance.

---

## ✨ Key Features

- 🧠 **RAG-Based Retrieval**: Combines semantic search with generative responses.
- 📜 **Memory Storage via Google Sheets**: Easy to manage, collaborative, and editable.
- 💬 **Streamlit Interface**: Simple, user-friendly conversational UI.
- 🧩 **Modular Code Design**: Includes reusable utilities for data access, embedding, and memory handling.
- 💭 **Emotionally Driven Use Case**: Designed with storytelling, relationships, and memory journaling in mind.

---

## 📚 What is RAG (Retrieval-Augmented Generation)?

Retrieval-Augmented Generation is an architecture where a chatbot first **retrieves relevant context** from a knowledge base using semantic search, then **generates** an answer using that context.

In this project:
- We use **ChromaDB** for vector-based semantic search.
- **LangChain** powers the pipeline for context-aware response generation.
- Google Sheets serves as the external “memory base” from which records are pulled and embedded.

![RAG Flow Diagram](https://github.com/yourname/yourrepo/assets/rag-diagram.png) *(Replace with your local image or a diagram)*

---

## 🛠 Tech Stack

- **Python**
- **Streamlit** – for building the web interface
- **LangChain** – RAG orchestration
- **ChromaDB** – Vector database for semantic search
- **Google Sheets API** – As memory storage
- **FAISS** *(used optionally in experiments)*

---

## 📂 File Structure

| File | Description |
|------|-------------|
| `main.py` | Streamlit front-end for chat interaction |
| `memory.py` | Controls conversation flow and memory search |
| `memory_utils.py` | Handles Google Sheets I/O and embeddings |
| `utils.py` | Helper functions and text cleanup |
| `requirements.txt` | List of required Python packages |

---

## 🧠 Sample Use Case

User: *“Tell me something about our last trip to Ooty.”*  
Bot: *“You and Vita took a spontaneous bus ride to Ooty on July 12. You bought her roses and shared corn by the lake. She laughed when you dropped the camera.”*

This isn’t just data. It’s **reliving**.

---

## 🌱 What's Next?

This memory chatbot is just the seed. I now have a vision of expanding this into a **full-fledged digital journaling app**:

- Secure **user login**
- **Contact-based memory grouping**
- Voice-based **memory input and retrieval**
- Timeline views and auto-summary of events

The journey has just begun — and I'm excited to build something that remembers, heals, and grows along with me.

---

## 🤍 Author Note

This was more than code for me — it was therapy. A piece of my heart now lives in this chatbot, one memory at a time. I hope one day, this helps someone else preserve their own cherished moments.

---

