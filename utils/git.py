from os import path, makedirs
from git import Repo
import subprocess

def clone(git_url: str, repo_dir: str, sample: str) -> None:
    '''Clone a git repository and checkout all files in the repository
    
    Args:
        git_url (str) - URL of the git repository\n
        repo_dir (str) - Directory to clone the repository to\n
        sample (str) - Name of the sample\n
        
    Returns:
        None
    '''
    repo_path = path.join(repo_dir, sample)
    makedirs(repo_path, exist_ok=True)

    Repo.clone_from(git_url, repo_path, multi_options=["--no-checkout"], bare=True)
        
def download(sample: str) -> None:
    '''Download the repository. If the repository is already downloaded,
    nothing is done.
    
    Args:
        sample (str) - Name of the sample
    
    Returns:
        None
    '''
    gitHubUrl = f"https://github.com/{sample}.git"
    repoDir = "../download/orgs/"
    isdir = path.isdir(repoDir+sample)
    if isdir:
        print(f"Repository {sample} already downloaded")
        return
    else:
        clone(gitHubUrl, repoDir, sample)

def is_merge_commit(repo_path: str, sha: str) -> bool:
    """Check if a commit is a merge commit.
    
    Args:
        repo_path (str): The path to the repository.
        sha (str): The commit SHA to check.
        
    Returns:
        bool: True if the commit is a merge commit, False otherwise.
    """
    try:
        process = subprocess.Popen(
            ["git", "rev-list", "--parents", "-n", "1", sha],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace'
        )
        stdout, stderr = process.communicate()
        
        if stderr:
            raise Exception(f"Error checking commit: {stderr.strip()}")
        
        if process.returncode != 0:
            return False
            
        parents = stdout.strip().split()
        return len(parents) > 2  # Commit SHA + at least 2 parents
    except Exception:
        return False
