import pytest
from file_processing_analytics.progress import ProgressTracker

def test_progress_tracker_mark_processed(progress_tracker):
    file_path = "some/file/path.csv"
    progress_tracker.mark_processed(file_path)

    # Check if the file is marked as processed
    assert progress_tracker.is_processed(file_path)

def test_progress_tracker_unprocessed_file(progress_tracker):
    file_path = "unprocessed/file/path.csv"

    # File should not be marked as processed
    assert not progress_tracker.is_processed(file_path)

def test_progress_tracker_persistence(progress_tracker, tmp_path_factory):
    file_path = "some/file/path.csv"
    progress_tracker.mark_processed(file_path)

    # Simulate reopening the progress tracker (simulates persistence via SQLite)
    new_tracker = ProgressTracker(str(progress_tracker.db_path))
    
    assert new_tracker.is_processed(file_path)
