from os import path, makedirs
from git import Repo

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