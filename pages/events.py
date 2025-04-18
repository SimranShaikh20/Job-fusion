import streamlit as st
from utils.event_utils import EventManager

def events_page():
    st.title("📅 Tech Events")
    st.markdown("Discover upcoming technology events and conferences")
    
    # Initialize event manager
    if 'event_manager' not in st.session_state:
        st.session_state.event_manager = EventManager(st.secrets["GROQ_API_KEY"])
    
    # Fetch events
    if 'events' not in st.session_state:
        with st.spinner("Loading events..."):
            st.session_state.events = st.session_state.event_manager.fetch_events()
    
    # Display events
    if st.session_state.events:
        for idx, event in enumerate(st.session_state.events):
            st.session_state.event_manager.display_event(event, str(idx))
        
        # Handle registration
        registration = st.session_state.event_manager.show_registration_form()
        if registration:
            st.session_state.setdefault('registrations', []).append(registration)
    else:
        st.warning("No events found. Please try again later.")
    
    # Show registrations in sidebar
    if 'registrations' in st.session_state and st.session_state.registrations:
        with st.sidebar.expander("Your Registrations"):
            for reg in st.session_state.registrations:
                st.write(f"✅ {reg['event']}")