import groq
import datetime
from typing import List, Dict
import streamlit as st

class EventManager:
    def __init__(self, groq_api_key: str):
        self.client = groq.Client(api_key=groq_api_key)
    
    def fetch_events(self) -> List[Dict]:
        """Fetch tech events using Groq API"""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        prompt = f"""
        List current tech events after {current_date} with:
        - name, date, location, organizer, url, description, registration_url
        Return as JSON array with these exact fields.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                response_format={"type": "json_object"}
            )
            return eval(response.choices[0].message.content).get('events', [])
        except Exception as e:
            st.error(f"Error fetching events: {str(e)}")
            return []

    @staticmethod
    def display_event(event: Dict, key_suffix: str = ""):
        """Display an event card with registration button"""
        with st.expander(f"{event['name']} - {event['date']}"):
            st.markdown(f"""
            **Location:** {event['location']}  
            **Organizer:** {event['organizer']}  
            **Description:** {event['description']}  
            [Event Website]({event['url']})
            """)
            
            if st.button("Register", key=f"reg_{key_suffix}"):
                st.session_state['selected_event'] = event
                st.session_state['show_registration'] = True

    @staticmethod
    def show_registration_form():
        """Display registration form modal"""
        if st.session_state.get('show_registration'):
            event = st.session_state['selected_event']
            
            with st.form(key=f"reg_form_{event['name']}"):
                st.subheader(f"Register for {event['name']}")
                name = st.text_input("Full Name*")
                email = st.text_input("Email*")
                company = st.text_input("Company")
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    # Here you would save to database
                    st.success("Registration submitted!")
                    st.session_state['show_registration'] = False
                    return {
                        'event': event['name'],
                        'name': name,
                        'email': email,
                        'company': company,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
        return None