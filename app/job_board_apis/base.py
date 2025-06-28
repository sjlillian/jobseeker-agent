from abc import ABC, abstractmethod

class JobBoardAPI(ABC):

    @abstractmethod
    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for jobs. Must be implemented by subclasses.
        
        Args:
            query (str): Job search query/keywords
            location (str): Location to search in
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[Dict]: List of standardized job objects
        """
        pass
