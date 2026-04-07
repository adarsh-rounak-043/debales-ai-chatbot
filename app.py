import uuid
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend import chatbot, retrieve_all_threads

# -------------------
# UTIL
# -------------------
def new_thread():
    return str(uuid.uuid4())

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])

# -------------------
# SESSION INIT
# -------------------
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = new_thread()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "threads" not in st.session_state:
    st.session_state["threads"] = retrieve_all_threads()

thread_id = st.session_state["thread_id"]

# -------------------
# SIDEBAR (THREAD UI)
# -------------------
st.sidebar.title("🤖 Debales AI Assistant")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state["thread_id"] = new_thread()
    st.session_state["messages"] = []
    st.rerun()

st.sidebar.markdown("### 💬 Conversations")

threads = st.session_state["threads"][::-1]

selected_thread = None
for t in threads:
    if st.sidebar.button(str(t), key=f"thread-{t}"):
        selected_thread = t

# -------------------
# LOAD THREAD
# -------------------
if selected_thread:
    st.session_state["thread_id"] = selected_thread

    msgs = load_conversation(selected_thread)
    temp = []

    for m in msgs:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        temp.append({"role": role, "content": m.content})

    st.session_state["messages"] = temp
    st.rerun()

# -------------------
# MAIN UI
# -------------------
st.title("🤖 Debales AI Chatbot")

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------
# INPUT
# -------------------
user_input = st.chat_input("Ask about Debales AI or anything...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {"configurable": {"thread_id": thread_id}}

    with st.chat_message("assistant"):

        status_holder = {"box": None}   # ✅ mutable container

        def stream():

            for message_chunk, _ in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):

                # 🛠️ TOOL DETECTED
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")

                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}`...",
                            expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}`...",
                            state="running",
                            expanded=True
                        )

                # 🤖 STREAM AI RESPONSE
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        response = st.write_stream(stream())

        # ✅ CLOSE STATUS BOX
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Done",
                state="complete",
                expanded=False
            )