# file_processing_analytics/input_collections.py

from pathlib import Path
from typing import List, Iterator, Iterable
from .errors import InvalidInputError

class InputCollection(Iterable):
    """
    Abstract base class for input collections.
    """
    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

class DirectoryInput(InputCollection):
    """
    Input collection from a directory path.
    """
    def __init__(self, directory_path: str, recursive: bool = True):
        self.directory_path = Path(directory_path)
        if not self.directory_path.is_dir():
            raise InvalidInputError(f"Directory does not exist: {directory_path}")
        self.recursive = recursive
        self.file_list = self._gather_files()

    def _gather_files(self) -> List[str]:
        if self.recursive:
            return [str(p) for p in self.directory_path.rglob('*') if p.is_file()]
        else:
            return [str(p) for p in self.directory_path.glob('*') if p.is_file()]

    def __iter__(self) -> Iterator[str]:
        return iter(self.file_list)

    def __len__(self) -> int:
        return len(self.file_list)

class ListInput(InputCollection):
    """
    Input collection from a list of file paths.
    """
    def __init__(self, file_paths: List[str]):
        self.file_paths = [str(Path(p)) for p in file_paths]

    def __iter__(self) -> Iterator[str]:
        return iter(self.file_paths)

    def __len__(self) -> int:
        return len(self.file_paths)
