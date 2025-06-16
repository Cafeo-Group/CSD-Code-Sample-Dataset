import sys
import os
import logging
import time
from tqdm import tqdm
from typing import Optional

print("Current working directory:", os.getcwd())

from openUiClient import OpenUiClient

client = OpenUiClient()
models = ['deepseek-r1:14b',
          'llama3:8b', 
          'qwen:1.8b',
          'phi:latest', 
          'stable-code:latest', 
          'gemma3:12b',
          'phi4-reasoning:latest',
          'llama3.2-vision:11b'
          ]

def read_json(file_path):
        """
        Read a JSON file and return its content.
        
        :param file_path: The path of the JSON file to read.
        :return: The content of the JSON file as a dictionary.
        """
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {file_path}: {e}")
            return None

def test_chatWithSeveralModels():
    filePath = r'C:\Users\oheit\Desktop\UNICAMP\IC code samples\projs\finer\golden_set.json'
    json_data = read_json(filePath)
    responses = []
    
    knowledge_file = r'C:\Users\oheit\Desktop\UNICAMP\IC code samples\projs\finer\src\knowledge\Guidelines.txt'
    
    for index, item in json_data.items():
        repos = item
        for repo in tqdm(repos, desc='Processing repos', leave=False):
            main_content = []
            commits = repo.get('commits', [])

            for commit in tqdm(commits, desc='Processing commits', leave=False):
                commit_message = commit.get('message', '')
                files = commit.get('files', [])
                main_content.append(f"""Commit Message: {commit_message}
                                    Commit SHA: {commit.get('sha', '')}
                                    Commit Link: {commit.get('link', '')}
                                    Files in the commit:
                                    {files}""")
            
            for content in main_content:
                for model in models:
                    print(f"\nUsing model: {model}")
                    max_retries = 3
                    for attempt in range(max_retries):
                        chat_response = client.chatWithModel(knowledge=knowledge_file, commit_data=content, model=model)
                        if chat_response:
                            print("Status code:", chat_response.status_code)
                            try:
                                chat_response_message = chat_response.json()['choices'][0]['message']['content']
                                print("Chat response:", chat_response_message)
                                responses.append({
                                    'model': model,
                                    'response': chat_response_message,
                                })
                                break
                            except (KeyError, IndexError) as e:
                                print(f"Error processing the chat response. Details: {e}")
                                break
                        else:
                            print("Unable to perform the chat.")
                            if attempt < max_retries - 1:
                                print(f"Retrying ({attempt+1}/{max_retries}) after 10 seconds...")
                                time.sleep(2)
                            else:
                                print("Max retries reached. Skipping this request.")
                    time.sleep(0.5)
    return responses

def test_chatWithModel(model: Optional[str] = 'llama3.1:8b'):
    # Call the chatWithModel method using the client instance
    filePath = r'C:\Users\oheit\Desktop\UNICAMP\IC code samples\projs\finer\golden_set.json'
    json_data = read_json(filePath)
    responses = []
    
    knowledge_file = r'C:\Users\oheit\Desktop\UNICAMP\IC code samples\projs\finer\src\commits\Guidelines.txt'
    
    for index, item in json_data.items():
        repos = item
        for repo in tqdm(repos, desc='Processing repos', leave=False):
            main_content = []
            commits = repo.get('commits', [])

            for commit in tqdm(commits, desc='Processing commits', leave=False):
                commit_message = commit.get('message', '')
                files = commit.get('files', [])
                main_content.append((commit.get('link'), f"""Commit Message: {commit_message}
                                    Files in the commit:
                                    {files}"""))
            
            for content in main_content:
                chat_response = client.chatWithModel(knowledge=knowledge_file, commit_data=content[1], model=model)
                if chat_response:
                    print("Status code:", chat_response.status_code)
                    try:
                        chat_response_message = chat_response.json()['choices'][0]['message']['content']
                        print("Chat response:\n", chat_response_message)
                        responses.append({
                            'model': model,
                            'link': content[0],
                            'response': chat_response_message,
                        })
                    except (KeyError, IndexError) as e:
                        print(f"Error processing the chat response. Details: {e}")
                else:
                    print("Unable to perform the chat.")
                time.sleep(0.5)
    return responses

def save_output(output: str, file_path: str):
    """
    Save the output to a file.
    
    :param output: The content to save.
    :param file_path: The path of the file where the content will be saved.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        for response in output:
            file.write(f"Model: {response['model']}\n")
            file.write(f"{response['response']}\n\n")

response = client.getAvailableApiModels()
print("Available models:", response)

output_stable_code = test_chatWithModel()
save_output(output_stable_code, r'C:\Users\oheit\Desktop\UNICAMP\IC code samples\projs\finer\output_for_llama3_model.txt')

# output_all_models = test_chatWithSeveralModels()
# save_output(output_all_models, r'C:\Users\oheit\Desktop\UNICAMP\IC code samples\projs\finer\output_for_all_models.txt')