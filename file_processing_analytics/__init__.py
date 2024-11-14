"""
The file_processing_analytics package provides tools for analyzing and extracting
metadata from a collection of files. This package integrates with the file-processing
suite, allowing users to gather metadata from files and save results in CSV format,
track processing progress, and handle different input collections.

Classes:
    AnalyticsProcessor: Core class for orchestrating metadata extraction and error handling.
    ProgressTracker: Tracks processed files in a SQLite database for resumption support.
    DirectoryInput: Collects files from a specified directory, with optional recursion.
    ListInput: Collects files from a predefined list of file paths.
"""

from .analytics import AnalyticsProcessor
from .progress import ProgressTracker
from .input_collections import DirectoryInput, ListInput

__all__ = [
    "AnalyticsProcessor",
    "ProgressTracker",
    "DirectoryInput",
    "ListInput",
]
