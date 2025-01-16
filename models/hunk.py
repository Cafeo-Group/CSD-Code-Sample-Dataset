from dataclasses import dataclass
from utils.postgres import db_conn, general_add, general_exists, general_fetch_all
from typing import List

@dataclass
class Hunk:
    id: int
    old_start: int
    old_lenght: int
    new_start: int
    new_lenght: int
    lines: list[str]
    
    def __str__(self):
        return f"""{self.id} - {self.old_start} - {self.old_lenght} - {self.new_start} - {self.new_lenght} - {self.lines}"""
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def add_hunk(hunk: 'Hunk') -> None:
        """Adds a Hunk to the database.
        
        Args:
            hunk (Hunk) - The Hunk to add to the database.
            
        Returns:
            None
        """
        
        general_add('hunks', hunk.to_dict())
        
    @staticmethod
    def exists(hunk: 'Hunk') -> bool:
        """Checks if a Hunk exists in the database.
        
        Args:
            hunk (Hunk) - The Hunk to check for in the database.
            
        Returns:
            bool: True if the Hunk exists in the database, False otherwise.
        """
        
        return general_exists('hunks', hunk.to_dict())
    
    @staticmethod
    def fetch_all() -> List['Hunk']:
        """Fetches all Hunks from the database.
        
        Returns:
            list: A list of all Hunks in the database.
        """
        
        return general_fetch_all('hunks')