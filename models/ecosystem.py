from dataclasses import dataclass
from utils.postgres import db_conn, general_add

@dataclass
class Ecosystem:
    eco_name: str
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
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
        conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
        cursor = conn.cursor()
        
        cursor.execute(f"""SELECT 1 FROM ecosystems WHERE eco_name = '{ecosystem.eco_name}';""")
        exists = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return exists
    
    @staticmethod
    def fetch_all_ecosystems() -> list:
        """Fetches all ecosystems from the database.
        
        Returns:
            list: A list of all ecosystems.
        """
        conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
        cursor = conn.cursor()
        
        cursor.execute(f"""SELECT * FROM ecosystems;""")
        ecosystems = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return ecosystems
    
    @staticmethod
    def fetch_ecosystem_by_name(name: str) -> 'Ecosystem':
        conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
        
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM ecosystems WHERE eco_name = '{name}';""")
        
        ecosystem = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return Ecosystem(ecosystem[0])