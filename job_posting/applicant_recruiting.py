from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from typing import Dict, Any
from dotenv import load_dotenv
import PyPDF2
import docx
import re

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class JobDescriptionGenerator:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)
        self.template = PromptTemplate(
            input_variables=["title", "company", "keywords", "experience"],
            template="""Create a professional job description for the following:
            
            Job Title: {title}
            Company: {company}
            Keywords: {keywords}
            Experience Level: {experience}
            
            Include sections for: Company Overview, Job Description, Requirements, Benefits
            Keep it professional and engaging. Format with appropriate Markdown.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.template)
    
    def generate(self, title, company, keywords, experience):
        return self.chain.run(
            title=title,
            company=company,
            keywords=keywords,
            experience=experience
        )

class ResumeParser:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.template = PromptTemplate(
            input_variables=["resume_text", "job_description"],
            template="""
            Analyze this resume against the job description.
            
            RESUME:
            {resume_text}
            
            JOB DESCRIPTION:
            {job_description}
            
            Extract the following information from the resume:
            1. Candidate Name
            2. Contact Information
            3. Education (degree, school, graduation year)
            4. Work Experience (years, companies, roles)
            5. Skills (technical and soft skills)
            6. Key Achievements
            
            Then provide a match analysis with the following:
            1. Skills Match (what skills match the job requirements)
            2. Experience Match (how their experience aligns with the job)
            3. Missing Requirements (what key job requirements they may be lacking)
            4. Overall Match Score (0-100%)
            
            Format your response as structured information.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.template)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from a DOCX file"""
        doc = docx.Document(docx_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    
    def extract_text_from_file(self, file_path):
        """Extract text from PDF or DOCX file"""
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            raise ValueError("Unsupported file format. Please use PDF, DOCX, or TXT files.")
    
    def parse(self, resume_path, job_description):
        """Parse resume and analyze against job description"""
        resume_text = self.extract_text_from_file(resume_path)
        return self.chain.run(
            resume_text=resume_text,
            job_description=job_description
        )

def job_description_mode():
    """Job description generation mode"""
    print("\n===== Job Description Generator =====\n")
    
    title = input("Enter job title: ")
    company = input("Enter company name: ")
    
    keywords = []
    print("Enter job keywords (one per line, enter blank line when done):")
    while True:
        keyword = input("> ")
        if not keyword:
            break
        keywords.append(keyword)
    
    experience = input("Enter required experience (e.g., '2-3 years'): ")
    
    # Generate job description
    generator = JobDescriptionGenerator()
    print("\nGenerating job description...")
    description = generator.generate(
        title,
        company,
        ", ".join(keywords),
        experience
    )
    
    # Save job description
    save_path = f"{title.replace(' ', '_').lower()}_job_description.md"
    with open(save_path, "w") as f:
        f.write(description)
    
    # Display job description
    print("\n===== Generated Job Description =====\n")
    print(description)
    print(f"\nSaved to: {save_path}")
    
    return description

def resume_evaluation_mode(job_description=None):
    """Resume evaluation mode"""
    print("\n===== Resume Evaluation =====\n")
    
    # Get job description if not provided
    if not job_description:
        jd_path = input("Enter path to job description file (or leave blank to enter manually): ")
        if jd_path:
            with open(jd_path, 'r') as f:
                job_description = f.read()
        else:
            print("Enter job description (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            job_description = '\n'.join(lines)
    
    # Get resume path
    resume_path = input("Enter path to resume file (PDF, DOCX, or TXT): ")
    
    # Parse resume
    parser = ResumeParser()
    print("\nAnalyzing resume...")
    analysis = parser.parse(resume_path, job_description)
    
    # Display analysis
    print("\n===== Resume Analysis =====\n")
    print(analysis)
    
    # Ask for decision
    decision = input("\nWould you like to move forward with this candidate? (y/n): ").lower()
    
    if decision.startswith('y'):
        print("Candidate marked for interview process!")
        interview_dates = input("Enter available interview dates/times (comma separated): ")
        print(f"Interview availability noted: {interview_dates}")
        return True, analysis
    else:
        print("Candidate rejected.")
        return False, analysis

def main():
    try:
        # Validate API keys
        if not OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY not found in .env file")
            return
        
        print("===== Recruiter Assistant =====")
        print("1. Generate Job Description")
        print("2. Evaluate Resume")
        print("3. Complete Workflow (Generate + Evaluate)")
        choice = input("Select mode: ")
        
        if choice == "1":
            job_description_mode()
        elif choice == "2":
            resume_evaluation_mode()
        elif choice == "3":
            job_description = job_description_mode()
            input("\nPress Enter to continue to resume evaluation...")
            resume_evaluation_mode(job_description)
        else:
            print("Invalid choice.")
            
    except KeyboardInterrupt:
        print("\nProcess cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()