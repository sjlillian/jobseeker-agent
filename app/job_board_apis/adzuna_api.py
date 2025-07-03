import requests
from job_board_apis.base import JobAPI
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class AdzunaAPI(JobAPI):
    def __init__(self):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.api_id = config['adzuna']['api_id']
        self.api_key = config['adzuna']['api_key']

    def search_jobs(self, resume_data: dict[str, any]):
        """
        Search for jobs on Adzuna
        https://developer.adzuna.com/docs/getting-started

        Args:
            query (str): Job search query/keywords
            location (str, optional): Location to search in. Defaults to "us".
            **kwargs: Additional parameters to pass to Adzuna API

        Returns:
            list[dict]: List of job objects with keys:
                title (str)
                company (str)
                description (str)
                location (str)
                url (str)
        """
        print("🔍 Searching for jobs on Adzuna...")
        url = f"{self.base_url}/{location}/search/1"
        params = {
            "api_id": self.api_id,
            "api_key": self.api_key,
            "what": query,
            "content-type": "application/json",
        }
        params.update(kwargs)
        response = requests.get(url, params=params)
        results = response.json().get("results", [])
        return [
            {
                "title": job["title"],
                "company": job["company"]["display_name"],
                "description": job["description"],
                "location": job["location"]["display_name"],
                "url": job["redirect_url"]
            }
            for job in results
        ]
