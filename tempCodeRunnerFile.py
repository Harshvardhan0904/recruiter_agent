from flask import Flask, render_template, jsonify, request, session
from PyPDF2 import PdfReader
import json
from utils.resume_parsing import get_details, skill_matching
from utils.agents import get_jobs , get_ques

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for using session storage

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload_resume', methods=["POST"])
def resume_parse():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files['resume']

    if file.filename == '':
        return jsonify({"error": "No file selected"})

    if file and file.filename.endswith(".pdf"):
        text = ""
        reader = PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()  

        res = get_details(text)

        clean = res.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(clean)

            
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse resume details"})

        # Extract skills properly
        skills = data.get("Skills", [])

        
        session['final_skill'] = skills if isinstance(skills, list) else []

        print("Skills stored in session:", session['final_skill'])

        # Extract other resume details
        name = data.get("Full Name", "N/A")
        info = data.get("Contact Information", {})
        email = info.get("Email", "N/A")
        phone = info.get("Phone", "N/A")
        certifications = data.get("Certifications", "N/A")
        projects = data.get("Projects", [])
        exp = data.get("Work Experience", [])

        # Extract project names and descriptions
        project_names = [p['Name'] for p in projects if 'Name' in p]
        project_desc = [p['Description'] for p in projects if 'Description' in p]

        # Extract work experience details
        company = [c["Company"] for c in exp if isinstance(exp, list) and "Company" in c]
        title = [c["Title"] for c in exp if isinstance(exp, list) and "Title" in c]

        project_work = [p['Projects'] for p in exp if isinstance(exp, list) and 'Projects' in p]
        flattened_projects = [p for sublist in project_work for p in sublist] if isinstance(project_work, list) else []

        project_names_intern = [p['Project Name'] for p in flattened_projects if 'Project Name' in p]
        project_desc_intern = [p['Description'] for p in flattened_projects if 'Description' in p]

        # ✅ Render result.html and pass session-stored skills
        return render_template('result.html', name=name, skills=session['final_skill'], email=email, phone=phone, 
                               certifications=certifications, project_names=project_names, 
                               project_desc=project_desc, 
                               company=company, title=title, 
                               project_names_intern=project_names_intern, 
                               project_desc_intern=project_desc_intern)

@app.route('/ats_matcher', methods=['GET', 'POST'])
def ats():
    ats_score = "N/A"
    suggestions = "Enter a job description and submit to see your ATS score"
    final_skill = session.get('final_skill', [])
    
    # Only process if it's a POST request with job description
    if request.method == 'POST':
        job_des = request.form.get('job_description', '').strip()
        
        if not job_des:
            suggestions = "Please enter a job description"
        elif not final_skill:
            suggestions = "No skills detected. Please GO BACK! and upload your resume first."
        else:
            try:
                res = skill_matching(final_skill, job_des)
                text = res.candidates[0].content.parts[0].text
                clean = text.replace("```json", "").replace("```", "").strip()

                
                final_text = json.loads(clean)
                ats_score = final_text.get("ATS_Score", "N/A")
                suggestions = final_text.get("Suggestions", "No suggestions provided.")
                ats_score = int(ats_score)
                    
    
                if isinstance(suggestions, list):
                    suggestions = "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
            except Exception as e:
                suggestions = "An error occurred during skill matching"
                app.logger.error(f"Error in ATS matching: {e}")

            print("ATS SCORE : ",ats_score)
            print("SUGGESIONS : ",suggestions)

    return render_template("ats.html", 
                         ats_score=ats_score, 
                         suggestions=suggestions, 
                         final_skill=final_skill)


@app.route('/recent_jobs', methods=["GET", "POST"])
def jobs():
    print("Route /recent_jobs was called!")  
    titles, descs, urls = get_jobs(session['final_skill'])
    
    jobs_data = zip(titles, urls, descs)
    
    print(titles)
    print(titles)

    return render_template('jobs.html', jobs_data=jobs_data)

@app.route('/interviw', methods=["GET", "POST"])
def interview():
    q_list = []
    question = get_ques(session["final_skill"])
    
    for i in question:
        q_list.append(i["question"])

    return render_template("interview.html",q_list = q_list)
if __name__ == "__main__":
    app.run(debug=True)
