"""
GitHub Client Module

This module provides a client for interacting with the GitHub API. It includes functionality to:
- Fetch pull requests from a repository.
- Retrieve commits and diffs from pull requests.
- Fetch files changed in a pull request.
- Convert pull request body content into a formatted string.

Classes:
    - PullRequestState: Enum representing the state of pull requests (open or closed).
    - GitHubClient: A client for interacting with the GitHub API.

Dependencies:
    - os
    - requests
    - pathlib.Path
    - dotenv.load_dotenv
    - enum.Enum
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum

class PullRequestState(Enum):
    OPEN = "open"
    CLOSED = "closed"

class GitHubClient:
    def __init__(self):
        # Load environment variables
        env_path = r'c:\Users\vicme\OneDrive\Livros Unicamp\TCC\Implementacao\AutomatedPullRequestGenerator\src\client\env.txt'
        load_dotenv(env_path)
    
        self.token = self.__getGitHubToken()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"        
        }

    def __getGitHubToken(self) -> str:
        """
        Retrieve the GitHub token from environment variables.

        Returns:
            str: The GitHub token as a string.
        """
        token = os.getenv("GITHUB_TOKEN").strip('"')
        print
        return token

    def getPulls(self, owner: str, repo: str, state: PullRequestState = PullRequestState.CLOSED) -> list:
        """
        Fetch pull requests from the specified repository.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            state (PullRequestState, optional): The state of pull requests to fetch. Defaults to PullRequestState.CLOSED.

        Returns:
            list: A list of pull requests in the specified state.

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": state.value}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def getCommitsFromPR(self, owner: str, repo: str, pr: dict) -> list:
        """
        Fetch commits from a specific pull request in the specified repository.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            pr (dict): The pull request object containing details of the PR.

        Returns:
            list: A list of commits from the specified pull request.

        Raises:
            HTTPError: If the API request fails.
        """
        pr_number = pr['number']
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def getDiffFromCommit(self, owner: str, repo: str, commit: dict) -> dict:
        """
        Fetch the diff from a specific commit in the specified repository.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            commit (dict): The commit object containing details of the commit.

        Returns:
            dict: The diff from the specified commit.

        Raises:
            HTTPError: If the API request fails.
        """
        sha = commit['sha']
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def getDiffsFromPRs(self, owner: str, repo: str, state: PullRequestState = PullRequestState.OPEN) -> list:
        """
        Fetch all diffs from commits in pull requests in the specified repository.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            state (PullRequestState, optional): The state of pull requests to fetch. Defaults to PullRequestState.OPEN.

        Returns:
            list: A list of diffs from all commits in pull requests in the specified state.

        Raises:
            HTTPError: If the API request fails.
        """
        pulls = self.getPulls(owner, repo, state)
        all_diffs = []
        for pr in pulls:
            commits = self.getCommitsFromPR(owner, repo, pr)
            for commit in commits:
                diff = self.getDiffFromCommit(owner, repo, commit)
                all_diffs.append(diff)
        return all_diffs

    def getFilesChangedInPR(self, owner: str, repo: str, pr_number: int) -> list:
        """
        Fetch the files changed in a specific pull request.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            pr_number (int): The pull request number.

        Returns:
            list: A list of files changed in the specified pull request. 
            Each file includes details such as filename, status, additions, deletions, and changes.

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    @staticmethod
    def convertBodyToString(body: str) -> str:
        """
        Convert the body of a pull request to a formatted string.

        Args:
            body (str): The body content of the pull request.

        Returns:
            str: A formatted string representation of the body. If the body contains HTML tags like <details>, 
            it extracts and formats the summary and details.

        Notes:
            - If the body is empty, a default message "No description provided." is returned.
            - HTML tags are removed, and the content is cleaned for readability.
        """
        if not body:
            return "No description provided."

        # Extract the main content and format it
        formatted_body = body.strip()
        if "<details>" in formatted_body:
            # Extract the summary and key details
            import re
            summary_match = re.search(r"<summary>(.*?)</summary>", formatted_body, re.DOTALL)
            details_match = re.search(r"<details>(.*?)</details>", formatted_body, re.DOTALL)

            summary = summary_match.group(1).strip() if summary_match else "No summary available."
            details = details_match.group(1).strip() if details_match else "No details available."

            # Clean up HTML tags and truncate if necessary
            formatted_body = f"Summary: {summary}\nDetails:\n{re.sub(r'<.*?>', '', details)}"
        
        return formatted_body
