# -*- coding: utf-8 -*-
from openUiClient import OpenUiClient

# Create an instance of OpenUiClient
client = OpenUiClient()

# Get user input for the chat message
# content = input("Enter your message: ")

def test_chatWithModel():
    # Call the chatWithModel method using the client instance
    filePath = r'c:\Users\vicme\OneDrive\Livros Unicamp\TCC\Implementacao\AutomatedPullRequestGenerator\src\client\diffFiles.txt'
    # chat_response = client.chatWithModel(filePath=filePath)
    chat_response = client.chatWithModel(content="Hello, how are you?", model='llama3.1:8b')
    if chat_response:
        print("Status code:", chat_response.status_code)
        try:
            # Extract and print the chat response message
            chat_response_message = chat_response.json()['choices'][0]['message']['content']
            print("Chat response:", chat_response_message)
        except (KeyError, IndexError) as e:
            print(f"Error processing the chat response. Details: {e}")
    else:
        print("Unable to perform the chat.")

def test_getAvailableApiModels():
    model_ids = client.getAvailableApiModels()
    if model_ids is not None:
        print("Available model IDs:", model_ids)
    else:
        print("Unable to fetch available model IDs.")

# run tests
test_chatWithModel()
# test_getAvailableApiModels()
