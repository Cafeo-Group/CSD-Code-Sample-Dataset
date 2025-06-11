# -*- coding: utf-8 -*-
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FileManager:
    def __init__(self, folderPath=None):
        """
        Initialize the FileManager instance.
        Currently, no instance-specific attributes are required.
        """
        if folderPath:
            self.folderPath = folderPath
        pass

    def removeNewlines(self, content):
        """
        Remove all newline characters from the given content.
        
        :param content: The string content to process.
        :return: The content without newline characters.
        """
        return content.replace("\n", "").replace("\r", "")

    def saveToFile(self, content, file_path):
        """
        Save a string content or a list of strings to a .txt file.
        
        :param content: The string content or list of strings to save.
        :param file_path: The path of the file where the content will be saved.
        """
        if isinstance(content, list):
            content = "\n".join(content)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def appendToFile(self, content, file_path):
        """
        Append new content to an existing file.
        
        :param content: The string content or list of strings to append.
        :param file_path: The path of the file where the content will be appended.
        """
        if isinstance(content, list):
            content = "\n".join(content)
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(content + "\n")

    def createFile(self, folder_path, file_name):
        """
        Create an empty file with the given file name in the specified folder path.
        If a file with the same name already exists, create a copy with a unique name (e.g., file_name(1)).
        
        :param folder_path: The path of the folder where the file will be created.
        :param file_name: The name of the file to create.
        :return: The name of the created file (with a unique name if necessary).
        """
        os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists
        base_name, ext = os.path.splitext(file_name)
        file_path = os.path.join(folder_path, file_name)
        counter = 1

        # Check if the file already exists and create a unique name if necessary
        while os.path.exists(file_path):
            file_name = f"{base_name}({counter}){ext}"
            file_path = os.path.join(folder_path, file_name)
            counter += 1

        # Create the file
        with open(file_path, 'w', encoding='utf-8') as file:
            pass

        return file_name
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def searchFiles(self, folder_path, file_name):
        """
        Search for a file with the specified name in the given folder path.
        
        :param folder_path: The path of the folder to search in.
        :param file_name: The name of the file to search for.
        :return: The full path of the file if found, otherwise None.
        """
        file_path = os.path.join(folder_path, file_name)
        logging.debug(f"Searching for file: {file_path}")
        if os.path.exists(file_path):
            logging.debug(f"File found: {file_path}")
            return file_path
        logging.debug(f"File not found: {file_path}")
        return None