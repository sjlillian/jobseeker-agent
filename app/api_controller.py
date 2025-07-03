from job_board_apis.jooble_api import JoobleAPI
from job_board_apis.adzuna_api import AdzunaAPI

class JobBoardController:
    def __init__(self):
        self.apis = {}
        self.is_initialized = self.initialize()

    def initialize(self) -> bool:
        try:
            self.apis["JoobleAPI"] = JoobleAPI()
            self.apis["AdzunaAPI"] = AdzunaAPI()
            # Add more API classes here
            print("✅ Job board APIs ready")
            return True
        except Exception as e:
            print(f"❌ Failed to setup job board APIs: {e}")
            return False

    def find_jobs(self, resume_data: dict[str, any] = None) -> dict[str, any]:
        if not self.is_initialized:
            return []
        
        print("🔍 Searching for relevant jobs...")
        return {**self.apis["JoobleAPI"].search_jobs(resume_data), **self.apis["AdzunaAPI"].search_jobs(resume_data)}