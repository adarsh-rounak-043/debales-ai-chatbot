from __future__ import annotations

import sqlite3
from typing import Annotated, Dict, Optional, TypedDict

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.embeddings import HuggingFaceEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.utilities import SerpAPIWrapper

load_dotenv()

# -------------------
# 1. LLM + embeddings
# -------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L12-v2"
)

# -------------------
# 2. Debales RAG (Chroma)
# -------------------
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -------------------
# 3. Tools
# -------------------
search = SerpAPIWrapper()

@tool
def debales_rag_tool(query: str) -> dict:
    """Retrieve information about Debales AI."""
    results = retriever.invoke(query)

    if not results:
        return {"error": "No relevant Debales info found."}

    return {
        "context": [doc.page_content for doc in results]
    }

@tool
def search_tool(query: str) -> str:
    """Search the web for external information."""
    return search.run(query)

tools = [debales_rag_tool, search_tool]

llm_with_tools = llm.bind_tools(tools)

# -------------------
# 4. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 5. Node (FIXED PROMPT)
# -------------------
def chat_node(state: ChatState, config=None):
    
    system_message = SystemMessage(
    content="""
    You are a Debales AI assistant.

    STRICT INSTRUCTIONS:

    - You MUST use tools for answering.
    - NEVER answer from memory.

    ROUTING:
    - Debales AI questions → ALWAYS call debales_rag_tool
    - General questions → ALWAYS call search_tool
    - Mixed → call BOTH tools

    RULES:
    - Do NOT skip tool calls
    - Do NOT guess answers
    - If tool returns no info:
    → "I don't know based on available information."

    FINAL OUTPUT:
    - Combine tool results into a clean answer
    """
    )

    messages = [system_message, *state["messages"]]

    response = llm_with_tools.invoke(messages, config=config)

    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 6. Checkpointer (THREAD MEMORY)
# -------------------
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 7. Graph
# -------------------
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 8. Helpers (KEEP THESE!)
# -------------------
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)