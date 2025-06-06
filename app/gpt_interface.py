from openai import OpenAI
import json
import os
from typing import List, Dict, Any

class GPTInterface:
    def __init__(self, api_key: str = None):
        """
        Initialize GPT interface
        
        Args:
            api_key (str): OpenAI API key. If None, will try to get from environment
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass it directly.")
            self.client = OpenAI(api_key=api_key)
    
    def find_relevant_jobs(self, resume_data: Dict[str, Any], job_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Use GPT to find relevant jobs based on resume data
        
        Args:
            resume_data (dict): Resume data from resume.json
            job_preferences (dict): User preferences for job search
            
        Returns:
            List[Dict]: List of relevant job opportunities
        """
        
        # Create a prompt for job searching
        prompt = self._create_job_search_prompt(resume_data, job_preferences)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional job search assistant. Your task is to suggest realistic, current job opportunities that match the candidate's profile. Provide specific, actionable job listings with company names, job titles, and brief descriptions. Format your response as a valid JSON array of job objects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse the response
            content = response.choices[0].message.content
            jobs = self._parse_job_response(content)
            
            return jobs
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return []
    
    def _create_job_search_prompt(self, resume_data: Dict[str, Any], job_preferences: Dict[str, Any] = None) -> str:
        """
        Create a detailed prompt for job searching
        """
        
        skills = ", ".join(resume_data.get('skills', []))
        experience_summary = self._summarize_experience(resume_data.get('experience', []))
        education = self._summarize_education(resume_data.get('education', []))
        
        prompt = f"""
Based on the following candidate profile, suggest 5-7 realistic job opportunities that would be a good match:

CANDIDATE PROFILE:
- Name: {resume_data.get('name', 'N/A')}
- Current Title: {resume_data.get('title', 'N/A')}
- Skills: {skills}
- Experience Summary: {experience_summary}
- Education: {education}
- Summary: {resume_data.get('summary', 'N/A')}
"""
        
        if job_preferences:
            prompt += f"\n\nJOB PREFERENCES:\n"
            for key, value in job_preferences.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += """

Please provide a JSON array of job opportunities with the following structure:
[
  {
    "title": "Job Title",
    "company": "Company Name",
    "location": "City, State/Country",
    "salary_range": "$X - $Y",
    "job_type": "Full-time/Part-time/Contract",
    "remote_option": "Remote/Hybrid/On-site",
    "description": "Brief description of the role and key responsibilities",
    "requirements": ["Requirement 1", "Requirement 2", "Requirement 3"],
    "match_score": "85%",
    "why_good_match": "Explanation of why this is a good fit"
  }
]

Focus on real companies and realistic positions. Ensure job titles and requirements align with the candidate's experience level.
"""
        
        return prompt
    
    def _summarize_experience(self, experience_list: List[Dict[str, Any]]) -> str:
        """
        Create a summary of work experience
        """
        if not experience_list:
            return "No experience listed"
        
        summaries = []
        for exp in experience_list:
            title = exp.get('title', 'Unknown')
            company = exp.get('company', 'Unknown')
            duration = f"{exp.get('start_date', 'Unknown')} - {exp.get('end_date', 'Present')}"
            summaries.append(f"{title} at {company} ({duration})")
        
        return "; ".join(summaries)
    
    def _summarize_education(self, education_list: List[Dict[str, Any]]) -> str:
        """
        Create a summary of education
        """
        if not education_list:
            return "No education listed"
        
        summaries = []
        for edu in education_list:
            degree = edu.get('degree', 'Unknown')
            school = edu.get('school', 'Unknown')
            year = edu.get('year', 'Unknown')
            summaries.append(f"{degree} from {school} ({year})")
        
        return "; ".join(summaries)
    
    def _parse_job_response(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse the GPT response and extract job listings
        """
        try:
            # Try to extract JSON from the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                jobs = json.loads(json_str)
                return jobs
            else:
                print("Could not find valid JSON in response")
                return []
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []

def test_gpt_interface():
    """
    Test the GPT interface with sample resume data
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
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "summary": "Experienced software developer with 3 years of experience"
        }
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\nTo test the GPT interface, please set your OpenAI API key:")
        print("$env:OPENAI_API_KEY='your-api-key-here'")
        print("\nOr pass it directly when creating the GPTInterface instance.")
        return
    
    try:
        # Initialize GPT interface
        gpt = GPTInterface()
        
        # Search for jobs
        print("Searching for relevant jobs...")
        jobs = gpt.find_relevant_jobs(resume_data)
        
        if jobs:
            print(f"\nFound {len(jobs)} job opportunities:")
            for i, job in enumerate(jobs, 1):
                print(f"\n{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"   Location: {job.get('location', 'N/A')}")
                print(f"   Match Score: {job.get('match_score', 'N/A')}")
                print(f"   Why Good Match: {job.get('why_good_match', 'N/A')}")
        else:
            print("No jobs found or error occurred.")
            
    except Exception as e:
        print(f"Error testing GPT interface: {e}")

if __name__ == "__main__":
    test_gpt_interface()

