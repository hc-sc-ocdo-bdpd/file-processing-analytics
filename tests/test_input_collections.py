import pytest
from file_processing_analytics.input_collections import DirectoryInput, ListInput
from file_processing_analytics.errors import InvalidInputError
from file_processing_test_data import get_all_test_files

def test_directory_input(temp_directory_with_files):
    input_collection = DirectoryInput(temp_directory_with_files)
    num_test_files = len(get_all_test_files())
    assert len(input_collection) == num_test_files

def test_directory_input_recursive(temp_directory_with_files):
    subdir = temp_directory_with_files / "subdir"
    subdir.mkdir()
    (subdir / "new_file.txt").write_text("Some content")

    input_collection = DirectoryInput(temp_directory_with_files)
    assert len(input_collection) == len(get_all_test_files()) + 1 

def test_list_input():
    file_list = get_all_test_files()
    input_collection = ListInput(file_list)

    assert len(input_collection) == len(file_list)

def test_invalid_directory():
    with pytest.raises(InvalidInputError):
        DirectoryInput("invalid_directory_path")
