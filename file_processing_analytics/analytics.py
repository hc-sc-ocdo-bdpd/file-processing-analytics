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
    def __init__(
        self,
        input_collection: Union[str, List[str], InputCollection, Path],
        output_csv_path: str,
        progress_tracker: ProgressTracker = None,
        log_level=logging.INFO,
    ):
        """
        Initializes the AnalyticsProcessor.

        :param input_collection: Directory path, list of file paths, or an InputCollection object.
        :param output_csv_path: Path to the output CSV file.
        :param progress_tracker: Optional ProgressTracker object.
        :param log_level: Logging level.
        """
        self.input_collection = self._init_input_collection(input_collection)
        self.output_csv_path = Path(output_csv_path)
        self.progress_tracker = progress_tracker or ProgressTracker()
        self.logger = self._init_logger(log_level)
        self._validate_output_path()

    def _init_logger(self, log_level):
        logger = logging.getLogger('AnalyticsProcessor')
        logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        return logger

    def _init_input_collection(self, input_collection):
        if isinstance(input_collection, InputCollection):
            return input_collection
        elif isinstance(input_collection, (str, Path)):  # Handle Path and string types
            return DirectoryInput(str(input_collection))
        elif isinstance(input_collection, list):
            return ListInput(input_collection)
        else:
            raise InvalidInputError("Invalid input collection type.")

    def _validate_output_path(self):
        if not self.output_csv_path.parent.exists():
            self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    def process_files(self):
        """
        Processes files and writes output to CSV.
        """
        total_files = len(self.input_collection)
        self.logger.info(f"Starting processing of {total_files} files.")

        with open(self.output_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                csv_writer.writerow(['file_name', 'text'])

            for file_path in tqdm(self.input_collection, total=total_files, unit='file'):
                if self.progress_tracker.is_processed(file_path):
                    self.logger.debug(f"Skipping already processed file: {file_path}")
                    continue
                try:
                    self.logger.info(f"Processing file: {file_path}")
                    file_obj = File(file_path)
                    text = file_obj.metadata.get('text', '').replace('\n', '\\n')  # Replace newlines
                    csv_writer.writerow([file_obj.file_name, text])
                    self.progress_tracker.mark_processed(file_path)
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {e}")
                    continue

        self.logger.info("Processing completed.")

