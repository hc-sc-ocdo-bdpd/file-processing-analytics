import pytest
import pandas as pd
from file_processing_analytics import AnalyticsProcessor
from file_processing_analytics.errors import InvalidInputError
from file_processing_test_data import get_test_files_path, get_all_test_files
from file_processing_analytics.progress import ProgressTracker
from pathlib import Path

def test_process_directory(temp_directory_with_files, tmp_path, progress_tracker):
    output_csv = tmp_path / "output.csv"

    # Process the directory and check if it creates a CSV file
    processor = AnalyticsProcessor(temp_directory_with_files, str(output_csv), progress_tracker)
    processor.process_files()

    assert output_csv.exists()

def test_csv_content(temp_directory_with_files, tmp_path, progress_tracker):
    output_csv = tmp_path / "output.csv"

    processor = AnalyticsProcessor(temp_directory_with_files, str(output_csv), progress_tracker)
    processor.process_files()

    # Use pandas to read the CSV
    df = pd.read_csv(output_csv)

    # Check that the first row is the header and has the correct columns
    expected_columns = ['file_name', 'text', 'error']
    assert list(df.columns) == expected_columns

    # Get the number of test files
    num_test_files = len(get_all_test_files())
    print(f"Number of test files: {num_test_files}")

    # Print the actual number of rows in the DataFrame
    print(f"Number of rows in DataFrame: {len(df)}")

    # Continue with the assertion
    assert len(df) == num_test_files


def test_invalid_input_type(progress_tracker):
    with pytest.raises(InvalidInputError):
        AnalyticsProcessor(12345, "output.csv", progress_tracker)

def test_list_input_processing(tmp_path, progress_tracker):
    test_files = get_all_test_files()
    output_csv = tmp_path / "output.csv"

    processor = AnalyticsProcessor(test_files, str(output_csv), progress_tracker)
    processor.process_files()

    assert output_csv.exists()

def test_progress_tracking(temp_directory_with_files, tmp_path, progress_tracker):
    output_csv = tmp_path / "output.csv"

    # Process the directory first time
    processor = AnalyticsProcessor(temp_directory_with_files, str(output_csv), progress_tracker)
    processor.process_files()

    # Check that progress is tracked for files before closing the tracker
    all_test_files = [str(temp_directory_with_files / Path(f).name) for f in get_all_test_files()]
    for file_path in all_test_files:
        assert progress_tracker.is_processed(file_path)

    # Close the tracker
    progress_tracker.close()

    # Create a new progress tracker (simulating a new process start)
    new_progress_tracker = ProgressTracker(str(progress_tracker.db_path))
    processor = AnalyticsProcessor(temp_directory_with_files, str(output_csv), new_progress_tracker)

    # Simulate a second run and ensure no files are re-processed
    processor.process_files()

    # Use pandas to read the CSV after the second run
    df = pd.read_csv(output_csv)

    # The number of rows should remain the same (all files should already have been processed)
    num_test_files = len(get_all_test_files())
    assert len(df) == num_test_files  # No additional rows should be added

    # Close the new tracker after the second run
    new_progress_tracker.close()
