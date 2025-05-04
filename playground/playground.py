from os import path
from sys import path as sys_path

parent_dir = path.abspath(path.join('.'))
sys_path.append(parent_dir)
print(f"Added {parent_dir.split("\\")[-1]} to sys.path")
    
from models.repository import Repository
from models.commit import Commit
from models.file import File
from models.cf import CommitFile, MetadataHelper
from models.hunk import Hunk

import pandas as pd
from datetime import datetime
import pytz

repos = pd.read_csv('./code_samples.csv', skiprows=1)
repos = repos.dropna(subset=['html_url'])

repo = None

for index, row in repos.iterrows():
    if row['name'] == 'amazon-bedrock-rag':
        repo = Repository.csv_row_to_Repository(row)


commits = Commit.get_commit_data(repo.get_repo_path(), datetime.now(pytz.timezone("UTC")))
print(f"Fetched {len(commits)} commits from {repo.get_repo_path()}")

com = commits[1]

file_names = Commit.get_file_names_from_commit(repo.get_repo_path(), com.sha)
print(f"Fetched {len(file_names)} file names from {repo.get_repo_path()}")

file_content, name = File.get_file_content(repo.get_repo_path(), com.sha, file_names[0])
metadata_list = CommitFile.get_metadata(com.org_name, com.repo_name, com.sha, name, True)

print(f"Fetched {len(metadata_list)} metadata from {repo.get_repo_path()}")

cfs = []
hunks = []
for mt in metadata_list:
    cf = CommitFile(com.repo_name, com.org_name, name, com.sha, file_content, mt.change_type, mt.file_mode, mt.index_info)
    cfs.append(cf)
    hunk = Hunk(None, name, com.repo_name, com.org_name, com.sha, mt.old_start, mt.old_length, mt.new_start, mt.new_length, mt.lines, mt.old_name, mt.new_name)
    hunks.append(hunk)
    
print(f"Fetched {len(cfs)} commit files and {len(hunks)} hunks from {repo.get_repo_path()}")
print(f"Commit file: {cfs[0]}")

print(f"Hunk: {hunks[0]}")