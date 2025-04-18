# THIS MUST BE THE VERY FIRST LINE
import streamlit as st

# THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    layout="wide",
    page_title="AI Career & Community Assistant",
    initial_sidebar_state="expanded",  # Hides auto sidebar
    menu_items={}                       # Disables hamburger menu
)

# Hide the automatic sidebar completely using CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Create your custom sidebar
    with st.sidebar:
        st.title("Navigation Menu")
        page = st.radio(
            "Go to",
            ["🏠 Home", "💬 Community Assistant", "🔍 Job Search", "📄 Resume Analysis","📅 Events"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.caption("AI Career & Community Assistant v1.0")

    # Import pages inside main() after Streamlit is initialized
    from pages.home import home_page
    from pages.community import community_assistant_page
    from pages.jobs import job_search_page
    from pages.resume import resume_analysis_page
    from pages.events import events_page

    # Page routing
    if page == "🏠 Home":
        home_page()
    elif page == "💬 Community Assistant":
        community_assistant_page()
    elif page == "🔍 Job Search":
        job_search_page()
    elif page == "📄 Resume Analysis":
        resume_analysis_page()
    elif page == "📅 Events":
        events_page() 

if __name__ == "__main__":
    main()