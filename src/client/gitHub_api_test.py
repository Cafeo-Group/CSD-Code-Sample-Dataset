# -*- coding: utf-8 -*-
import sys
import os

# Add the parent directory of 'utils' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gitHubClient import GitHubClient, PullRequestState
from utils.fileManager import FileManager
import os

# Create an instance of GitHubClient
client = GitHubClient()

# Create an instance of FileManager
fileManager = FileManager()

# Set the repository owner and name
owner = "aws-samples"
repo = "amazon-kinesis-data-analytics-snapshot-manager-for-flink"

# owner = "VictorMendesFS"
# repo = "Object-Oriented-lab-implementation"

def test_getPulls():
    """
    Test the getPulls method of GitHubClient.
    """
    try:
        pulls = client.getPulls(owner, repo, state=PullRequestState.CLOSED)

        if pulls:
            print("Pull requests fetched successfully.")
            print("Total pull requests:", len(pulls))
            for pr in pulls:
                print(f"PR #{pr['number']}: {pr['title']}")
                print(f"Author: {pr['user']['login']}")
                print(f"URL: {pr['html_url']}")
                print(f"Description: {client.convertBodyToString(pr['body'])}")
                print("-" * 50)
        else:
            print("No pull requests found.")
    except Exception as e:
        print("An error occurred:", str(e))

def test_getCommitsFromPR():
    """
    Test the getCommitsFromPR method of GitHubClient.
    """
    try:
        pulls = client.getPulls(owner, repo, state=PullRequestState.OPEN)
        commits = client.getCommitsFromPR(owner, repo, pulls[0])

        if commits:
            print("Commits fetched successfully.")
            print("Total commits:", len(commits))
            for commit in commits:
                print(f"Commit SHA: {commit['sha']}")
                print(f"Author: {commit['commit']['author']['name']}")
                print(f"Message: {commit['commit']['message']}")
                print("-" * 50)
        else:
            print("No commits found.")
    except Exception as e:
        print("An error occurred:", str(e))

def test_getDiffsFromPRs():
    """
    Test the getDiffsFromPRs method of GitHubClient.
    """
    try:
        diffs = client.getDiffsFromPRs(owner, repo, state=PullRequestState.OPEN)

        if diffs:
            print("Diffs fetched successfully.")
            print("Total diffs:", len(diffs))
            for diff in diffs:
                print(f"Commit SHA: {diff['sha']}")
                print(f"Diff: {diff['diff']}")
                print("-" * 50)
        else:
            print("No diffs found.")
    except Exception as e:
        print("An error occurred:", str(e))

def test_getFilesChangedInPR():
    """
    Test the getFilesChangedInPR method of GitHubClient.
    """
    try:
        pulls = client.getPulls(owner, repo, state=PullRequestState.CLOSED)
        files = client.getFilesChangedInPR(owner, repo, pulls[2]['number'])
        folderPath = r'c:\Users\vicme\OneDrive\Livros Unicamp\TCC\Implementacao\AutomatedPullRequestGenerator\src\client'
        fileName = "diffFiles.txt"
        
        fileName = fileManager.createFile(folderPath, fileName)
        filePath = os.path.join(folderPath, fileName)
        
        fileManager.saveToFile("", filePath)

        if files:
            print("Files changed fetched successfully.")
            print("Total files changed:", len(files))
            for file in files:
                concatenated_files = "\n".join(
                    f"File: {file['filename']}, Status: {file['status']}, Content: {fileManager.removeNewlines(file.get('patch', 'No content available'))}"
                    for file in files
                )

                fileManager.appendToFile(concatenated_files, filePath)

                print(concatenated_files)
        else:
            print("No files changed found.")
    except Exception as e:
        print("An error occurred:", str(e))

# run tests
# test_getPulls()
test_getFilesChangedInPR()
# test_getCommitsFromPR()
# test_getDiffsFromPRs()