# -*- coding: utf-8 -*-
"""
This module provides a client for interacting with an OpenAI-like API. 
It includes functions to load environment variables, retrieve API details, 
and interact with the API for tasks such as chatting with a model and fetching available models.

Classes:
    - OpenUiClient: A client for interacting with the API.

Functions:
    - chatWithModel(content: Optional[str], model: str, filePath: Optional[str]) -> Optional[requests.Response]: 
      Sends a chat message to the specified model and retrieves the response.
    - getAvailableApiModels() -> Optional[requests.Response]: 
      Fetches the list of available models from the API.

Usage:
    Ensure the environment variables `API_URL` and `API_KEY` are set in the specified env file.
    Use the provided functions to interact with the API.
"""

import os
import requests
from dotenv import load_dotenv
from typing import Optional

class OpenUiClient:
    # Load environment variables from env file
    env_path = r'c:\Users\vicme\OneDrive\Livros Unicamp\TCC\Implementacao\AutomatedPullRequestGenerator\src\client\env.txt'
    load_dotenv(env_path)

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Constructor for the OpenUiClient class.

        Args:
            api_url (Optional[str]): The base URL of the API. Defaults to the value from the environment variable.
            api_key (Optional[str]): The API key for authentication. Defaults to the value from the environment variable.
        """
        self.api_url = api_url or self.__getApiUrl()
        self.api_key = api_key or self.__getApiKey()

    def __getApiUrl(self) -> str:
        """
        Retrieves the base URL of the API from environment variables (private method).

        Returns:
            str: The API base URL.
        """
        api_url = os.getenv("API_URL").strip('"')
        return api_url

    def __getApiKey(self) -> str:
        """
        Retrieves the API key from environment variables (private method).

        Returns:
            str: The API key.
        """
        return os.getenv("API_KEY").strip('"')

    def chatWithModel(self, content: Optional[str] = None, model: str = 'llama3.1:8b', filePath: Optional[str] = None) -> Optional[requests.Response]:
        """
        Sends a chat message to the specified model and retrieves the response.

        Args:
            content (Optional[str]): The message content to send to the model. If None, a default prompt is used.
            model (str): The model to interact with (default is 'llama3.1:8b').
            filePath (Optional[str]): Path to a file containing the message content. If provided, the file content is used.

        Returns:
            Optional[requests.Response]: The API response object if successful, None otherwise.
        """
        if filePath:
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    fileContent = file.read()
            except Exception as e:
                print(f"Error reading the file. Details: {e}")
                return None
            
        if content is None:
            content = (
                "You are an AI code assistant. Read and understand the following code diff carefully. Do not generate anything yet.\n"
                "Wait for further instructions after reading.\n\n"
                "Code diff:"
            )

        finalContent = (
            "Now, based only on the code diff provided earlier, generate a single Pull Request title and a single body with the description.\n"
            "Strictly follow the template below and provide only the completed result, with no extra text:\n\n"
            "Title: <concise, imperative summary of the change>\n"
            "Body: <clear, bullet-point or paragraph summary explaining the key changes, motivations, and impact>"
        )
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': f"{content} \n{fileContent} \n{finalContent}" if filePath else content
                }
            ]
        }
        try:
            response = requests.post(f'{self.api_url}/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error performing the chat. Details: {e}")
            return None

    def getAvailableApiModels(self) -> Optional[list]:
        """
        Fetches the list of available model IDs from the API.

        Returns:
            Optional[list]: A list of model IDs if successful, None otherwise.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        models_endpoint = '/models'

        try:
            response = requests.get(f'{self.api_url}{models_endpoint}', headers=headers)
            response.raise_for_status()
            data = response.json()
            # Extract the list of model IDs
            model_ids = [model['id'] for model in data.get('data', []) if 'id' in model]
            return model_ids
        except requests.exceptions.RequestException as e:
            print(f"Error fetching available models. Details: {e}")
            return None
        except (KeyError, TypeError) as e:
            print(f"Error processing the available models response. Details: {e}")
            return None
