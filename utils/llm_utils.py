import json
import groq
from typing import Dict

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
    """Convert natural language prompt to job search parameters"""
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

def analyze_resume(client, resume_text: str) -> str:
    """Analyze resume text and return summary"""
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