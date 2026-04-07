# 🤖 Debales AI Chatbot (RAG + LangGraph)

An AI assistant built using **LangGraph**, **RAG (Retrieval-Augmented Generation)**, and **tool calling** that answers questions about Debales AI and fetches external information when needed.

---

## 🚀 Features

* 🔍 **Debales AI Knowledge (RAG)**

  * Scrapes and indexes Debales AI website content
  * Uses Chroma vector database for semantic retrieval

* 🌐 **Web Search (SERP API)**

  * Handles general/non-Debales queries
  * Fetches real-time information from the web

* 🧠 **Intelligent Routing (LangGraph)**

  * Debales queries → RAG
  * External queries → Search tool
  * Mixed queries → Both tools

* 💬 **Multi-Thread Chat**

  * Each conversation stored separately
  * Sidebar thread switching (ChatGPT-like UX)

* ⚡ **Streaming + Tool Visibility**

  * Real-time response streaming
  * Shows when tools are being used

* ❌ **No Hallucination**

  * Answers only from retrieved data or search
  * Falls back safely if no info is found

---

## 🏗️ Architecture

```
User Query
   ↓
LangGraph Agent
   ↓
Decision Layer
   ├── Debales AI → RAG (Chroma DB)
   ├── External → SERP API
   ├── Mixed → Both
   ↓
Final Response (LLM)
```

---

## 🧰 Tech Stack

* **Frontend:** Streamlit
* **Backend:** LangGraph
* **LLM:** Google Gemini (via LangChain)
* **Vector DB:** Chroma
* **Embeddings:** Sentence Transformers
* **Search Tool:** SERP API

---

## 📂 Project Structure

```
debales-ai-chatbot/
│
├── streamlit_app.py          # Frontend UI
├── langgraph_rag_backend.py  # Backend (LangGraph agent)
├── chroma_db/                # Vector database (Debales content)
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/debales-ai-chatbot.git
cd debales-ai-chatbot
```

---

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set environment variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
SERPAPI_API_KEY=your_serpapi_key
```

---

### 5. Run the application

```bash
streamlit run streamlit_app.py
```

---

## 🧠 How It Works

### 1. RAG (Debales AI Knowledge)

* Website content is scraped and stored in Chroma DB
* Queries are embedded and matched against relevant chunks
* Retrieved context is used to generate answers

---

### 2. Tool Calling

* If query is not about Debales AI → SERP API is used
* LangGraph decides which tool to call
* Results are combined into final response

---

### 3. LangGraph Workflow

* `chat_node` → decides next step
* `ToolNode` → executes tools
* Conditional edges → route between nodes

---

## 🧪 Example Queries

| Query                         | Behavior      |
| ----------------------------- | ------------- |
| What does Debales AI do?      | RAG           |
| What is OpenAI?               | Search tool   |
| Compare Debales AI and OpenAI | Both tools    |
| Unknown company info          | Safe fallback |

---

## 📦 Deployment

Deployed using **Streamlit Cloud**:

👉 [https://debales-ai-chatbot.streamlit.app/](https://debales-ai-chatbot.streamlit.app/)

---

## 🎯 Assignment Requirements Covered

* ✅ RAG from Debales AI website
* ✅ SERP API tool integration
* ✅ LangGraph workflow
* ✅ Correct routing (RAG vs Search)
* ✅ No hallucination
* ✅ Clean UI and streaming

---

## 💡 Future Improvements

* Add chat titles (like ChatGPT)
* Better tool routing (rule-based + LLM hybrid)
* Source citations in responses
* Caching for faster responses

---

## 🙌 Acknowledgements

* LangChain & LangGraph
* Streamlit
* Sentence Transformers
* SERP API
