# -*- coding: utf-8 -*-
import json

class CodeSamplesFetcher:
    def __init__(self):
        self.code_samples_path = r'c:\Users\vicme\OneDrive\Livros Unicamp\TCC\Implementacao\AutomatedPullRequestGenerator\src\codeSamples\code_samples.csv'

    def openCodeSamples(self):
        """
        Open the code samples from the specified path.
        """
        try:
            with open(self.code_samples_path, 'r') as file:
                code_samples = file.readlines()
            return code_samples
        except FileNotFoundError:
            print(f"File not found: {self.code_samples_path}")
            return []

    def parseCodeSamplesToJSON(self):
        """
        Parse the code samples into a JSON-compatible structure.

        Returns:
            list: A list of dictionaries representing the code samples.
        """
        code_samples = self.openCodeSamples()
        if not code_samples:
            return []

        # Define the keys for the JSON structure
        keys = [
            "name", "Ecosystem", "html_url", "Stars", "Forks", "Watchers", "Contributors",
            "Language", "Size (KB)", "LOC", "First Commit", "Last Commit", "# of Commits",
            "year-evolution", "month-evolution", "days-evolution", "year-age", "month-age",
            "days-age", "year-since-last-update", "month-since-last-update", "days-since-last-update",
            "Open Issues", "Closed Issues", "# of Issues", "Open PRs", "Closed PRs", "Total PRs",
            "Merged PRs", "% of Open PRs", "% of Merged", "archived"
        ]

        # Parse each line into a dictionary
        parsed_samples = []
        for line in code_samples[2:]:  # Skip the headers
            values = line.strip().split(",")  # Split by commas
            sample_dict = dict(zip(keys, values))
            parsed_samples.append(sample_dict)

        return parsed_samples
    
    def fetchCodeSamplesHtmls(self):
        """
        Fetch the HTML URLs of the code samples.
        """
        code_samples = self.parseCodeSamplesToJSON()
        html_urls = [sample['html_url'] for sample in code_samples if 'html_url' in sample]
        return html_urls
    
    def extractOwnerAndRepoFromUrl(self, html_url):
        """
        Extract the owner and repository name from a GitHub URL.

        Args:
            html_url (str): The GitHub repository URL.

        Returns:
            dict: A dictionary with 'owner' and 'repo' as keys.
        """
        try:
            # Split the URL by '/' and extract the owner and repo
            import logging
            logging.debug(f"Extracting owner and repo from URL: {html_url}")
            parts = html_url.strip("/").split("/")
            owner = parts[-2]
            repo = parts[-1]
            return {"owner": owner, "repo": repo}
        except IndexError:
            raise ValueError(f"Invalid GitHub URL: {html_url}")

    def fetchOwnsersAndReposFromUrls(self, url_list):
        """
        Fetch all owners and repositories from a list of GitHub URLs.

        Args:
            url_list (list): A list of GitHub repository URLs.

        Returns:
            list: A list of dictionaries with 'owner' and 'repo' for each URL.
        """
        return [self.extractOwnerAndRepoFromUrl(url) for url in url_list]