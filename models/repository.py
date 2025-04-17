from dataclasses import dataclass
from datetime import datetime
from utils.postgres import general_add, general_exists, db_conn
import pandas as pd

@dataclass
class Repository:
    repo_name: str
    eco_name: str
    org_name: str
    stars: int
    forks: int
    watchers: int
    contributors: int
    language: str
    size: float
    loc: float
    archived: bool
    
    def __str__(self):
        return f'{self.repo_name} ({self.eco_name}) - {self.org_name}'
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def add_repository(repo: 'Repository') -> None:
        """Adds a repository to the database.
        
        Args:
            repo (Repository) - The repository to add to the database.
        """
        general_add('repositories', repo.__dict__)
        
    @staticmethod
    def is_repo_in_db(repo_name: str) -> bool:
        """Checks if a repository is in the database.
        
        Args:
            repo_name (str) - The name of the repository to check.
            
        Returns:
            bool - True if the repository is in the database, False otherwise.
        """
        return general_exists('repositories', {'repo_name': repo_name})
    
    @staticmethod
    def fetch_by_name_and_org(repo_name: str, org_name: str) -> 'Repository':
        """Fetches a repository from the database by its name and ecosystem.
        
        Args:
            repo_name (str) - The name of the repository to fetch.
            org_name (str) - The 
            
        Returns:
            Repository - The repository fetched from the database.
        """
        
        conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM repositories WHERE repo_name = '{repo_name}' AND org_name = '{org_name}';")
        
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        repo = Repository.tuple_to_Repository(row)
        return repo
        
        
    @staticmethod
    def tuple_to_Repository(tuple: tuple) -> 'Repository':
        """Converts a tuple to a Repository object.
        
        Args:
            tuple (tuple) - The tuple to convert.
            
        Returns:
            Repository - The Repository object created from the tuple.
        """
        
        return Repository(
            repo_name=tuple[0],
            eco_name=tuple[1],
            org_name=tuple[2],
            stars=tuple[4],
            forks=tuple[5],
            watchers=tuple[6],
            contributors=tuple[7],
            language=tuple[8],
            size=tuple[9],
            loc=tuple[10],
            archived=tuple[32]
        )
    
    @staticmethod
    def csv_row_to_Repository(row: pd.Series) -> 'Repository':
        """Converts a row from a CSV file to a Repository object.
        
        Args:
            row (pd.Series) - The row to convert.
            
        Returns:
            Repository - The Repository object created from the row.
        """
        
        try:
            return Repository(
                repo_name=row['name'],
                eco_name=row['Ecosystem'],
                org_name=row['html_url'].split('/')[3],
                stars=row['Stars'],
                forks=row['Forks'],
                watchers=row['Watchers'],
                contributors=row['Contributors'],
                language=row['Language'],
                size=row['Size (KB)'],
                loc=row['LOC'],
                archived=row['archived']
            )
        except Exception as e:
            print(e)