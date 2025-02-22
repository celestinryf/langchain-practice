from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
import requests
import json
import os
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Get API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PYJOBS_API_KEY = os.getenv("PYJOBS_API_KEY")

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

class PyJobsPoster(BaseTool):
    name = "pyjobs_poster"
    description = "Posts a job to PyJobs board"
    
    def _run(self, job_data: Dict[str, Any]) -> str:
        """Post a job to PyJobs"""
        url = "https://pyjobs.com/api/jobs/"
        headers = {
            "Authorization": f"Token {PYJOBS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": job_data["title"],
            "company_name": job_data["company"],
            "description": job_data["description"],
            "requirements": job_data.get("requirements", ""),
            "job_type": job_data.get("job_type", "full-time"),
            "remote": job_data.get("remote", True),
            "country": job_data.get("country", "United States"),
            "state": job_data.get("state", ""),
            "city": job_data.get("city", ""),
            "contact_email": job_data.get("contact_email", "")
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return f"Job posted successfully. Job ID: {result.get('id')}"
        except requests.exceptions.RequestException as e:
            return f"Error posting job: {str(e)}"


def get_user_input():
    """Get job details from user input"""
    print("\n===== Job Posting Console Application =====\n")
    
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
    job_type = input("Enter job type (full-time, part-time, contract): ")
    remote_input = input("Is this position remote? (y/n): ").lower()
    remote = remote_input.startswith('y')
    
    country = input("Enter country (default: United States): ") or "United States"
    state = input("Enter state/province: ")
    city = input("Enter city: ")
    contact_email = input("Enter contact email: ")
    
    return {
        "title": title,
        "company": company,
        "keywords": keywords,
        "experience": experience,
        "job_type": job_type,
        "remote": remote,
        "country": country,
        "state": state,
        "city": city,
        "contact_email": contact_email
    }


def main():
    try:
        # Validate API keys
        if os.environ.get("OPENAI_API_KEY") == "your-openai-api-key":
            print("Error: Please set your OpenAI API key")
            return
            
        if PYJOBS_API_KEY == "your-pyjobs-api-key":
            print("Error: Please set your PyJobs API key")
            return
        
        # Get job details from user
        job_details = get_user_input()
        
        # Create job description generator
        desc_generator = JobDescriptionGenerator()
        
        # Generate job description
        print("\nGenerating job description...")
        description = desc_generator.generate(
            job_details["title"],
            job_details["company"],
            ", ".join(job_details["keywords"]),
            job_details["experience"]
        )
        
        # Preview job description
        print("\n===== Generated Job Description =====\n")
        print(description)
        print("\n=====================================\n")
        
        # Confirm posting
        confirmation = input("Do you want to post this job? (y/n): ").lower()
        if not confirmation.startswith('y'):
            print("Job posting cancelled.")
            return
        
        # Add description to job details
        job_details["description"] = description
        
        # Post to PyJobs
        print("\nPosting job to PyJobs...")
        poster = PyJobsPoster()
        result = poster._run(job_details)
        
        print(result)
        
    except KeyboardInterrupt:
        print("\nProcess cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")


if __name__ == "__main__":
    main()