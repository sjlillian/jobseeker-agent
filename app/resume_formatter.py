import requests
import json
import os
from typing import Dict, Any
from jinja2 import Template

class OllamaResumeFormatter:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize Ollama interface for resume formatting
        
        Args:
            ollama_url (str): URL of the Ollama server
        """
        self.ollama_url = ollama_url
        
    def check_ollama_connection(self) -> bool:
        """
        Check if Ollama is running and accessible
        
        Returns:
            bool: True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def tailor_resume_for_job(self, resume_data: Dict[str, Any], job_details: Dict[str, Any], model: str = "llama2") -> Dict[str, Any]:
        """
        Use Ollama to tailor a resume for a specific job
        
        Args:
            resume_data (dict): Original resume data
            job_details (dict): Job posting details
            model (str): Ollama model to use
            
        Returns:
            Dict[str, Any]: Tailored resume data
        """
        
        # Check connection first
        if not self.check_ollama_connection():
            print("Error: Cannot connect to Ollama. Make sure it's running on http://localhost:11434")
            return resume_data
        
        # Create prompt for resume tailoring
        prompt = self._create_tailoring_prompt(resume_data, job_details)
        
        try:
            # Make request to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2000
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                tailored_content = result.get('response', '')
                
                # Parse the tailored resume
                tailored_resume = self._parse_tailored_resume(tailored_content, resume_data)
                return tailored_resume
            else:
                print(f"Error from Ollama: {response.status_code}")
                return resume_data
                
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return resume_data
    
    def _create_tailoring_prompt(self, resume_data: Dict[str, Any], job_details: Dict[str, Any]) -> str:
        """
        Create a prompt for Ollama to tailor the resume
        """
        
        prompt = f"""
You are a professional resume writer. Your task is to tailor a resume for a specific job posting.

ORIGINAL RESUME:
Name: {resume_data.get('name', 'N/A')}
Title: {resume_data.get('title', 'N/A')}
Summary: {resume_data.get('summary', 'N/A')}
Skills: {', '.join(resume_data.get('skills', []))}

Experience:
"""
        
        for exp in resume_data.get('experience', []):
            prompt += f"- {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')})\n"
            for desc in exp.get('description', []):
                prompt += f"  * {desc}\n"
        
        prompt += f"""

TARGET JOB:
Title: {job_details.get('title', 'N/A')}
Company: {job_details.get('company', 'N/A')}
Description: {job_details.get('description', 'N/A')}
Requirements: {', '.join(job_details.get('requirements', []))}

PLEASE PROVIDE:
1. A tailored professional summary that highlights relevant experience for this specific role
2. A prioritized skills list that emphasizes the most relevant skills for this job
3. Rewritten experience descriptions that better align with the job requirements
4. Suggest any additional keywords that should be included

Format your response as structured text with clear sections:

TAILORED SUMMARY:
[Your tailored summary here]

PRIORITIZED SKILLS:
[Comma-separated list of skills in order of relevance]

TAILORED EXPERIENCE:
[For each job, provide improved descriptions]

KEYWORDS TO INCLUDE:
[Additional relevant keywords]

Keep the core facts accurate but emphasize aspects most relevant to the target position.
"""
        
        return prompt
    
    def _parse_tailored_resume(self, ollama_response: str, original_resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Ollama's response and create a tailored resume
        """
        tailored_resume = original_resume.copy()
        
        try:
            # Extract sections from the response
            sections = self._extract_sections(ollama_response)
            
            # Update summary if provided
            if 'TAILORED SUMMARY' in sections:
                tailored_resume['summary'] = sections['TAILORED SUMMARY'].strip()
            
            # Update skills if provided
            if 'PRIORITIZED SKILLS' in sections:
                skills_text = sections['PRIORITIZED SKILLS'].strip()
                skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                if skills:
                    tailored_resume['skills'] = skills
            
            # Add keywords if provided
            if 'KEYWORDS TO INCLUDE' in sections:
                keywords_text = sections['KEYWORDS TO INCLUDE'].strip()
                keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
                if keywords:
                    # Add to skills if not already there
                    existing_skills = set(tailored_resume.get('skills', []))
                    for keyword in keywords:
                        if keyword not in existing_skills:
                            tailored_resume['skills'].append(keyword)
            
            return tailored_resume
            
        except Exception as e:
            print(f"Error parsing Ollama response: {e}")
            return original_resume
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections from Ollama's structured response
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Check if this is a section header
            if line.endswith(':') and line.upper() == line:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line[:-1]  # Remove the colon
                current_content = []
            elif current_section and line:
                current_content.append(line)
        
        # Save the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

def test_ollama_interface():
    """
    Test the Ollama interface
    """
    # Load resume data
    try:
        with open('data/resume.json', 'r') as f:
            resume_data = json.load(f)
    except FileNotFoundError:
        print("Resume file not found. Using sample data.")
        resume_data = {
            "name": "John Doe",
            "title": "Software Developer",
            "summary": "Experienced software developer with 3 years of experience in web development",
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "experience": [
                {
                    "title": "Software Developer",
                    "company": "Tech Corp",
                    "start_date": "2021",
                    "end_date": "Present",
                    "description": ["Developed web applications", "Collaborated with team"]
                }
            ]
        }
    
    # Sample job details
    job_details = {
        "title": "Senior Python Developer",
        "company": "DataTech Solutions",
        "description": "We are looking for a Senior Python Developer to join our data engineering team",
        "requirements": ["Python", "Django", "PostgreSQL", "AWS", "Docker"]
    }
    
    # Initialize Ollama interface
    ollama = OllamaResumeFormatter()
    
    # Test connection
    print("Testing Ollama connection...")
    if ollama.check_ollama_connection():
        print("✓ Ollama is accessible")
        
        # Test resume tailoring
        print("\nTailoring resume for job...")
        tailored_resume = ollama.tailor_resume_for_job(resume_data, job_details)
        
        print("\n--- ORIGINAL SUMMARY ---")
        print(resume_data.get('summary', 'N/A'))
        
        print("\n--- TAILORED SUMMARY ---")
        print(tailored_resume.get('summary', 'N/A'))
        
        print("\n--- ORIGINAL SKILLS ---")
        print(', '.join(resume_data.get('skills', [])))
        
        print("\n--- TAILORED SKILLS ---")
        print(', '.join(tailored_resume.get('skills', [])))
        
    else:
        print("✗ Cannot connect to Ollama")
        print("Make sure Ollama is installed and running:")
        print("1. Install Ollama from https://ollama.ai")
        print("2. Run: ollama serve")
        print("3. Pull a model: ollama pull llama2")

if __name__ == "__main__":
    test_ollama_interface()

