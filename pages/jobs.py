import streamlit as st
import pandas as pd
import groq
from utils.llm_utils import convert_prompt_to_parameters
from utils.job_utils import get_job_data
from utils.ui_utils import make_clickable
from config import API_KEY

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