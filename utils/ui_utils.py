import streamlit as st
    
def setup_page():
    # REMOVE st.set_page_config() from here
    st.markdown("""
    <style>
        /* Your CSS styles only */
    </style>
    """, unsafe_allow_html=True)

def make_clickable(url: str) -> str:
    return f'<a href="{url}" target="_blank">🔗 Link</a>'