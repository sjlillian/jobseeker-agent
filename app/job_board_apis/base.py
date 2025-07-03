from abc import ABC, abstractmethod

class JobAPI(ABC):

    @abstractmethod
    def search_jobs(self, resume_data: dict[str, any]) -> list[dict[str, any]]:
        """
        Search for jobs. Must be implemented by subclasses.
        
        Args:
            query (str): Job search query/keywords
            location (str): Location to search in
            limit (int): Maximum number of jobs to return
            
        Returns:
            list[dict]: list of standardized job objects
        """
        pass
