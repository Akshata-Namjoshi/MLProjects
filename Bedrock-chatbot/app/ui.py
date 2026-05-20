import streamlit as st

from .bedrock_client import call_bedrock_async
from .metrics import CallStats

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_calls": 0,
            "total_cost": 0.0,
            "latencies": [],
        }


def update_stats(call_stats: CallStats):
    s = st.session_state.stats
    s["total_calls"] += 1
    s["total_cost"] += call_stats.cost_usd
    s["latencies"].append(call_stats.latency_ms)


def render_sidebar():
    st.sidebar.header("Chat Settings")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    stream = st.sidebar.toggle("Stream responses", value=True)

    st.sidebar.subheader("Session Stats")
    s = st.session_state.stats
    avg_latency = sum(s["latencies"]) / len(s["latencies"]) if s["latencies"] else 0
    st.sidebar.write(f"Total calls: {s['total_calls']}")
    st.sidebar.write(f"Total cost (approx): ${s['total_cost']:.4f}")
    st.sidebar.write(f"Avg latency: {avg_latency:.1f} ms")

    return temperature, stream


def render_chat():
    st.title("Amazon Bedrock Chatbot")
    st.caption("Local Streamlit app using Bedrock Inference Profile + Prompt Management")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask something...")
    return user_input


def handle_user_message(user_input: str, temperature: float, stream: bool):
    from time import time
    start = time()

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        if stream:
            placeholder = st.empty()
            acc_text = ""
            for token in call_bedrock_async(user_input, temperature, stream=True):
                acc_text += token
                placeholder.markdown(acc_text)
            assistant_reply = acc_text
        else:
            future = call_bedrock_async(user_input, temperature, stream=False)
            resp = future.result()
            # adapt to actual response structure; here just show raw JSON
            assistant_reply = f"```json\n{resp}\n```"
            st.markdown(assistant_reply)

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    latency_ms = (time() - start) * 1000
    # crude tokens estimate; refine when you have real metadata
    call_stats = CallStats(latency_ms=latency_ms, tokens=512, cost_usd=0.003 * 0.512)
    update_stats(call_stats)