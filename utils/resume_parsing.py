import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found! Set it in your .env file.")

# Configure Generative AI
genai.configure(api_key=API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

def get_details(resume_text):
    """
    Extracts structured details from a resume using Gemini AI.

    Returns:
        A dictionary containing extracted information.
    """
    prompt = f"""
    You are an AI resume parser. Extract the following details from the given resume and return a JSON-formatted response:

    1. Full Name
    2. Contact Information(like Email , phone no.)
    3. Education 
    4. Work Experience 
    5. Skills(list formate)
    6. Certifications 
    7. Projects 
    8. Languages Known
    9. Summary 

    Ensure the output is valid JSON.

    Resume Text:
    \"\"\"{resume_text}\"\"\"
    """

    
    response = model.generate_content(prompt)
    return response.text  
    

def skill_matching(skills, job_desc):
    """
    Extracts structured details from the given skill list and job description.
    OUTPUT SHOULD BE JSON ONLY
    

    Returns:
        A JSON response containing:
        - ATS score (out of 100)
        - Suggested improvements for resume
    """
    prompt = f"""
    You are an ATS (Applicant Tracking System) evaluator. Your job is to compare a list of candidate skills with a job description and return an ATS score along with suggestions for improvement.
    show score even if the job description is irrevelivent to the skills
    **Job Description:** {job_desc}

    **Candidate Skills:** {skills}

    Return a valid JSON response in the following format:
    {{
        "ATS_Score": <score out of 100>,
        "Suggestions": "<improvements required>"
    }}
    """

    response = model.generate_content(prompt)
    return response
