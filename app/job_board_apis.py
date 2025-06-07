import requests
import json
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode, quote
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobBoardAPI:
    """
    Base class for job board API integrations
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for jobs. To be implemented by subclasses.
        
        Args:
            query (str): Job search query/keywords
            location (str): Location to search in
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[Dict]: List of standardized job objects
        """
        raise NotImplementedError("Subclasses must implement search_jobs method")
    
    def standardize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw job data to standardized format
        
        Args:
            raw_job (dict): Raw job data from API
            
        Returns:
            Dict: Standardized job object
        """
        raise NotImplementedError("Subclasses must implement standardize_job method")

class AdzunaAPI(JobBoardAPI):
    """
    Adzuna job search API integration
    Free tier: 1000 calls/month
    """
    def __init__(self, app_id: str = None, app_key: str = None):
        super().__init__()
        self.app_id = app_id or "YOUR_ADZUNA_APP_ID"  # Users need to replace this
        self.app_key = app_key or "YOUR_ADZUNA_APP_KEY"  # Users need to replace this
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search"
    
    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search jobs using Adzuna API
        """
        if self.app_id == "YOUR_ADZUNA_APP_ID" or self.app_key == "YOUR_ADZUNA_APP_KEY":
            logger.warning("Adzuna API credentials not configured. Returning empty results.")
            return []
        
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'what': query,
            'results_per_page': min(limit, 50),
            'content-type': 'application/json'
        }
        
        if location:
            params['where'] = location
        
        try:
            response = self.session.get(f"{self.base_url}/1", params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for raw_job in data.get('results', []):
                standardized_job = self.standardize_job(raw_job)
                if standardized_job:
                    jobs.append(standardized_job)
            
            logger.info(f"Adzuna: Found {len(jobs)} jobs for query '{query}'")
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"Adzuna API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Adzuna processing error: {e}")
            return []
    
    def standardize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert Adzuna job data to standardized format
        """
        try:
            return {
                'title': raw_job.get('title', ''),
                'company': raw_job.get('company', {}).get('display_name', ''),
                'location': raw_job.get('location', {}).get('display_name', ''),
                'description': raw_job.get('description', ''),
                'url': raw_job.get('redirect_url', ''),
                'salary_min': raw_job.get('salary_min'),
                'salary_max': raw_job.get('salary_max'),
                'job_type': 'Full-time',  # Adzuna doesn't always specify
                'remote_option': 'Unknown',
                'posted_date': raw_job.get('created'),
                'source': 'Adzuna',
                'raw_data': raw_job  # Keep original for debugging
            }
        except Exception as e:
            logger.error(f"Error standardizing Adzuna job: {e}")
            return None

class JSearchAPI(JobBoardAPI):
    """
    JSearch API integration (RapidAPI)
    Free tier: 150 requests/month
    """
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or "YOUR_RAPIDAPI_KEY"  # Users need to replace this
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.session.headers.update({
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        })
    
    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search jobs using JSearch API
        """
        if self.api_key == "YOUR_RAPIDAPI_KEY":
            logger.warning("JSearch API key not configured. Returning empty results.")
            return []
        
        params = {
            'query': f"{query} {location}".strip(),
            'page': '1',
            'num_pages': '1',
            'date_posted': 'all'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for raw_job in data.get('data', [])[:limit]:
                standardized_job = self.standardize_job(raw_job)
                if standardized_job:
                    jobs.append(standardized_job)
            
            logger.info(f"JSearch: Found {len(jobs)} jobs for query '{query}'")
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"JSearch API error: {e}")
            return []
        except Exception as e:
            logger.error(f"JSearch processing error: {e}")
            return []
    
    def standardize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert JSearch job data to standardized format
        """
        try:
            # Extract salary information
            salary_info = self._extract_salary(raw_job)
            
            return {
                'title': raw_job.get('job_title', ''),
                'company': raw_job.get('employer_name', ''),
                'location': f"{raw_job.get('job_city', '')}, {raw_job.get('job_state', '')}".strip(', '),
                'description': raw_job.get('job_description', ''),
                'url': raw_job.get('job_apply_link', ''),
                'salary_min': salary_info.get('min'),
                'salary_max': salary_info.get('max'),
                'job_type': raw_job.get('job_employment_type', 'Full-time'),
                'remote_option': 'Remote' if raw_job.get('job_is_remote', False) else 'On-site',
                'posted_date': raw_job.get('job_posted_at_datetime_utc'),
                'requirements': raw_job.get('job_required_skills', []),
                'source': 'JSearch',
                'raw_data': raw_job
            }
        except Exception as e:
            logger.error(f"Error standardizing JSearch job: {e}")
            return None
    
    def _extract_salary(self, raw_job: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """
        Extract salary information from JSearch job data
        """
        try:
            salary_min = raw_job.get('job_min_salary')
            salary_max = raw_job.get('job_max_salary')
            
            return {
                'min': float(salary_min) if salary_min else None,
                'max': float(salary_max) if salary_max else None
            }
        except (ValueError, TypeError):
            return {'min': None, 'max': None}

class USAJobsAPI(JobBoardAPI):
    """
    USAJobs.gov API integration (for government jobs)
    No API key required, but has rate limits
    """
    def __init__(self, email: str = None):
        super().__init__()
        self.email = email or "your-email@example.com"  # Required for API identification
        self.base_url = "https://data.usajobs.gov/api/search"
        self.session.headers.update({
            'Host': 'data.usajobs.gov',
            'User-Agent': f'JobSeekerAgent ({self.email})'
        })
    
    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search jobs using USAJobs API
        """
        params = {
            'Keyword': query,
            'ResultsPerPage': min(limit, 500),
            'Page': 1
        }
        
        if location:
            params['LocationName'] = location
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            search_result = data.get('SearchResult', {})
            for raw_job in search_result.get('SearchResultItems', []):
                standardized_job = self.standardize_job(raw_job)
                if standardized_job:
                    jobs.append(standardized_job)
            
            logger.info(f"USAJobs: Found {len(jobs)} jobs for query '{query}'")
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"USAJobs API error: {e}")
            return []
        except Exception as e:
            logger.error(f"USAJobs processing error: {e}")
            return []
    
    def standardize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert USAJobs data to standardized format
        """
        try:
            match_job = raw_job.get('MatchedObjectDescriptor', {})
            
            # Extract salary
            salary_info = self._extract_government_salary(match_job)
            
            # Extract location
            locations = match_job.get('PositionLocation', [])
            location_str = ""
            if locations:
                first_location = locations[0]
                city = first_location.get('CityName', '')
                state = first_location.get('StateName', '')
                location_str = f"{city}, {state}".strip(', ')
            
            return {
                'title': match_job.get('PositionTitle', ''),
                'company': match_job.get('OrganizationName', 'U.S. Government'),
                'location': location_str,
                'description': match_job.get('UserArea', {}).get('Details', {}).get('JobSummary', ''),
                'url': match_job.get('PositionURI', ''),
                'salary_min': salary_info.get('min'),
                'salary_max': salary_info.get('max'),
                'job_type': 'Full-time',
                'remote_option': 'Government',
                'posted_date': match_job.get('PublicationStartDate'),
                'grade': match_job.get('JobGrade', []),
                'source': 'USAJobs',
                'raw_data': raw_job
            }
        except Exception as e:
            logger.error(f"Error standardizing USAJobs job: {e}")
            return None
    
    def _extract_government_salary(self, match_job: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """
        Extract salary from government job posting
        """
        try:
            remuneration = match_job.get('PositionRemuneration', [])
            if remuneration:
                first_pay = remuneration[0]
                min_salary = first_pay.get('MinimumRange')
                max_salary = first_pay.get('MaximumRange')
                
                return {
                    'min': float(min_salary) if min_salary else None,
                    'max': float(max_salary) if max_salary else None
                }
        except (ValueError, TypeError, IndexError):
            pass
        
        return {'min': None, 'max': None}

class JobBoardAggregator:
    """
    Aggregates results from multiple job board APIs
    """
    def __init__(self):
        self.apis = []
        self.setup_apis()
    
    def setup_apis(self):
        """
        Setup available job board APIs
        """
        # Add APIs here - users can configure with their own API keys
        # For demo purposes, these will return empty results without proper API keys
        self.apis = [
            AdzunaAPI(),
            JSearchAPI(),
            USAJobsAPI()
        ]
    
    def search_all_boards(self, query: str, location: str = "", limit_per_board: int = 10) -> List[Dict[str, Any]]:
        """
        Search across all configured job boards
        
        Args:
            query (str): Job search query
            location (str): Location to search in
            limit_per_board (int): Max jobs per board
            
        Returns:
            List[Dict]: Aggregated job results
        """
        all_jobs = []
        
        for api in self.apis:
            try:
                logger.info(f"Searching {api.__class__.__name__}...")
                jobs = api.search_jobs(query, location, limit_per_board)
                all_jobs.extend(jobs)
                
                # Small delay to be respectful to APIs
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error with {api.__class__.__name__}: {e}")
                continue
        
        # Remove duplicates based on title and company
        unique_jobs = self._deduplicate_jobs(all_jobs)
        
        logger.info(f"Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs
    
    def _deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate jobs based on title and company
        """
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a simple key for deduplication
            key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            
            if key not in seen and job.get('title') and job.get('company'):
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def configure_adzuna(self, app_id: str, app_key: str):
        """
        Configure Adzuna API credentials
        """
        for i, api in enumerate(self.apis):
            if isinstance(api, AdzunaAPI):
                self.apis[i] = AdzunaAPI(app_id, app_key)
                break
    
    def configure_jsearch(self, api_key: str):
        """
        Configure JSearch API credentials
        """
        for i, api in enumerate(self.apis):
            if isinstance(api, JSearchAPI):
                self.apis[i] = JSearchAPI(api_key)
                break
    
    def configure_usajobs(self, email: str):
        """
        Configure USAJobs API email
        """
        for i, api in enumerate(self.apis):
            if isinstance(api, USAJobsAPI):
                self.apis[i] = USAJobsAPI(email)
                break

def test_job_apis():
    """
    Test function for job board APIs
    """
    print("Testing Job Board APIs")
    print("=" * 50)
    
    aggregator = JobBoardAggregator()
    
    # Test search
    query = "software developer"
    location = "Texas"
    
    print(f"Searching for '{query}' in '{location}'...\n")
    
    jobs = aggregator.search_all_boards(query, location, limit_per_board=5)
    
    if jobs:
        print(f"Found {len(jobs)} total jobs:\n")
        
        for i, job in enumerate(jobs[:10], 1):  # Show first 10
            print(f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"   📍 {job.get('location', 'N/A')}")
            print(f"   🌐 Source: {job.get('source', 'N/A')}")
            
            if job.get('salary_min') or job.get('salary_max'):
                salary_min = f"${job.get('salary_min', 0):,.0f}" if job.get('salary_min') else "N/A"
                salary_max = f"${job.get('salary_max', 0):,.0f}" if job.get('salary_max') else "N/A"
                print(f"   💰 Salary: {salary_min} - {salary_max}")
            
            print(f"   🔗 URL: {job.get('url', 'N/A')[:60]}...")
            print()
    else:
        print("No jobs found. This might be due to:")
        print("1. API keys not configured")
        print("2. Network issues")
        print("3. API rate limits")
        print("\nTo configure API keys, check the README for instructions.")

if __name__ == "__main__":
    test_job_apis()

