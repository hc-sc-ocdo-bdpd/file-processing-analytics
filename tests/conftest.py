import shutil
import pytest
from pathlib import Path
from file_processing_test_data import get_test_files_path
from file_processing_analytics import AnalyticsProcessor, ProgressTracker
from file_processing_analytics.input_collections import DirectoryInput, ListInput

# Fixture to set up temporary directory with test files
@pytest.fixture(scope="function")
def temp_directory_with_files(tmp_path_factory):
    test_files_path = get_test_files_path()
    temp_dir = tmp_path_factory.mktemp("temp_test_dir")

    # Copy some test files into the temp directory
    test_files = [
        '2021_Census_English.csv',
        'ArtificialNeuralNetworksForBeginners.pdf',
        'HealthCanadaOverviewFromWikipedia.docx'
    ]
    for file_name in test_files:
        shutil.copy(test_files_path / file_name, temp_dir)
    
    return temp_dir

# Fixture to set up a temporary SQLite progress tracking database
@pytest.fixture(scope="function")
def progress_tracker(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("progress") / ".progress.db"
    return ProgressTracker(str(db_path))
