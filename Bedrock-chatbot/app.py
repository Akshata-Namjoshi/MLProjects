import streamlit as st

from app.ui import init_session_state, render_sidebar, render_chat, handle_user_message

def main():
    st.set_page_config(page_title="Bedrock Chatbot", page_icon="💬", layout="wide")
    init_session_state()
    temperature, stream = render_sidebar()
    user_input = render_chat()

    if user_input:
        handle_user_message(user_input, temperature, stream)


if __name__ == "__main__":
    main()