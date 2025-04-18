import streamlit as st
import groq
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
from utils.file_utils import extract_text_from_pdf
from utils.llm_utils import analyze_resume
from config import API_KEY

def resume_analysis_page():
    st.title("📄 Resume Analysis")
    st.markdown("<p style='text-align: center;'>Upload your resume for AI-powered analysis and insights!</p>", unsafe_allow_html=True)

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

                    # Extract and process text
                    resume_text = extract_text_from_pdf(uploaded_resume)

                    # Enhanced Prompt for Analysis
                    prompt = f"""
                    Analyze the following resume and provide a detailed summary including:
                    - Candidate's top skills (technical & soft)
                    - Most relevant job titles
                    - Experience level (fresher, intermediate, senior)
                    - Any resume improvement suggestions
                    - Any missing keywords based on current market demands

                    Resume Content:
                    {resume_text}
                    """

                    resume_summary = analyze_resume(client, prompt)

                    # Display AI Summary
                    st.success("📋 AI-Powered Resume Overview")
                    st.markdown(f"""
                    <div style='background-color: #2c2c3a; 
                                padding: 20px; 
                                border-radius: 10px;
                                color: white;
                                margin-top: 20px;'>
                        {resume_summary}
                    </div>
                    """, unsafe_allow_html=True)

                    # Skill Frequency Chart (Enhanced)
                    words = resume_text.lower().split()
                    keywords = ['python', 'java', 'sql', 'react', 'communication', 'machine', 'learning', 'project', 'team']
                    keyword_freq = Counter(word for word in words if word in keywords)

                    if keyword_freq:
                        st.markdown("### 📊 Keyword Frequency in Resume")

                        # Style
                        sns.set_style("whitegrid")

                        # Create figure
                        fig, ax = plt.subplots(figsize=(8, 5))  # medium size chart

                        # Plot bars
                        bars = ax.bar(keyword_freq.keys(), keyword_freq.values(), color='#4da6ff')

                        # Add labels on top of bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate(f'{height}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 5),  # offset
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontsize=9)

                        # Customize chart
                        ax.set_title("🔑 Common Keywords Detected", fontsize=14, fontweight='bold')
                        ax.set_ylabel("Frequency")
                        ax.set_xticks(range(len(keyword_freq)))
                        ax.set_xticklabels(keyword_freq.keys(), rotation=45, ha='right')

                        # Clean up chart borders
                        sns.despine()

                        # Show chart in Streamlit
                        st.pyplot(fig)
                    else:
                        st.info("🤔 No major skill keywords found in the resume text.")
                    
            except Exception as e:
                st.error(f"🚨 Error analyzing resume: {str(e)}")
        else:
            st.warning("⚠️ API key is required for resume analysis")
