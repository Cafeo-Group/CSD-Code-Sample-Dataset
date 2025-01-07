from dataclasses import dataclass
from datetime import datetime
from utils.postgres import general_add, general_exists, db_conn
import pandas as pd

@dataclass
class Repository:
    repo_name: str
    eco_name: str
    org_name: str
    html_url: str
    stars: int
    forks: int
    watchers: int
    contributors: int
    language: str
    size: float
    loc: float
    first_commit: datetime
    last_commit: datetime
    num_commits: int
    evolution_years: int
    evolution_months: int
    evolution_days: int
    age_years: int
    age_months: int
    age_days: int
    year_since_last_update: int
    month_since_last_update: int
    day_since_last_update: int
    open_issues: int
    closed_issues: int
    num_issues: int
    open_prs: int
    closed_prs: int
    num_prs: int
    merged_prs: int
    percentage_merged_prs: float
    percentage_open_prs: float
    archived: bool
    
    def __str__(self):
        return f'{self.repo_name} ({self.eco_name}) - {self.org_name} - {self.html_url}'
    
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
            html_url=tuple[3],
            stars=tuple[4],
            forks=tuple[5],
            watchers=tuple[6],
            contributors=tuple[7],
            language=tuple[8],
            size=tuple[9],
            loc=tuple[10],
            first_commit=tuple[11],
            last_commit=tuple[12],
            num_commits=tuple[13],
            evolution_years=tuple[14],
            evolution_months=tuple[15],
            evolution_days=tuple[16],
            age_years=tuple[17],
            age_months=tuple[18],
            age_days=tuple[19],
            year_since_last_update=tuple[20],
            month_since_last_update=tuple[21],
            day_since_last_update=tuple[22],
            open_issues=tuple[23],
            closed_issues=tuple[24],
            num_issues=tuple[25],
            open_prs=tuple[26],
            closed_prs=tuple[27],
            num_prs=tuple[28],
            merged_prs=tuple[29],
            percentage_merged_prs=tuple[30],
            percentage_open_prs=tuple[31],
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
                html_url=row['html_url'],
                stars=row['Stars'],
                forks=row['Forks'],
                watchers=row['Watchers'],
                contributors=row['Contributors'],
                language=row['Language'],
                size=row['Size (KB)'],
                loc=row['LOC'],
                first_commit=datetime.strptime(row['First Commit'], '%d/%m/%Y'),
                last_commit=datetime.strptime(row['Last Commit'], '%d/%m/%Y'),
                num_commits=row['# of Commits'],
                evolution_years=row['year-evolution'],
                evolution_months=row['month-evolution'],
                evolution_days=row['days-evolution'],
                age_years=row['year-age'],
                age_months=row['month-age'],
                age_days=row['days-age'],
                year_since_last_update=row['year-since-last-update'],
                month_since_last_update=row['month-since-last-update'],
                day_since_last_update=row['days-since-last-update'],
                open_issues=row['Open Issues'],
                closed_issues=row['Closed Issues'],
                num_issues=row['# of Issues'],
                open_prs=row['Open PRs'],
                closed_prs=row['Closed PRs'],
                num_prs=row['Total PRs'],
                merged_prs=row['Merged PRs'],
                percentage_merged_prs=float(row['% of Merged'].strip('%').replace(',', '.')),
                percentage_open_prs=float(row['% of Open PRs'].strip('%').replace(',', '.')),
                archived=row['archived']
            )
        except Exception as e:
            print(e)