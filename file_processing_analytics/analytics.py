import logging
import csv
from pathlib import Path
from typing import Union, List
from file_processing import File
from .input_collections import InputCollection, DirectoryInput, ListInput
from .progress import ProgressTracker
from .errors import InvalidInputError
from tqdm import tqdm

class AnalyticsProcessor:
    """
    The core class for processing files to extract metadata and store it in CSV format.

    This class orchestrates the file processing, metadata extraction, and error handling.
    It supports directory-based and list-based input collections and allows resuming long-running tasks.
    """

    def __init__(
        self,
        input_collection: Union[str, List[str], InputCollection, Path],
        output_csv_path: str,
        progress_tracker: ProgressTracker = None,
        log_level=logging.INFO,
    ):
        """
        Initializes the AnalyticsProcessor.

        Args:
            input_collection (Union[str, List[str], InputCollection, Path]): Directory path, list of file paths,
                or an InputCollection object for processing.
            output_csv_path (str): Path to the output CSV file where results will be stored.
            progress_tracker (ProgressTracker, optional): Tracker for processed files, allowing task resumption.
            log_level (int, optional): Logging level, with default set to INFO.
        """
        self.input_collection = self._init_input_collection(input_collection)
        self.output_csv_path = Path(output_csv_path)
        self.progress_tracker = progress_tracker or ProgressTracker()
        self.logger = self._init_logger(log_level)
        self._validate_output_path()

    def _init_logger(self, log_level):
        """
        Initializes and returns a logger for tracking file processing progress and errors.

        Args:
            log_level (int): The logging level to set.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger('AnalyticsProcessor')
        logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        return logger

    def _init_input_collection(self, input_collection):
        """
        Initializes the input collection based on the provided input type.

        Args:
            input_collection (Union[str, List[str], InputCollection, Path]): The input files for processing,
                specified as a directory path, list of file paths, or an InputCollection object.

        Returns:
            InputCollection: The initialized input collection.

        Raises:
            InvalidInputError: If an invalid type is provided for input_collection.
        """
        if isinstance(input_collection, InputCollection):
            return input_collection
        elif isinstance(input_collection, (str, Path)):
            return DirectoryInput(str(input_collection))
        elif isinstance(input_collection, list):
            return ListInput(input_collection)
        else:
            raise InvalidInputError("Invalid input collection type.")

    def _validate_output_path(self):
        """
        Validates and creates the output directory if it doesn't exist.
        """
        if not self.output_csv_path.parent.exists():
            self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    def process_files(self):
        """
        Processes files in the input collection and writes metadata and errors to the CSV output.

        This method iterates through each file in the input collection, extracts metadata,
        and logs errors as they occur. Processed file names are tracked for resumption support.
        """
        total_files = len(self.input_collection)
        self.logger.info(f"Starting processing of {total_files} files.")

        with open(self.output_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:  # Write header if file is empty
                csv_writer.writerow(['file_name', 'text', 'error'])

            for file_path in tqdm(self.input_collection, total=total_files, unit='file'):
                if self.progress_tracker.is_processed(file_path):
                    self.logger.debug(f"Skipping already processed file: {file_path}")
                    continue
                try:
                    self.logger.info(f"Processing file: {file_path}")
                    file_obj = File(file_path)
                    text = file_obj.metadata.get('text', '').replace('\n', '\\n')  # Replace newlines
                    csv_writer.writerow([file_obj.file_name, text, ''])
                    self.progress_tracker.mark_processed(file_path)
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {e}")
                    csv_writer.writerow([Path(file_path).name, '', str(e)])
                    self.progress_tracker.mark_processed(file_path)
                    continue

        self.logger.info("Processing completed.")
