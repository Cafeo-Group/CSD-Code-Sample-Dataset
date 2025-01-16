from dataclasses import dataclass
from utils.postgres import general_add, general_exists, general_fetch_all

@dataclass
class Organization:
    org_name: str
    eco_name: str
    url: str
    
    def __str__(self):
        return f"{self.org_name} - {self.eco_name} - {self.url}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def add_organization(organization: 'Organization') -> None:
        """Adds an organization to the database.
        
        Args:
            organization (Organization) - The organization to add to the database.
        """
        general_add('organizations', organization.__dict__)
        
    @staticmethod
    def is_organization_in_db(organization: 'Organization') -> bool:
        """Checks if an organization is already in the database.
        
        Args:
            organization (Organization) - The organization to check.
            
        Returns:
            bool: True if the organization is in the database, False otherwise.
        """
        general_exists('organizations', organization.__dict__)
        
    @staticmethod
    def fetch_all_organizations() -> list:
        """Fetches all organizations from the database.
        
        Returns:
            list: A list of all organizations.
        """
        return [Organization(*org) for org in general_fetch_all('organizations')]