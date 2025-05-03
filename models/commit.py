from datetime import datetime
from dataclasses import dataclass
from utils.postgres import general_add, general_exists, general_fetch_all, general_fetch_by_args, general_add_in_batches, general_exists_in_batches
import pytz
import subprocess
from typing import List
from git import Repo

@dataclass
class Commit:
    sha: str
    repo_name: str
    org_name: str
    timestamp: datetime
    message: str
    
    def __str__(self) -> str:
        return f"-{self.sha} - {self.repo_name} - {self.org_name} - {self.timestamp} - {self.message}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __hash__(self):
        return hash((self.sha, self.repo_name, self.org_name))
    
    def __eq__(self, other):
        if not isinstance(other, Commit):
            return False
        return (self.sha, self.repo_name, self.org_name) == (other.sha, other.repo_name, other.org_name)
    
    @staticmethod
    def add_commit(commit: 'Commit') -> 'Commit':
        """Adds a commit to the database.
        
        Args:
            commit (Commit) - The commit to add.
            
        Returns:
            None
        """
        general_add('commits', commit.__dict__)
        return commit
        
        
    @staticmethod
    def exists(commit: 'Commit') -> bool:
        """Checks if a commit is already in the database.
        
        Args:
            commit (Commit) - The commit to check.
            
        Returns:
            bool: True if the commit is in the database, False otherwise.
        """
        return general_exists('commits', commit.__dict__)

    @staticmethod
    def add_all_commits_from_repo(repo_path: str, cutoff_date: datetime):
        fetch_all = Commit.fetch_all_commits(repo_path, cutoff_date)
        if fetch_all:
            Commit.add_formatted_commit(fetch_all, repo_path)
            
    @staticmethod
    def get_file_names_from_git(repo_path: str, sha: str) -> List[str]:
        """Gets the names of all the files in a commit.
        
        Args:
            repo_path (str) - The path to the repository the commit is in.\n
            sha (str) - The sha of the commit to get the files from.\n
            
        Returns:
            List[str]: A list of the names of all the files in the commit.
        """
        try:
            process = subprocess.Popen(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--cc", sha],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Error fetching logs for {repo_path}: {stderr.decode('utf-8')}")
                return

            files = stdout.decode('utf-8', errors='replace').splitlines()
            return files
        except Exception as e:
            print(f"Unexpected error processing {repo_path}: {e}")
       
    @staticmethod     
    def get_commit_data(repo_path: str, cutoff_date: datetime) -> List['Commit']:
        """Extracts commit data from the repository and stores it in a list of Commit objects.

        Args:
            repo_path (str) - The path to the repository to extract commit data from.\n
            repo_url (str) - The URL of the repository.\n
            cutoff_date (datetime) - The date to fetch commits until.\n
            
        Returns:
            List[Commit]: A list of Commit objects containing the commit data.
        """
        repo = Repo(repo_path)
        if repo.bare:
            raise ValueError("The repository is bare or invalid.")

        repo_name = repo_path.split("\\")[-1]
        org_name = repo_path.split("\\")[-2]
        commits = []

        for commit in repo.iter_commits():
            commit_date = datetime.fromtimestamp(commit.committed_date, tz=pytz.UTC)
            if commit_date > cutoff_date:
                continue
            sha = commit.hexsha
            timestamp = datetime.fromtimestamp(commit.committed_date)
            message = commit.message.strip()
            
            candidate = Commit(
                    sha=sha,
                    repo_name=repo_name,
                    org_name=org_name,
                    timestamp=timestamp,
                    message=message,
                )
            
            if not Commit.exists(candidate):
                commits.append(candidate )

        return commits
    
    @staticmethod
    def fetch_all_commits():
        """Fetches all commits from all repositories in the database.
        
        Returns:
            list[Commit]: A list of all commits in the database.
        """
        return [Commit(*commit) for commit in general_fetch_all('commits')]
    
    @staticmethod
    def fetch_by_commit_sha_and_repo_name(commit_sha: str, repo_name: str) -> 'Commit':
        """Fetches a commit from the database by its sha and repository name.
        
        Args:
            commit_sha (str) - The sha of the commit to fetch.\n
            repo_name (str) - The name of the repository the commit is in.\n
            
        Returns:
            Commit: The commit fetched from the database.
        """
        return Commit(*general_fetch_by_args('commits', {'sha': commit_sha, 'repo_name': repo_name}))

    @staticmethod
    def add_commit_in_batches(commits: List['Commit']) -> None:
        """Adds a list of commits to the database in batches.
        
        Args:
            commits (List[Commit]) - The list of commits to add.
            
        Returns:
            None
        """
        general_add_in_batches('commits', [commit.__dict__ for commit in commits])
        
    @staticmethod
    def exist_commits_in_batches(commits: List['Commit']) -> List[bool]:
        """Checks if a list of commits exist in the database in batches.
        
        Args:
            commits (List[Commit]) - The list of commits to check.
            
        Returns:
            List[bool]: A list of booleans indicating if each commit exists in the database.
        """
        return general_exists_in_batches('commits', [commit.__dict__ for commit in commits])