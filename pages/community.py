import json
import streamlit as st
import groq
from utils.file_utils import load_knowledge_base
from utils.llm_utils import get_llm_response
from config import API_KEY, KNOWLEDGE_BASE_FILE

def community_assistant_page():
    st.title("💬 Community Assistant")
    st.markdown("Ask me anything about careers, jobs, or the community!")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Type your question..."):
        knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_FILE)
        context = json.dumps(knowledge_base)
        
        client = groq.Client(api_key=API_KEY)
        with st.spinner("Thinking..."):
            ai_response = get_llm_response(client, user_input, context)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()