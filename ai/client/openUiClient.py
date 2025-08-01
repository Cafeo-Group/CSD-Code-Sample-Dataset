import os
import requests
from dotenv import load_dotenv
from typing import Optional, List
import fitz

def read_pdf_text(pdf_path: str) -> str:
    """
    Extracts and returns the full text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: Extracted text content.
    """
    try:
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

class OpenUiClient:
    # Load environment variables from env file
    load_dotenv()
    

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
        if not api_url:
            raise ValueError("API URL is not set in the environment variables.")
        return api_url

    def __getApiKey(self) -> str:
        """
        Retrieves the API key from environment variables (private method).

        Returns:
            str: The API key.
        """
        api_key = os.getenv("OPEN_WEB_UI_API_KEY").strip('"')
        if not api_key:
            raise ValueError("API key is not set in the environment variables.")
        return api_key
 
    def simpleChatWithModel(self, content: Optional[str] = None, model: str = 'llama3:8b') -> Optional[requests.Response]:
        """
        Sends a simple chat message to the specified model and retrieves the response.

        Args:
            content (Optional[str]): The message content to send to the model. If None, a default prompt is used.
            model (str): The model to interact with (default is 'llama3:8b').

        Returns:
            Optional[requests.Response]: The API response object if successful, None otherwise.
        """
        if content is None:
            content = "Hello, what can you do for me? Please provide a brief introduction about your capabilities."

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': content}]
        }
        
        try:
            response = requests.post(f'{self.api_url}/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error performing the chat. Details: {e}")
            return None

    def chatWithModel(self, knowledge: Optional[str] = None, commit_data: Optional[str] = None, content: Optional[str] = None, model: str = 'llama3:8b') -> Optional[requests.Response]:
        """
        Sends a chat message to the specified model and retrieves the response.

        Args:
            content (Optional[str]): The message content to send to the model. If None, a default prompt is used.
            model (str): The model to interact with (default is 'llama3.1:8b').
            knowledge (str): PDF file path with knowledge to be used in the chat.

        Returns:
            Optional[requests.Response]: The API response object if successful, None otherwise.
        """
            
        file_content = ""
        if knowledge:
            try:
                with open(knowledge, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            except FileNotFoundError:
                print(f"File not found: {knowledge}")
                return None

        context_instructions = (
            "You are an AI code assistant. Read and understand carefully guidelines about maintenance types and modification requests classification below.\n"
            "Do not generate anything yet. Wait for further instructions after reading.\n\n"
            "Guidelines:\n"
        )

        if content is None:
            content = (
                "Now read and understand carefully the following commit data which consists of its message and its code content. Do not generate anything yet.\n"
                "Wait for further instructions after reading.\n\n"
                "Commit data:"
            )

        finalContent = (
            "Based solely on the guidelines and commit data provided earlier, respond using ONLY the format below.\n"
            "Do NOT include any explanations, comments, or extra text. Do NOT change the format. Do NOT skip any lines.\n"
            "Use ONLY one of the allowed keywords listed in angle brackets <>. Follow the exact format below:\n\n"
            "Modification Request Classification: <correction | enhancement>\n"
            "Maintenance Type: <corrective | adaptive | preventive | perfective | additive>\n"
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
                    'content': f"""{context_instructions} \n {file_content} 
                    \n\n {content} \n {commit_data} 
                    \n{finalContent}""" if knowledge else content
                }
            ]
        }
        try:
            response = requests.post(f'{self.api_url}/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            if response.status_code != 200:
                print(f"Chat failed with status code: {response.status_code}")
            return response
        except Exception as e:
            print(f"Error performing the chat. Details: {e}")
            return None

    def evaluateCommitQualityChatWithModel(
        self, knowledge_files: Optional[List[str]] = None, commit_msg: Optional[str] = None,
        commit_files_changed: Optional[int] = None, content: Optional[str] = None,
        model: str = 'llama3:8b'
    ) -> Optional[requests.Response]:
        """
        Evaluates the quality of a Git commit using an LLM and reference guidelines.

        Args:
            knowledge (Optional[str]): Path to a PDF (converted to text) with commit quality guidelines.
            commit_msg (Optional[str]): The commit message as a string.
            commit_files_changed (Optional[int]): The number of files changed.
            content (Optional[str]): Optional override content prompt.
            model (str): The model name to query (default: 'llama3:8b').

        Returns:
            Optional[requests.Response]: The model's raw response in strict JSON format.
        """

        combined_knowledge = ""
        if knowledge_files:
            for path in knowledge_files:
                combined_knowledge += read_pdf_text(path).strip() + "\n\n"

        context_instructions = (
            "You are a Git commit analysis expert. Read the guidelines below carefully. "
            "They explain how to identify high-quality commits based on software engineering research "
            "regarding the presence of 'What' and 'Why' in commit messages, and the size of the change.\n\n"
            "Do not produce output yet. Wait for commit data.\n\n"
            "=== Guidelines ===\n"
        )

        if content is None:
            content = (
                "Now read the following Git commit data.\n"
                "Do not generate output yet. Wait for explicit output instructions.\n\n"
                "=== Commit Message ===\n"
                f"{commit_msg.strip() if commit_msg else ''}\n\n"
                "=== Files Changed ===\n"
                f"{commit_files_changed if commit_files_changed is not None else 0}\n\n"
            )

        finalContent = (
            "Based solely on the guidelines and commit data provided earlier, evaluate the commit quality.\n"
            "Respond ONLY in the exact JSON format below. Do NOT include explanations, comments, or any other text.\n\n"
            "Return this object (no modification, no extra keys):\n\n"
            "{\n"
            '  "what_present": <boolean value>,\n'
            '  "why_present": <boolean value>,\n'
            '  "files_changed": <integer value>\n'
            "}\n\n"
            "Use only boolean values (true/false) and an integer for files_changed.\n"
        )

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        full_prompt = f"{context_instructions}{combined_knowledge}\n\n{content}\n\n{finalContent}" if knowledge_files else content

        data = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': full_prompt
                }
            ]
        }

        try:
            response = requests.post(f'{self.api_url}/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            if response.status_code != 200:
                print(f"Chat failed with status code: {response.status_code}")
            return response
        except Exception as e:
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
