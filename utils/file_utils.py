import json
import PyPDF2
from typing import Dict

def load_knowledge_base(file_path: str) -> Dict:
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
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_kb

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text