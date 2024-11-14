from pathlib import Path
from typing import List, Iterator, Iterable
from .errors import InvalidInputError

class InputCollection(Iterable):
    """
    Abstract base class for input collections.

    Provides an interface for different types of input collections used in file processing.
    Subclasses should implement `__iter__` and `__len__` methods to define custom behavior.
    """

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over file paths in the input collection."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Returns the number of files in the input collection."""
        raise NotImplementedError

class DirectoryInput(InputCollection):
    """
    Represents an input collection of files from a specified directory path.

    This class gathers file paths from the directory and optionally traverses subdirectories.

    Attributes:
        directory_path (Path): The path of the directory to gather files from.
        recursive (bool): If True, includes files in subdirectories.
        file_list (List[str]): List of file paths gathered from the directory.
    """

    def __init__(self, directory_path: str, recursive: bool = True):
        """
        Initializes the DirectoryInput with a specified directory path.

        Args:
            directory_path (str): Path to the directory containing files to process.
            recursive (bool): Whether to include files from subdirectories.

        Raises:
            InvalidInputError: If the directory path does not exist or is not a directory.
        """
        self.directory_path = Path(directory_path)
        if not self.directory_path.is_dir():
            raise InvalidInputError(f"Directory does not exist: {directory_path}")
        self.recursive = recursive
        self.file_list = self._gather_files()

    def _gather_files(self) -> List[str]:
        """
        Gathers all file paths from the specified directory.

        Returns:
            List[str]: List of file paths as strings.

        If recursive is True, files from subdirectories are also included.
        """
        if self.recursive:
            return [str(p) for p in self.directory_path.rglob('*') if p.is_file()]
        else:
            return [str(p) for p in self.directory_path.glob('*') if p.is_file()]

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the file paths in the directory."""
        return iter(self.file_list)

    def __len__(self) -> int:
        """Returns the number of files in the directory input collection."""
        return len(self.file_list)

class ListInput(InputCollection):
    """
    Represents an input collection based on a predefined list of file paths.

    Attributes:
        file_paths (List[str]): A list of file paths provided by the user.
    """

    def __init__(self, file_paths: List[str]):
        """
        Initializes the ListInput with a list of file paths.

        Args:
            file_paths (List[str]): A list of file paths to include in the input collection.
        """
        self.file_paths = [str(Path(p)) for p in file_paths]

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the list of file paths."""
        return iter(self.file_paths)

    def __len__(self) -> int:
        """Returns the number of files in the list input collection."""
        return len(self.file_paths)
