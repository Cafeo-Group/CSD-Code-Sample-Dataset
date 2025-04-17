from utils.postgres import general_add, general_exists, general_fetch_all, \
    general_add_in_batches, general_exists_in_batches
from dataclasses import dataclass
from typing import List
import re
import subprocess

@dataclass
class File:
    file_name: str
    repo_name: str
    org_name: str
    type: str
    
    def __str__(self) -> str:
        return f"-{self.file_name}.{self.type} - {self.repo_name} - {self.org_name}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @staticmethod
    def add_file(file: 'File') -> None:
        """Adds a file to the database.
        
        Args:
            file (File) - The file to add.
            
        Returns:
            None
        """
        general_add('files', file.__dict__)
        
    @staticmethod
    def add_files_in_batches(files: List['File']):
        """Adds a list of files to the database in batches.
        
        Args:
            files (list) - The list of files to add.
        """
        general_add_in_batches('files', [file.__dict__ for file in files])
        
    @staticmethod
    def exists(file: 'File') -> bool:
        """Checks if a file is already in the database.
        
        Args:
            file (File) - The file to check.
            
        Returns:
            bool: True if the file is in the database, False otherwise.
        """
        return general_exists('files', file.__dict__)
    
    @staticmethod
    def exists_by_args(file_name: str, sha: str, repo_name: str, org_name: str) -> bool:
        """Checks if a file is already in the database by its arguments.
        
        Args:
            file_name (str) - The name of the file.\n
            sha (str) - The commit SHA.\n
            repo_name (str) - The name of the repository.\n
            org_name (str) - The name of the organization.
            
        Returns:
            bool: True if the file is in the database, False otherwise.
        """
        return general_exists('files', {'file_name': file_name, 'sha': sha, 'repo_name': repo_name, 'org_name': org_name})
    
    @staticmethod
    def exists_in_batches(files: List[set]) -> List[bool]:
        """Checks if a list of files are already in the database in batches.
        
        Args:
            files (list) - The list of files to check.
            
        Returns:
            list: A list of booleans indicating if each file is in the database.
        """
        return general_exists_in_batches('files', [{'file_name': file_set[0], 'sha': file_set[1], 'repo_name': file_set[2], 'org_name': file_set[3]} for file_set in files])
    
    @staticmethod
    def fetch_all() -> List['File']:
        """Fetches all files from the database.
        
        Returns:
            list: A list of all files in the database.
        """
        return [File(*file) for file in general_fetch_all('files')]
    
    @staticmethod
    def get_file_status(repo_path: str, commit_sha: str, file_path: str) -> str:
        """Determines the status of a file in a specific commit (added, modified, deleted, or renamed).

        Args:
            repo_path (str): Path to the git repository.
            commit_sha (str): SHA of the commit.
            file_path (str): Path of the file relative to the repo.

        Returns:
            str: 'deleted', 'modified', 'added', 'renamed', or 'not_changed'.

        Raises:
            Exception: If there is an error running the git command.
        """
        try:
            result = subprocess.check_output(
                ['git', 'diff', '--name-status', f'{commit_sha}^', commit_sha],
                cwd=repo_path,
                text=True
            )
            if re.search(rf'^D\t{re.escape(file_path)}$', result, re.MULTILINE):
                return 'deleted'
            if re.search(rf'^M\t{re.escape(file_path)}$', result, re.MULTILINE):
                return 'modified'
            if re.search(rf'^A\t{re.escape(file_path)}$', result, re.MULTILINE):
                return 'added'
            if re.search(rf'^R\d+\t.*?\t{re.escape(file_path)}$', result, re.MULTILINE) or \
            re.search(rf'^R\d+\t{re.escape(file_path)}\t.*?$', result, re.MULTILINE):
                return 'renamed'

            return 'not_changed'

        except subprocess.CalledProcessError as e:
            raise Exception(f"Error determining file status: {e.stderr.strip()}")

    @staticmethod
    def get_file_content(repo_path: str, commit_sha: str, file_path: str) -> str:
        """
        Returns the content of the file as a string, handling deleted files and submodules.

        Args:
            repo_path (str): Path to the git repository.
            commit_sha (str): SHA of the commit.
            file_path (str): Path of the file relative to the repo.

        Returns:
            str: The content of the file (decoded text), '<binary content>' if it's binary,
                'File was deleted in this commit', 'File was renamed in this commit', or 
                'This is a submodule' if the 'file' references a submodule.
        """
        if File.is_submodule(repo_path, commit_sha, file_path):
            return 'This is a submodule', file_path

        file_status = File.get_file_status(repo_path, commit_sha, file_path)
    
        if file_status == 'deleted':
            return 'File was deleted in this commit', file_path
        if file_status == 'renamed':
            return 'File was renamed in this commit', file_path
        else:
            try:
                file_content = subprocess.check_output(
                    ['git', 'show', f'{commit_sha}:{file_path}'],
                    cwd=repo_path,
                    stderr=subprocess.PIPE
                )

                if File.is_binary(file_content):
                    return '<binary content>', file_path
                
                file_content = file_content.decode('utf-8', errors='replace')
                
                if not file_content.strip():
                    return "File is empty", file_path
                
                return file_content, file_path
            
            except subprocess.CalledProcessError as e:
                if "does not exist" in e.stderr.decode():
                    return "Couldn't retrieve content", file_path
                print(f"Error occurred while retrieving file: {e.stderr.strip()}")

    @staticmethod
    def is_binary(content: bytes) -> bool:
        """
        Determines if the content is binary by checking for non-printable characters.
        Args:
            content (bytes): The content of the file in byte form.
        
        Returns:
            bool: True if the file is binary, False if it's a text file.
        """
        for byte in content:
            if byte == 0:  # Null byte
                return True
            # Check for non-printable ASCII characters (excluding carriage return (13), newlines (10), tabs (9))
            if (byte < 32 or byte > 126) and byte not in [9, 10, 13]:
                        return True
        
        return False


    @staticmethod
    def is_submodule(repo_path: str, commit_sha: str, file_path: str) -> bool:
        """Checks if a file is a Git submodule in a specific commit.
        
        Args:
            repo_path (str): Path to the Git repository.
            commit_sha (str): The commit SHA to check in.
            file_path (str): Path of the file to check.

        Returns:
            bool: True if the file is a submodule, False otherwise.
        """
        try:
            result = subprocess.check_output(
                ['git', 'ls-tree', commit_sha, file_path],
                cwd=repo_path,
                stderr=subprocess.PIPE
            ).decode().strip()

            if result.startswith('160000'):
                return True  # 160000 is the object type for submodules

            return False

        except subprocess.CalledProcessError:
            return False