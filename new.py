import streamlit as st
import groq
from jobspy import scrape_jobs
import pandas as pd
import json
from typing import Dict

def make_clickable(url: str) -> str:
    """
    Convert a URL to a clickable HTML link.
    """
    return f'<a href="{url}" target="_blank" style="color: #4e79a7;">Link</a>'

def convert_prompt_to_parameters(client, prompt: str) -> Dict[str, str]:
    """
    Convert user input prompt to structured job search parameters using AI.
    """
    system_prompt = """
    You are a language decoder. Extract:
    - search_term: job role/keywords (expand abbreviations)
    - location: mentioned place or 'USA'
    Return only: {"search_term": "term", "location": "location"}
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": f"Extract from: {prompt}"}],
        max_tokens=1024,
        model='llama3-8b-8192',
        temperature=0.2
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"search_term": prompt, "location": "USA"}

def analyze_resume(client, resume: str) -> str:
    """
    Generate a comprehensive resume analysis using AI.
    """
    system_prompt = """Analyze resume comprehensively in 150 words:
    1. Professional Profile Summary
    2. Key Technical Skills
    3. Educational Background
    4. Core Professional Experience Highlights
    5. Unique Strengths/Achievements
    Return a concise, structured professional overview."""
    
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": resume}],
        max_tokens=400,
        model='llama3-8b-8192',
        temperature=0.3
    )
    
    return response.choices[0].message.content

@st.cache_data(ttl=3600)
def get_job_data(search_params: Dict[str, str]) -> pd.DataFrame:
    """
    Fetch job listings from multiple sources based on search parameters.
    """
    try:
        return scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter"],
            search_term=search_params["search_term"],
            location=search_params["location"],
            results_wanted=60,
            hours_old=24,
            country_indeed='USA'
        )
    except Exception as e:
        st.warning(f"Error in job scraping: {str(e)}")
        return pd.DataFrame()

def main():
    """
    Main Streamlit application entry point for Smart Job Search.
    Handles user interface, job search, and AI-powered job matching.
    """
    st.set_page_config(
        layout="wide",
        page_title="Smart Job Search with AI Matching",
        initial_sidebar_state="collapsed"
    )

    # Header
    st.markdown("""
        <h1 style='text-align: center;'>🚀 Smart Job Search with AI Matching</h1>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        user_input = st.text_area(
            "Describe the job you're looking for",
            placeholder="E.g., 'Senior Python developer with React experience in San Francisco'",
            height=150
        )
    
    with col2:
        user_resume = st.text_area(
            "Paste your resume here (for AI-powered matching)",
            placeholder="Paste your resume for AI-powered job matching",
            height=150
        )
        
    api_key = st.text_input(
        "Enter your Groq API key",
        type="password",
        help="Your API key will be used to process the job search query"
    )

    if st.button("🔍 Search Jobs", disabled=not api_key):
        # Show job listings and analyze resume if input is valid
        if user_input and api_key:
            try:
                client = groq.Client(api_key=api_key)
                
                # Process job search parameters
                with st.spinner("Processing search parameters..."):
                    processed_params = convert_prompt_to_parameters(client, user_input)
                
                # Fetch job listings
                with st.spinner("Searching for jobs..."):
                    jobs_data = get_job_data(processed_params)
                    
                    if not jobs_data.empty:
                        display_df = jobs_data[['site', 'job_url', 'title', 'company', 'location', 'job_type', 'date_posted']]
                        display_df['job_url'] = display_df['job_url'].apply(make_clickable)
                        
                        st.success(f"Found {len(display_df)} jobs!")
                        st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
                        
                        # Resume analysis
                        if user_resume:
                            with st.spinner("Analyzing resume summary..."):
                                resume_summary = analyze_resume(client, user_resume)
                                st.success("Resume summary:")
                                st.write(resume_summary)
                    else:
                        st.warning("No jobs found with the given parameters.")
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
        elif not api_key:
            st.warning("Please enter your API key.")
        else:
            st.warning("Please enter a job description.")

if __name__ == "__main__":
    main()
