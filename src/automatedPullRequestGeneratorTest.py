# -*- coding: utf-8 -*-
import os
import sys
# Ensure the parent directory is in the system path for imports
from AutomatedPullRequestGenerator import AutomatedPullRequestGenerator
from src.client.openUiClient import OpenUiClient

def test_downloadPullRequestSamples():
    """
    Test the downloadPullRequestSamples method of AutomatedPullRequestGenerator.
    """
    generator = AutomatedPullRequestGenerator()
    file_map = generator.downloadPullRequestSamples()

    # Check if the folder exists
    assert os.path.exists(generator.folderPath), "Folder does not exist."

    # Check if files were created in the folder
    # files = os.listdir(generator.folderPath)
    # assert len(files) > 0, "No files were created in the folder."

    # Print all elements in the returned map if there are any
    if not file_map:
        print("No files were created.")
    else:
        for file_name, file_path in file_map.items():
            print(f"File Name: {file_name}, File Path: {file_path}")

def test_scanAllFilesInFolder():
    """
    Test the scanAllFilesInFolder method of AutomatedPullRequestGenerator.
    """
    generator = AutomatedPullRequestGenerator()
    files = generator.scanAllFilesInFolder()

    # Check if the folder exists
    assert os.path.exists(generator.folderPath), "Folder does not exist."

    # Check if files were scanned successfully
    # assert len(files) > 0, "No files were scanned in the folder."

    # # Print all scanned files
    for file in files:
        print(f"Scanned File: {file}")

    # Print total files scanned
    print(f"Total files scanned: {len(files)}")

def test_runAutomatedPullRequestGenerator(num_samples = 0):
    """
    Test the runAutomatedPullRequestGenerator method of AutomatedPullRequestGenerator.
    """
    generator = AutomatedPullRequestGenerator()
    openUiClient = OpenUiClient()

    models = openUiClient.getAvailableApiModels()[1:]
    print(f"Available models: {models}")

    totalModels = len(models)
    totalRuns = totalModels * num_samples
    count = 0
    for model in models:
        count += 1
        percent = int((count / totalRuns) * 100)
        bar_length = 30
        filled_length = int(bar_length * count // totalRuns)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print()
        print(f"Running for file: {model} ({count}/{totalRuns})")
        print(f"Running for models: {totalModels} - Completed: {count}/{totalRuns} ({percent}%)")
        print(f"\rProgress: |{bar}| {percent}% - Running for model: {model}", end='', flush=True)
        print()
        generator.runAutomatedPullRequestGenerator(num_samples, model=model)
    print()  # Move to next line after progress bar is complete

def test_runAutomatedPullRequestGeneratorForAllModels(num_samples=0):
    """
    Test the runAutomatedPullRequestGeneratorForAllModels method of AutomatedPullRequestGenerator.
    """
    generator = AutomatedPullRequestGenerator()
    generator.runAutomatedPullRequestGeneratorForAllModels(num_samples)

# Run test
# test_scanAllFilesInFolder()
# test_downloadPullRequestSamples()
# test_runAutomatedPullRequestGenerator(844)
test_runAutomatedPullRequestGeneratorForAllModels()
