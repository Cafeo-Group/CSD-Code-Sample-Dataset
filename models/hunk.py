from dataclasses import dataclass
from utils.postgres import general_add, general_exists, general_fetch_all, general_add_in_batches
from typing import List, Optional
import re
import subprocess
import os

@dataclass
class Hunk:
    id: int
    file_name: str    
    repo_name: str
    org_name: str
    sha: str
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    lines: list[str]
    old_name: Optional[str] = None
    new_name: Optional[str] = None 
    
    def __str__(self):
        return f"""
        {self.change_type} {self.file_mode}
        {self.index_info} 
        --- {self.old_name}
        +++ {self.new_name}
        
        @@ -{self.old_start},{self.old_length} +{self.new_start},{self.new_length} @@
        
        {'\n'.join(self.lines)}
        """
    
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
        hunk_dict = hunk.__dict__
        if not hunk_dict["id"]: del hunk_dict['id']
        
        general_add('hunks', hunk_dict)
        
    @staticmethod
    def add_hunks_in_batches(hunks: List['Hunk']) -> None:
        """Adds a list of Hunks to the database in batches.
        
        Args:
            hunks (list) - The list of Hunks to add to the database.
            
        Returns:
            None
        """
        hunks_in_dict = []
        for hunk in hunks:
            hunk_dict = hunk.__dict__
            del hunk_dict['id']
            hunks_in_dict.append(hunk_dict)
        
        general_add_in_batches('hunks', hunks_in_dict)
    
    @staticmethod
    def exists(hunk: 'Hunk') -> bool:
        """Checks if a Hunk exists in the database.
        
        Args:
            hunk (Hunk) - The Hunk to check for in the database.
            
        Returns:
            bool: True if the Hunk exists in the database, False otherwise.
        """
        
        return general_exists('hunks', hunk.__dict__)
    
    @staticmethod
    def fetch_all() -> List['Hunk']:
        """Fetches all Hunks from the database.
        
        Returns:
            list: A list of all Hunks in the database.
        """
        
        return general_fetch_all('hunks')
