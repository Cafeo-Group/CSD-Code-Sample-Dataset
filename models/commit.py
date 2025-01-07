from datetime import datetime
from dataclasses import dataclass
from utils.postgres import general_add, general_exists, general_fetch_all
from io import StringIO
import pytz
import subprocess
from os import path
from typing import List
from git import Repo, Commit as GitCommit

@dataclass
class Commit:
    sha: str
    repo_name: str
    org_name: str
    timestamp: datetime
    message: str
    url: str
    files: list[str]
    
    def __str__(self) -> str:
        return f"-{self.sha} - {self.repo_name} - {self.org_name} - {self.timestamp} - {self.message} - {self.url} - {self.files}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @staticmethod
    def add_commit(commit: 'Commit') -> None:
        """Adds a commit to the database.
        
        Args:
            commit (Commit) - The commit to add.
            
        Returns:
            None
        """
        general_add('commits', commit.__dict__)
        
        
    @staticmethod
    def exists(commit: 'Commit') -> bool:
        """Checks if a commit is already in the database.
        
        Args:
            commit (Commit) - The commit to check.
            
        Returns:
            bool: True if the commit is in the database, False otherwise.
        """
        general_exists('commits', commit)
    
    @staticmethod
    def add_formatted_commit(commit_text: str, repo_path: str) -> None:
        """Parses the diff of a commit and adds the whole commit to the database.

        Args:
            commit_text (str) - The text of the commit to parse.\n
            repo_path (str) - The path to the repository the commit is from.\n
            
        Returns:
            None
        """
        sha, timestamp, message, diff_lines = None, None, None, []

        for line in StringIO(commit_text):
            if "<<DELIM>>" in line:
                if sha:
                    ecossystem = repo_path.split('\\')[1]
                    url = f"https://github.com/{ecossystem}/{repo_path.split('\\')[2]}/commit/{sha}"
                    commit = Commit(repo_path, datetime.fromtimestamp(int(timestamp), tz=pytz.utc),
                                    sha, message, "\n".join(diff_lines), ecossystem, url)
                    Commit.add_commit(commit)
                sha, timestamp, message = line.split("<<DELIM>>")
                diff_lines = []
            else:
                diff_lines.append(line.strip())

        if sha:
            ecossystem = repo_path.split('\\')[1]
            url = f"https://github.com/{ecossystem}/{repo_path.split('\\')[2]}/commit/{sha}"
            commit = Commit(repo_path, datetime.fromtimestamp(int(timestamp), tz=pytz.utc),
                            sha, message, "\n".join(diff_lines), ecossystem, url)
            Commit.add_commit(commit)

    @staticmethod
    def fetch_all_commits(repo_path: str, cutoff_date: datetime) -> None:
        """Fetches the commits from a repository that were made before a certain 
        date and adds them to the database.

        Args:
            repo_path (str) - The path to the repository to fetch commits from.\n
            cutoff_date (datetime) - The date to fetch commits until.\n
            
        Returns:
            None
        """
        if not path.exists(path.join(repo_path, '.git')):
            print(f"Skipping non-Git directory: {repo_path}")
            return

        try:
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path)
        except subprocess.CalledProcessError:
            print(f"Skipping invalid Git repository: {repo_path}")
            return

        try:
            process = subprocess.Popen(
                ["git", "log", "--pretty=format:%H<<DELIM>>%ct<<DELIM>>%s", "--patch", f"--until={cutoff_date.timestamp()}"],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Error fetching logs for {repo_path}: {stderr.decode('utf-8')}")
                return

            commit_info = stdout.decode('utf-8', errors='replace')
            Commit.add_formatted_commit(commit_info, repo_path)
            

        except Exception as e:
            print(f"Unexpected error processing {repo_path}: {e}")

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
                # remove the --cc flag to remove the files not necessarily changed by the merge commit itself
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
    def get_commit_data(repo_path: str, repo_url: str, cutoff_date: datetime) -> List['Commit']:
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
            url = f"{repo_url}/commit/{sha}"

            files = Commit.get_file_names_from_git(repo_path, sha)

            commits.append(
                Commit(
                    sha=sha,
                    repo_name=repo_name,
                    org_name=org_name,
                    timestamp=timestamp,
                    message=message,
                    url=url,
                    files=files,
                )
            )

        return commits
    
    @staticmethod
    def fetch_all_commits():
        """Fetches all commits from all repositories in the database.
        
        Returns:
            None
        """
        return general_fetch_all('commits')