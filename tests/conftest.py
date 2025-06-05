import csv
import re
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
import shutil
import pytest
from file_processing_test_data import get_all_test_files
from file_processing_analytics.analytics import ProgressTracker
from file_processing_classification.classifier import DocumentClassifier

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

# Test data directory with copies of all sample files
@pytest.fixture(scope="function")
def temp_directory_with_files(tmp_path_factory):
    """Return a temp dir that contains a copy of every test file."""
    temp_dir = tmp_path_factory.mktemp("temp_test_dir")
    for src in get_all_test_files():
        shutil.copy(src, temp_dir)
    return temp_dir

# Progress-tracking DB (optional)
@pytest.fixture(scope="function")
def progress_tracker(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("progress") / ".progress.db"
    return ProgressTracker(str(db_path))


# labels.yaml fixture ­– copied so tests never touch the real file
@pytest.fixture(scope="session")
def labels_yaml(tmp_path_factory):
    src = Path(__file__).parents[1] / "file_processing_classification" / "labels.yaml"
    dst = tmp_path_factory.mktemp("labels") / "labels.yaml"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dst

# Re-usable classifier object (saves embedding cost)
@pytest.fixture(scope="session")
def classifier(labels_yaml):
    return DocumentClassifier(labels_yaml)



# OPTIONAL: clear HF cache between sessions (helps CI)
@pytest.fixture(scope="session", autouse=False)
def clean_venv_cache():
    cache_dir = Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface"))
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    yield
