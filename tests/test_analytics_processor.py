import pytest
from file_processing_analytics import AnalyticsProcessor
from file_processing_analytics.errors import InvalidInputError
from file_processing_test_data import get_test_files_path
from file_processing_analytics.progress import ProgressTracker

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

    # Open the file using 'utf-8' encoding
    with open(output_csv, 'r', encoding='utf-8') as f:
        content = f.readlines()

    # Check that the first row is the header
    assert content[0].strip() == 'file_name,text'

    # Check that the number of files processed matches the number of lines (3 files + 1 header)
    assert len(content) == 4  # 3 files in the directory + 1 header line

    # Verify the file names in the first column (without verifying the text)
    expected_files = [
        '2021_Census_English.csv',
        'ArtificialNeuralNetworksForBeginners.pdf',
        'HealthCanadaOverviewFromWikipedia.docx'
    ]
    actual_files = [row.split(",")[0] for row in content[1:]]  # Skip header
    assert actual_files == expected_files




def test_invalid_input_type(progress_tracker):
    with pytest.raises(InvalidInputError):
        AnalyticsProcessor(12345, "output.csv", progress_tracker)

def test_list_input_processing(tmp_path, progress_tracker):
    test_files_path = get_test_files_path()
    test_files = [
        str(test_files_path / '2021_Census_English.csv'),
        str(test_files_path / 'ArtificialNeuralNetworksForBeginners.pdf')
    ]
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
    assert progress_tracker.is_processed(str(temp_directory_with_files / "2021_Census_English.csv"))
    assert progress_tracker.is_processed(str(temp_directory_with_files / "ArtificialNeuralNetworksForBeginners.pdf"))
    assert progress_tracker.is_processed(str(temp_directory_with_files / "HealthCanadaOverviewFromWikipedia.docx"))

    # Close the tracker
    progress_tracker.close()

    # Create a new progress tracker (simulating a new process start)
    new_progress_tracker = ProgressTracker(str(progress_tracker.db_path))
    processor = AnalyticsProcessor(temp_directory_with_files, str(output_csv), new_progress_tracker)

    # Simulate a second run and ensure no files are re-processed
    processor.process_files()

    with open(output_csv, 'r', encoding='utf-8') as f:
        content = f.readlines()

    # The number of lines should remain the same (header + 3 file entries)
    assert len(content) == 4

    # Close the new tracker after the second run
    new_progress_tracker.close()



