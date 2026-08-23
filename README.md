# 🌍 TravelMate AI — Multilingual AI Travel & Tourism Chatbot

**TravelMate AI** is a state-of-the-art Multilingual AI Travel & Tourism Chatbot powered by dynamic **Wikimedia APIs (Wikipedia, Wikivoyage, Wikimedia Commons)**, Retrieval-Augmented Generation (RAG), and Google Gemini LLM synthesis.

---

## 🌟 Key Features

1. **Dynamic Wikimedia API Integration**:
   - **Wikipedia API** (`{lang}.wikipedia.org`): Retrieves historical facts, cultural significance, monuments, and geography extracts.
   - **Wikivoyage API** (`{lang}.wikivoyage.org`): Retrieves travel guide information, top attractions, local cuisine, activities, and transport.
   - **Wikimedia Commons API** (`commons.wikimedia.org`): Retrieves high-definition travel photos with license & creator attributions (`Image: Wikimedia Commons — Author (License)`).

2. **Multilingual Support (12+ Languages)**:
   - English, Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, French, Spanish, German, Japanese.

3. **Anti-Hallucination Guardrail**:
   - If relevant information is not found in Wikimedia or Knowledge Base sources, outputs:
     > *"I couldn't find reliable information about this topic in the available Wikimedia sources."*

4. **Real-time Live Data Notice**:
   - Educates users asking for live flight prices, today's current weather, or tonight's hotel availability that Wikimedia sources provide static encyclopedic knowledge.

5. **Conversation Session Memory**:
   - Resolves follow-up queries dynamically (e.g. *"Tell me about Paris"* followed by *"What are the famous places there?"*).

6. **Voice Input & Text-to-Speech (TTS)**:
   - Native browser Web Speech API for voice microphone input and speech playback.

7. **Developer Debug Diagnostic Panel**:
   - Toggleable dev panel showing query trace, detected language, search query, retrieved Wikimedia extracts, and image metadata.

---

## 📁 Repository Structure

```
travel/
├── app.py                      # Flask REST Backend Server
├── wikimedia_service.py        # Wikimedia (Wikipedia, Wikivoyage, Commons) Integration Service
├── rag_engine.py               # RAG Pipeline, Language Detection & LLM Synthesis
├── data/
│   └── knowledge_base.json     # Travel Knowledge Base Catalog
├── templates/
│   └── index.html              # TravelMate AI Web Application Interface
├── static/
│   ├── css/
│   │   └── styles.css          # Modern Dark/Light Theme CSS
│   └── js/
│       └── app.js              # Client Application Logic, Web Speech & Debug Panel
├── .env.example                # Environment Variable Template
└── README.md                   # Project Documentation
```

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.9+
- Flask, Flask-CORS, google-genai

### 2. Installation
```bash
pip install flask flask-cors google-genai
```

### 3. Environment Setup (Optional)
Copy `.env.example` to `.env` and set your Google Gemini API key:
```bash
GEMINI_API_KEY=your_google_gemini_api_key
```

### 4. Running the Web Application
```bash
python -B -X utf8 app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📡 API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Main TravelMate AI Application Interface |
| `/api/chat` | `POST` | Primary Multilingual RAG Chatbot Endpoint |
| `/api/wikimedia/search` | `GET` | Live Wikipedia, Wikivoyage & Commons Search |
| `/api/debug` | `POST` | Dev Mode Diagnostic Trace Payload |
| `/api/plan-trip` | `POST` | Interactive Trip Itinerary & Budget Planner |
| `/api/destinations` | `GET` | Catalog of Destinations with Region Filtering |

---

## 📜 License & Attribution

All content retrieved from Wikipedia and Wikivoyage is licensed under **CC BY-SA 4.0** / **GFDL**. Media thumbnails are sourced from **Wikimedia Commons** with appropriate creator and license attributions.
