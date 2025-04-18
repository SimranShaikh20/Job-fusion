import pandas as pd
from jobspy import scrape_jobs
import streamlit as st
from typing import Dict

@st.cache_data(ttl=3600)
def get_job_data(search_params: Dict[str, str]) -> pd.DataFrame:
    """Scrape job data from various sources"""
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