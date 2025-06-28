import requests
from app.job_apis.base import JobAPI

class AdzunaAPI(JobAPI):
    def __init__(self, app_id: str, app_key: str):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.app_id = adzuna_app_id
        self.app_key = adzuna_app_key

    def search_jobs(self, query: str, location: str = "us", **kwargs):
        url = f"{self.base_url}/{location}/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
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
