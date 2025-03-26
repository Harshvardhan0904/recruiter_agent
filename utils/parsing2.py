import os
import requests
import json
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found! Set it in your .env file.")

# Groq API URL
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_resume_details(resume_text):
    """
    Extracts structured details from a resume using LLaMA 3.
    """
    prompt = f"""
    You are an AI-powered resume parser. Extract the following details from the given resume:

    1. Full Name
    2. Contact Information (Email, Phone, Address)
    3. Education
    4. Work Experience
    5. Skills
    6. Certifications
    7. Projects
    8. Languages Known
    9. Summary

    Return the data in JSON format.

    Resume Text:
    \"\"\"{resume_text}\"\"\"
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            result = response.json()
            return json.loads(result["choices"][0]["message"]["content"])
        except json.JSONDecodeError:
            return {"error": "Failed to parse response"}
    else:
        return {"error": f"API Error: {response.status_code}, {response.text}"}

