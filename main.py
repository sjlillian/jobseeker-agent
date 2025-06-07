#!/usr/bin/env python3
"""
Job Seeker Agent - Main Application

This application helps users find relevant jobs and create tailored resumes:
1. Loads user's resume data
2. Uses OpenAI to find relevant job opportunities
3. Allows user to select jobs of interest
4. Uses Ollama to tailor resume for selected jobs
5. Generates PDF resumes for each selected job

Author: Job Seeker Agent
Date: 2025
"""

import os
import json
import sys
from typing import List, Dict, Any

# Add the app directory to the path
sys.path.append('app')

# Import our modules
from gpt_interface import GPTInterface
from resume_formatter import OllamaResumeFormatter
from resume_loader import ResumeRenderer

try:
    from html_to_pdf import html_to_pdf
except ImportError:
    print("Warning: PDF conversion not available. Install wkhtmltopdf or setup alternative.")
    html_to_pdf = None

class JobSeekerAgent:
    def __init__(self):
        """
        Initialize the Job Seeker Agent
        """
        self.resume_renderer = ResumeRenderer()
        self.gpt_interface = None
        self.ollama_formatter = OllamaResumeFormatter()
        self.resume_data = {}
        
    def load_resume(self, resume_path: str = "data/resume.json") -> bool:
        """
        Load the user's resume data
        
        Args:
            resume_path (str): Path to resume JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.resume_data = self.resume_renderer.load_resume_data(resume_path)
        
        if not self.resume_data:
            print("❌ Failed to load resume data")
            return False
        
        print(f"✅ Loaded resume for: {self.resume_data.get('name', 'Unknown')}")
        return True
    
    def setup_openai(self, api_key: str = None) -> bool:
        """
        Setup OpenAI interface
        
        Args:
            api_key (str): OpenAI API key. If None, tries environment variable
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.gpt_interface = GPTInterface(api_key)
            print("✅ OpenAI interface ready")
            return True
        except Exception as e:
            print(f"❌ Failed to setup OpenAI: {e}")
            return False
    
    def find_jobs(self, job_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find relevant jobs using OpenAI
        
        Args:
            job_preferences (dict): User job preferences
            
        Returns:
            List[Dict]: List of relevant job opportunities
        """
        if not self.gpt_interface:
            print("❌ OpenAI not configured. Please set up OpenAI first.")
            return []
        
        if not self.resume_data:
            print("❌ Resume data not loaded. Please load resume first.")
            return []
        
        print("🔍 Searching for relevant jobs...")
        jobs = self.gpt_interface.find_relevant_jobs(self.resume_data, job_preferences)
        
        if jobs:
            print(f"✅ Found {len(jobs)} job opportunities")
        else:
            print("❌ No jobs found")
            
        return jobs
    
    def display_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """
        Display job opportunities to the user
        
        Args:
            jobs (list): List of job opportunities
        """
        if not jobs:
            print("No jobs to display.")
            return
        
        print("\n" + "="*60)
        print("FOUND JOB OPPORTUNITIES")
        print("="*60)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}] {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"    🔗 Job Link: {job.get('url', 'N/A')}")
            print(f"    📍 Location: {job.get('location', 'N/A')}")
            print(f"    💰 Salary: {job.get('salary_range', 'N/A')}")
            print(f"    🏢 Type: {job.get('job_type', 'N/A')} | {job.get('remote_option', 'N/A')}")
            print(f"    📊 Match Score: {job.get('match_score', 'N/A')}")
            print(f"    📄 Description: {job.get('description', 'N/A')[:100]}...")
            print(f"    ✅ Why Good Match: {job.get('why_good_match', 'N/A')[:100]}...")
    
    def select_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allow user to select jobs they're interested in
        
        Args:
            jobs (list): List of available jobs
            
        Returns:
            List[Dict]: List of selected jobs
        """
        if not jobs:
            return []
        
        print("\n" + "="*60)
        print("SELECT JOBS FOR TAILORED RESUMES")
        print("="*60)
        print("Enter the numbers of jobs you want to create tailored resumes for.")
        print("Example: 1,3,5 or 1 2 3")
        print("Enter 'all' to select all jobs, or 'none' to skip.")
        
        while True:
            try:
                selection = input("\nYour selection: ").strip().lower()
                
                if selection == 'none':
                    return []
                
                if selection == 'all':
                    return jobs
                
                # Parse selection
                if ',' in selection:
                    indices = [int(x.strip()) for x in selection.split(',')]
                else:
                    indices = [int(x) for x in selection.split()]
                
                # Validate indices
                selected_jobs = []
                for idx in indices:
                    if 1 <= idx <= len(jobs):
                        selected_jobs.append(jobs[idx - 1])
                    else:
                        print(f"Warning: Invalid job number {idx}. Skipping.")
                
                if selected_jobs:
                    return selected_jobs
                else:
                    print("No valid jobs selected. Please try again.")
                    
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas or spaces.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return []
    
    def create_tailored_resumes(self, selected_jobs: List[Dict[str, Any]]) -> List[str]:
        """
        Create tailored resumes for selected jobs
        
        Args:
            selected_jobs (list): List of selected job opportunities
            
        Returns:
            List[str]: List of generated resume file paths
        """
        if not selected_jobs:
            return []
        
        print("\n" + "="*60)
        print("CREATING TAILORED RESUMES")
        print("="*60)
        
        resume_files = []
        
        for i, job in enumerate(selected_jobs, 1):
            print(f"\n[{i}/{len(selected_jobs)}] Creating resume for {job.get('title', 'N/A')} at {job.get('company', 'N/A')}...")
            
            # Tailor resume using Ollama
            tailored_resume = self.ollama_formatter.tailor_resume_for_job(self.resume_data, job)
            
            # Generate filename
            company = job.get('company', 'Company').replace(' ', '_').replace(',', '')
            title = job.get('title', 'Position').replace(' ', '_').replace(',', '')
            filename = f"resume_{company}_{title}.html"
            output_path = f"data/output/{filename}"
            
            # Render HTML
            success = self.resume_renderer.render_and_save(tailored_resume, output_path)
            
            if success:
                resume_files.append(output_path)
                print(f"    ✅ HTML resume saved: {output_path}")
                
                # Try to create PDF if available
                if html_to_pdf:
                    pdf_path = output_path.replace('.html', '.pdf')
                    try:
                        with open(output_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        if html_to_pdf(html_content, pdf_path):
                            print(f"    ✅ PDF resume saved: {pdf_path}")
                        else:
                            print(f"    ⚠️  PDF conversion failed for {pdf_path}")
                    except Exception as e:
                        print(f"    ⚠️  PDF conversion error: {e}")
                else:
                    print(f"    ℹ️  PDF conversion not available")
            else:
                print(f"    ❌ Failed to create resume for {job.get('company', 'N/A')}")
        
        return resume_files
    
    def run_interactive(self):
        """
        Run the application in interactive mode
        """
        print("\n" + "="*60)
        print("JOB SEEKER AGENT")
        print("Find jobs and create tailored resumes")
        print("="*60)
        
        # Step 1: Load resume
        print("\nStep 1: Loading your resume...")
        if not self.load_resume():
            print("Please ensure your resume.json file exists in the data/ directory.")
            return
        
        # Step 2: Setup OpenAI (optional)
        print("\nStep 2: Setting up job search...")
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("OpenAI API key not found in environment variables.")
            print("You can:")
            print("1. Set OPENAI_API_KEY environment variable")
            print("2. Enter your API key now (not recommended for security)")
            print("3. Skip job search and only test resume generation")
            
            choice = input("\nChoose an option (1/2/3): ").strip()
            
            if choice == '2':
                api_key = input("Enter your OpenAI API key: ").strip()
            elif choice == '3':
                print("Skipping job search. You can test resume generation with sample data.")
                api_key = None
            else:
                print("Please set the OPENAI_API_KEY environment variable and try again.")
                return
        
        if api_key:
            if not self.setup_openai(api_key):
                return
            
            # Step 3: Find jobs
            print("\nStep 3: Searching for relevant jobs...")
            jobs = self.find_jobs()
            
            if jobs:
                # Step 4: Display and select jobs
                self.display_jobs(jobs)
                selected_jobs = self.select_jobs(jobs)
                
                if selected_jobs:
                    print(f"\nSelected {len(selected_jobs)} jobs for tailored resumes.")
                    
                    # Step 5: Create tailored resumes
                    resume_files = self.create_tailored_resumes(selected_jobs)
                    
                    if resume_files:
                        print(f"\n🎉 Successfully created {len(resume_files)} tailored resumes!")
                        print("\nFiles created:")
                        for file_path in resume_files:
                            print(f"  📄 {file_path}")
                    else:
                        print("\n❌ No resumes were created.")
                else:
                    print("\nNo jobs selected. Exiting.")
            else:
                print("\nNo jobs found. You can still test resume generation.")
        
        # Test resume generation
        print("\n" + "="*60)
        print("TESTING RESUME GENERATION")
        print("="*60)
        
        test_job = {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "description": "We're looking for a senior Python developer",
            "requirements": ["Python", "Django", "AWS", "PostgreSQL"]
        }
        
        print("Creating a test tailored resume...")
        test_resumes = self.create_tailored_resumes([test_job])
        
        if test_resumes:
            print("\n✅ Test resume generation successful!")
        else:
            print("\n❌ Test resume generation failed.")

def main():
    """
    Main entry point
    """
    try:
        agent = JobSeekerAgent()
        agent.run_interactive()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()

