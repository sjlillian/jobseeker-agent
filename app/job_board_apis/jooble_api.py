import requests
from app.job_apis.base import JobAPI

class JoobleAPI(JobAPI):
    def __init__(self, config: dict):
        self.base_url = "https://jooble.org/api/"
        self.api_key = jooble_api_key

    def search_jobs(self, query: str, location: str = "", **kwargs) -> list[dict]:
        payload = {
            "keywords": query,
            "location": location
        }
        response = requests.post(f"{self.base_url}{self.api_key}", json=payload)
        results = response.json().get("jobs", [])
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
