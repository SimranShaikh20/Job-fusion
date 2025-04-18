# NO STREAMLIT IMPORTS AT TOP LEVEL
def home_page():
    """Contains ONLY page content"""
    import streamlit as st  # Import INSIDE function
    st.title("Welcome to AI Career & Community Assistant! 🚀")
    # ... rest of your content