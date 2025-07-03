import requests
from job_board_apis.base import JobAPI
import yaml
import json

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class JoobleAPI(JobAPI):
    def __init__(self):
        self.api_key = config['jooble']['api_key']
        self.url = f"https://jooble.org/api/{self.api_key}"
        

    def search_jobs(self, resume_data: dict[str, any]):
        """
        Search for jobs on Jooble

        Args:
            query (str): Keywords to search for
            location (str): Location to search in
            **kwargs: Additional parameters to pass to the API

        Returns:
            list[dict]: List of standardized job objects
        """
        print("🔍 Searching for jobs on Jooble...")
        headers = {"Content-type": "application/json"}
        body = {
            "keywords": " OR ".join(resume_data.get('skills')),
            "location": resume_data.get('location'),
            "radius": "25", # Radius in kilometers
            "searchMode": "2" # Broad search
        }
        response = requests.post(self.url, json=body, headers=headers)

        results = response.json().get("jobs", [])

        print(f"Found {len(results)} jobs on Jooble.")
        return [
            {
                "title": job["title"],
                "company": job.get("company", "Unknown"),
                "description": job["snippet"],
                "url": job["link"],
                "location": job.get("location", "N/A"),
            }
            for job in results
        ]
