from dataclasses import dataclass
from utils.postgres import general_add, general_exists,\
    general_exists_in_batches, general_add_in_batches
from typing import List, Optional
import re
import subprocess
import os

@dataclass
class MetadataHelper:
    file_name: str    
    repo_name: str
    org_name: str
    sha: str
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    lines: list[str]
    old_name: Optional[str] = None
    new_name: Optional[str] = None
    change_type: Optional[str] = None
    file_mode: Optional[str] = None
    index_info: Optional[str] = None

@dataclass
class CommitFile:
    repo_name: str
    org_name: str
    file_name: str
    sha: str
    content: List[str]
    change_type: Optional[str] = None
    file_mode: Optional[str] = None
    index_info: Optional[str] = None
    
    def __str__(self):
        return f"{self.repo_name} - {self.org_name} - {self.file_name} - {self.sha}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def add_commit_file(commit_file: 'CommitFile') -> None:
        """Adds a commit file to the database.
        
        Args:
            commit_file (CommitFile) - The commit file to add.
            
        Returns:
            None
        """
        general_add('commit_files', commit_file.__dict__)
        
    @staticmethod
    def exists(commit_file: 'CommitFile') -> bool:
        """Checks if a commit file is already in the database.
        
        Args:
            commit_file (CommitFile) - The commit file to check.
            
        Returns:
            bool: True if the commit file is in the database, False otherwise.
        """
        return general_exists('commit_files', commit_file)
    
    @staticmethod
    def exists_in_batches(cfs: List[set]) -> List[bool]:
        """Checks if a list of cfs are already in the database in batches.
        
        Args:
            cfs (list) - The list of cfs to check.
            
        Returns:
            list: A list of booleans indicating if each cf is in the database.
        """
        return general_exists_in_batches('commit_files', [{'file_name': cf_set[0], 'sha': cf_set[1], 'repo_name': cf_set[2], 'org_name': cf_set[3]} for cf_set in cfs])
    
    @staticmethod
    def add_cfs_in_batches(cfs: List['CommitFile']):
        """Adds a list of cfs to the database in batches.
        
        Args:
            cfs (list) - The list of cfs to add.
        """
        general_add_in_batches('commit_files', [cf.__dict__ for cf in cfs])
        
    @staticmethod
    def get_metadata(org_name: str, repo_name: str, sha: str, file_name: str) -> List['MetadataHelper']:
        """Fetches all Hunks from a specific commit and file using `git show`.

        Args:
            org_name (str): The organization name.
            repo_name (str): The repository name.
            sha (str): The commit SHA to fetch the diffs from.
            file_name (str): The file name to check for in the commit.

        Returns:
            list[Hunk]: A list of all Hunks parsed from the git diff output.
        """
        try:
            process = subprocess.Popen(
                ['git', 'show', sha, '--', file_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.join('..', 'download', 'orgs', org_name, repo_name),
                encoding='utf-8',
                errors='replace'
            )
            
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"Error executing git show: {stderr.strip()}")
            
            all_metadata = []
            current_metadata = None
            hunk_pattern = re.compile(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@')
            file_name_pattern = re.compile(r'---\s+(a\/[\w.\-\/]+|\/dev\/null)[\r\n]+\+\+\+\s+(b\/[\w.\-\/]+|\/dev\/null)')
            change_type_pattern = re.compile(r'(new file mode|deleted file mode|rename|copy)')
            file_mode_pattern = re.compile(r'(100\d{3})')
            index_info_pattern = re.compile(r'^(index ([0-9a-f]+)\.\.([0-9a-f]+))$')
            
            old_name = None
            new_name = None
            change_type = None
            file_mode = None
            index_info = None
            
            if stdout:
                lines = stdout.split('\n')
                for index in range(len(lines)):
                    if index != (len(lines) - 1):
                        candidate_names = lines[index] + '\n'+lines[index+1]
                        file_match = file_name_pattern.match(candidate_names)
                        if file_match:
                            old_name, new_name = file_match.groups()
                    
                    change_match = change_type_pattern.match(lines[index])
                    if change_match:
                        change_type = change_match.group(1)
                    elif 'index' in lines[index] and change_type is None:
                        change_type = 'modified'
                        modified_pattern = re.compile(r'index ([0-9a-f]+)\.\.([0-9a-f]+) ([0-9]+)')
                        modified_match = modified_pattern.match(lines[index])
                        if modified_match:
                            old_sha, new_sha, mode_of_file = modified_match.groups()
                            index_info = f'index {old_sha}..{new_sha}'
                            file_mode = mode_of_file
                    
                    file_mode_match = file_mode_pattern.search(lines[index])
                    if file_mode_match:
                        file_mode = file_mode_match.group(1)
                        
                    index_info_match = index_info_pattern.match(lines[index])
                    if index_info_match:
                        index_info = index_info_match.group(1)
                    
                    match = hunk_pattern.match(lines[index])
                    if match:
                        if current_metadata:
                            all_metadata.append(current_metadata)
                        
                        old_start, old_length, new_start, new_length = map(int, match.groups())
                        current_metadata = MetadataHelper(
                            file_name=file_name,
                            sha=sha,
                            repo_name=repo_name,
                            org_name=org_name,
                            old_start=old_start,
                            old_length=old_length,
                            new_start=new_start,
                            new_length=new_length,
                            lines=[],
                            old_name=old_name,
                            new_name=new_name,
                            change_type=change_type,
                            file_mode=file_mode,
                            index_info=index_info
                        )
                    elif current_metadata is not None:
                        current_metadata.lines.append(lines[index])
                
                if current_metadata:
                    current_metadata.append(current_metadata)
                
                return all_metadata
            else:
                print(org_name, repo_name, sha, file_name)
                return None
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve diffs: {str(e)}")