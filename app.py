import os
from flask import Flask, render_template, request
import PyPDF2

app = Flask(__name__)

# A comprehensive baseline dictionary mapping job roles to targeted keywords/skills
JOB_DATABASE = {
    "Data Scientist": ["python", "machine learning", "data analysis", "sql", "pandas", "scikit-learn", "r", "tableau"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "bootstrap", "frontend", "backend"],
    "DevOps Engineer": ["docker", "kubernetes", "aws", "linux", "jenkins", "cicd", "git", "cloud"],
    "Software Engineer (Java)": ["java", "spring boot", "hibernate", "oop", "sql", "data structures", "algorithms"]
}

def extract_text_from_pdf(file):
    """Extracts clean text content out of an uploaded PDF file object."""
    pdf_reader = PyPDF2.PdfReader(file)
    extracted_text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted_text += page_text + " "
    return extracted_text.lower()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['resume']
    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.pdf'):
        # 1. Parse text from the PDF file
        resume_text = extract_text_from_pdf(file)
        
        # 2. Extract detected skills based on our target keywords master-list
        all_master_skills = set(skill for skills in JOB_DATABASE.values() for skill in skills)
        detected_skills = [skill for skill in all_master_skills if skill in resume_text]
        
        # 3. Calculate match scores against predefined job buckets
        recommendations = []
        for role, required_skills in JOB_DATABASE.items():
            matched_skills = [skill for skill in required_skills if skill in resume_text]
            
            # Match score formula: (Matched Skills / Total Required Skills) * 100
            score = int((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0
            
            if score > 0:  # Only recommend if there's at least one skill matching
                recommendations.append({
                    "role": role,
                    "score": score,
                    "matched_skills": matched_skills
                })
        
        # Sort recommendations so the best match sits at the top
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)

        return render_template('index.html', 
                               extracted_skills=detected_skills, 
                               recommendations=recommendations)
    
    return "Invalid file extension. Please upload a PDF.", 400

if __name__ == '__main__':
    app.run(debug=True)