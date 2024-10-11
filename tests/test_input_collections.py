import pytest
from file_processing_analytics.input_collections import DirectoryInput, ListInput
from file_processing_analytics.errors import InvalidInputError
from file_processing_test_data import get_test_files_path

def test_directory_input(temp_directory_with_files):
    input_collection = DirectoryInput(temp_directory_with_files)
    assert len(input_collection) == 3  # Three files in the temp directory

def test_directory_input_recursive(temp_directory_with_files):
    subdir = temp_directory_with_files / "subdir"
    subdir.mkdir()
    (subdir / "new_file.txt").write_text("Some content")

    input_collection = DirectoryInput(temp_directory_with_files)
    assert len(input_collection) == 4  # Now includes the new file in subdir

def test_list_input():
    test_files_path = get_test_files_path()
    file_list = [
        str(test_files_path / '2021_Census_English.csv'),
        str(test_files_path / 'ArtificialNeuralNetworksForBeginners.pdf')
    ]
    input_collection = ListInput(file_list)

    assert len(input_collection) == 2

def test_invalid_directory():
    with pytest.raises(InvalidInputError):
        DirectoryInput("invalid_directory_path")
