from openai import OpenAI
import json
import os
from typing import List, Dict, Any
from job_board_apis import JobBoardAggregator

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
        
        # Initialize job board aggregator
        self.job_aggregator = JobBoardAggregator()
    
    def find_relevant_jobs(self, resume_data: Dict[str, Any], job_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Fetch real jobs from job boards and use GPT to analyze and rank them based on resume data
        
        Args:
            resume_data (dict): Resume data from resume.json
            job_preferences (dict): User preferences for job search
            
        Returns:
            List[Dict]: List of analyzed and ranked job opportunities
        """
        
        # Step 1: Determine search query from resume and preferences
        search_query = self._generate_search_query(resume_data, job_preferences)
        location = self._extract_location(resume_data, job_preferences)
        
        print(f"🔍 Searching job boards for: '{search_query}' in '{location}'")
        
        # Step 2: Fetch real jobs from job boards
        raw_jobs = self.job_aggregator.search_all_boards(
            query=search_query,
            location=location,
            limit_per_board=15  # Get more jobs to have better selection
        )
        
        if not raw_jobs:
            print("⚠️ No jobs found from job boards. This might be due to:")
            print("   - API keys not configured")
            print("   - Network connectivity issues")
            print("   - No matching jobs available")
            return []
        
        print(f"📊 Found {len(raw_jobs)} jobs from job boards")
        
        # Step 3: Use GPT to analyze and rank the jobs
        print("🤖 Analyzing jobs with AI for best matches...")
        analyzed_jobs = self._analyze_jobs_with_gpt(resume_data, raw_jobs, job_preferences)
        
        return analyzed_jobs
    
    def configure_job_apis(self, adzuna_app_id: str = None, adzuna_app_key: str = None, 
                          jsearch_api_key: str = None, usajobs_email: str = None):
        """
        Configure job board API credentials
        
        Args:
            adzuna_app_id (str): Adzuna API app ID
            adzuna_app_key (str): Adzuna API app key
            jsearch_api_key (str): JSearch RapidAPI key
            usajobs_email (str): Email for USAJobs API
        """
        if adzuna_app_id and adzuna_app_key:
            self.job_aggregator.configure_adzuna(adzuna_app_id, adzuna_app_key)
            print("✅ Adzuna API configured")
        
        if jsearch_api_key:
            self.job_aggregator.configure_jsearch(jsearch_api_key)
            print("✅ JSearch API configured")
        
        if usajobs_email:
            self.job_aggregator.configure_usajobs(usajobs_email)
            print("✅ USAJobs API configured")
    
    def _create_job_search_prompt(self, resume_data: Dict[str, Any], job_preferences: Dict[str, Any] = None) -> str:
        """
        Create a detailed prompt for job searching
        """
        
        skills = ", ".join(resume_data.get('skills', []))
        experience_summary = self._summarize_experience(resume_data.get('experience', []))
        education = self._summarize_education(resume_data.get('education', []))
        location = resume_data.get('location', 'Unknown')
        
        prompt = f"""
Based on the following candidate profile, suggest 5-7 realistic job opportunities that would be a good match:

CANDIDATE PROFILE:
- Name: {resume_data.get('name', 'N/A')}
- Current Title: {resume_data.get('title', 'N/A')}
- current Location: {location}
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
    "url": "Link to job listing",
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

The candidate is located in: {location}.

Focus ONLY on job listings that are:
- **Based in or near this location**
- OR offer **fully remote work options**
- Avoid listings based in unrelated states, cities, or countries unless fully remote

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

    