import shutil
import pytest
from pathlib import Path
from file_processing_test_data import get_test_files_path, get_all_test_files
from file_processing_analytics.analytics import AnalyticsProcessor, ProgressTracker
from file_processing_analytics.input_collections import DirectoryInput, ListInput

# Fixture to set up temporary directory with all test files
@pytest.fixture(scope="function")
def temp_directory_with_files(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("temp_test_dir")

    # Get all test files (full paths)
    test_files = get_all_test_files()
    for file_path in test_files:
        shutil.copy(file_path, temp_dir)

    return temp_dir

# Fixture to set up a temporary SQLite progress tracking database
@pytest.fixture(scope="function")
def progress_tracker(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("progress") / ".progress.db"
    return ProgressTracker(str(db_path))
