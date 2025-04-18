import streamlit as st
import groq
from jobspy import scrape_jobs
import pandas as pd
import json
from typing import Dict, List
import PyPDF2
import os
from datetime import datetime

# ====== Configuration ======
API_KEY = "gsk_your_api_key_here"  # Replace with your Groq API key
KNOWLEDGE_BASE_FILE = "community_knowledge.json"

# ====== Shared Functions ======
def make_clickable(url: str) -> str:
    return f'<a href="{url}" target="_blank" style="color: #91cfff;">🔗 Link</a>'

def load_knowledge_base() -> Dict:
    """Load predefined FAQs and responses"""
    default_kb = {
        "general": [
            {"question": "How do I reset my password?", "answer": "Go to Settings > Security > Reset Password."},
            {"question": "Where can I find upcoming events?", "answer": "Check the Events tab in the community dashboard."},
        ],
        "technical": [
            {"question": "How do I report a bug?", "answer": "Submit a ticket at support.example.com."},
            {"question": "Why is my account not working?", "answer": "Try clearing your cache or contact support."},
        ],
        "career": [
            {"question": "How do I improve my resume?", "answer": "Use our Resume Analysis tool for personalized feedback."},
            {"question": "Where can I find job postings?", "answer": "Try our Job Search feature with AI-powered matching."},
        ]
    }
    try:
        with open(KNOWLEDGE_BASE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_kb

def get_llm_response(client, user_query: str, context: str = "") -> str:
    """Get an AI-generated response using Groq/Llama3"""
    system_prompt = f"""
    You are a helpful community and career assistant. Answer concisely and accurately.
    Knowledge Base Context: {context}
    """
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        model="llama3-8b-8192",
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content

def convert_prompt_to_parameters(client, prompt: str) -> Dict[str, str]:
    system_prompt = """
    You are a language decoder. Extract:
    - search_term: job role/keywords (expand abbreviations)
    - location: mentioned place or 'USA'
    Return only: {"search_term": "term", "location": "location"}
    """
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract from: {prompt}"}
        ],
        max_tokens=1024,
        model='llama3-8b-8192',
        temperature=0.2
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"search_term": prompt, "location": "USA"}

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(client, resume_text: str) -> str:
    system_prompt = """Analyze resume comprehensively in 150 words:
    1. Professional Profile Summary
    2. Key Technical Skills
    3. Educational Background
    4. Core Professional Experience Highlights
    5. Unique Strengths/Achievements
    Return a concise, structured professional overview."""
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": resume_text}
        ],
        max_tokens=400,
        model='llama3-8b-8192',
        temperature=0.3
    )
    
    return response.choices[0].message.content

@st.cache_data(ttl=3600)
def get_job_data(search_params: Dict[str, str]) -> pd.DataFrame:
    try:
        return scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search_params["search_term"],
            location=search_params["location"],
            results_wanted=60,
            hours_old=24,
            country_indeed='USA'
        )
    except Exception as e:
        st.warning(f"⚠️ Error in job scraping: {str(e)}")
        return pd.DataFrame()

# ====== Page Config ======
def setup_page():
    st.set_page_config(
        layout="wide",
        page_title="AI Career & Community Assistant",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        .job-table-container, .chat-container {
            width: 100% !important;
            overflow-x: auto;
            margin-top: 20px;
        }
        table {
            width: 100% !important;
            border-collapse: collapse;
            table-layout: auto;
        }
        th, td {
            padding: 12px 15px;
            border: 1px solid #444;
            text-align: left;
            white-space: normal !important;
            max-width: 300px;
            word-wrap: break-word;
        }
        th {
            background-color: #1f1f2e;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background-color: #2c2c3a;
        }
        tr:hover {
            background-color: #3a3a4a;
        }
        a {
            color: #91cfff !important;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .stTextArea textarea {
            min-height: 150px !important;
        }
        .chat-message-user {
            background-color: #2c3e50;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .chat-message-bot {
            background-color: #34495e;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# ====== Pages ======
def home_page():
    st.title("Welcome to AI Career & Community Assistant! 🚀")
    st.markdown("""
    <div style="background-color:#2c2c3a; padding:20px; border-radius:10px;">
        <h3 style="color:#91cfff;">Your All-in-One Career Development Platform</h3>
        <p>Select an option from the sidebar menu to:</p>
        <ul>
            <li>💬 Get instant answers to career questions</li>
            <li>🔍 Search for jobs using natural language</li>
            <li>📄 Get AI analysis of your resume</li>
            <li>✨ Find the perfect job matches</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://source.unsplash.com/random/800x400/?career,technology", use_column_width=True)

def community_assistant_page():
    st.title("💬 Community Assistant")
    st.markdown("Ask me anything about careers, jobs, or the community!")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Type your question..."):
        knowledge_base = load_knowledge_base()
        context = json.dumps(knowledge_base)
        
        client = groq.Client(api_key=API_KEY)
        with st.spinner("Thinking..."):
            ai_response = get_llm_response(client, user_input, context)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

def job_search_page():
    st.title("🔍 Job Search")
    st.markdown("<p style='text-align: center;'>Describe your dream job and let AI find the best matches!</p>", unsafe_allow_html=True)
    
    user_input = st.text_area(
        "📝 Enter Your Dream Job Description:",
        placeholder="E.g., 'Senior Python developer with React experience in San Francisco' 💡",
        height=150
    )
    
    if st.button("🚀 Search Jobs Now! 🔍"):
        if user_input and API_KEY:
            try:
                client = groq.Client(api_key=API_KEY)

                with st.spinner("🔧 Processing your job description with AI... ⏳"):
                    processed_params = convert_prompt_to_parameters(client, user_input)

                with st.spinner("🔍 Hunting for the best job listings... 🔎"):
                    jobs_data = get_job_data(processed_params)

                    if not jobs_data.empty:
                        display_df = jobs_data[['site', 'job_url', 'title', 'company', 'location', 'job_type', 'date_posted']]
                        display_df['job_url'] = display_df['job_url'].apply(make_clickable)
                        
                        display_df = display_df.rename(columns={
                            'site': 'Source',
                            'title': 'Job Title',
                            'company': 'Company',
                            'location': 'Location',
                            'job_type': 'Type',
                            'date_posted': 'Posted'
                        })

                        st.success(f"🎯 Found {len(display_df)} jobs matching your description! 🧾")
                        st.markdown("""
                        <div class="job-table-container">
                        """ + display_df.to_html(escape=False, index=False) + """
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("❌ No jobs found for that description. Try rephrasing or broadening your input.")
            except Exception as e:
                st.error(f"🚨 Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a job description to proceed")

def resume_analysis_page():
    st.title("📄 Resume Analysis")
    st.markdown("<p style='text-align: center;'>Upload your resume for AI-powered analysis</p>", unsafe_allow_html=True)
    
    uploaded_resume = st.file_uploader(
        "📎 Upload Your Resume (PDF only, max 20MB)",
        type=["pdf"],
        accept_multiple_files=False
    )
    
    if uploaded_resume and st.button("🧠 Analyze Resume"):
        if API_KEY:
            try:
                client = groq.Client(api_key=API_KEY)
                with st.spinner("📊 Analyzing your resume..."):
                    resume_text = extract_text_from_pdf(uploaded_resume)
                    resume_summary = analyze_resume(client, resume_text)
                    st.success("📋 AI-Powered Resume Overview")
                    st.markdown(f"""
                    <div style='background-color: #2c2c3a; 
                                padding: 20px; 
                                border-radius: 10px;
                                margin-top: 20px;'>
                        {resume_summary}
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"🚨 Error analyzing resume: {str(e)}")
        else:
            st.warning("⚠️ API key is required for resume analysis")

# ====== Main App ======
def main():
    setup_page()
    
    # Sidebar navigation
    st.sidebar.title("Navigation Menu")
    page = st.sidebar.radio("", 
        ["🏠 Home", "💬 Community Assistant", "🔍 Job Search", "📄 Resume Analysis"],
        index=0
    )
    
    # Display selected page
    if page == "🏠 Home":
        home_page()
    elif page == "💬 Community Assistant":
        community_assistant_page()
    elif page == "🔍 Job Search":
        job_search_page()
    elif page == "📄 Resume Analysis":
        resume_analysis_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align:center; font-size:small;">
        <p>AI Career & Community Assistant v1.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()