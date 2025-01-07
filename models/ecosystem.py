from dataclasses import dataclass
from utils.postgres import db_conn, general_add, general_exists, general_fetch_all

@dataclass
class Ecosystem:
    eco_name: str
    
    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def add_ecosystem(ecosystem: 'Ecosystem') -> None:
        """Adds an ecosystem to the database.
        
        Args:
            ecosystem (Ecosystem) - The ecosystem to add to the database.
        """
        general_add('ecosystems', ecosystem.__dict__)
        
    @staticmethod
    def is_ecosystem_in_db(ecosystem: 'Ecosystem') -> bool:
        """Checks if an ecosystem is already in the database.
        
        Args:
            ecosystem (Ecosystem) - The ecosystem to check.
            
        Returns:
            bool: True if the ecosystem is in the database, False otherwise.
        """
        general_exists('ecosystems', ecosystem.__dict__)
    
    @staticmethod
    def fetch_all_ecosystems() -> list:
        """Fetches all ecosystems from the database.
        
        Returns:
            list: A list of all ecosystems.
        """
        return general_fetch_all('ecosystems')
        
    
    @staticmethod
    def fetch_ecosystem_by_name(name: str) -> 'Ecosystem':
        """Fetches an ecosystem from the database by name.
        
        Args:
            name (str) - The name of the ecosystem to fetch.
            
        Returns:
            Ecosystem: The ecosystem with the specified name.
        """
        conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
        
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM ecosystems WHERE eco_name = '{name}';""")
        
        ecosystem = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return Ecosystem(ecosystem[0])