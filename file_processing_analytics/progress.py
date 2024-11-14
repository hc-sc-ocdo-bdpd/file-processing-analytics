import sqlite3
from pathlib import Path

class ProgressTracker:
    """
    Tracks file processing progress using a SQLite database.

    This class stores a record of processed files, allowing the process to resume
    from where it left off. Each processed file is marked in the database, ensuring
    that already processed files are not processed again.
    """

    def __init__(self, db_path: str = None):
        """
        Initializes the ProgressTracker with an optional database path.

        Args:
            db_path (str, optional): Path to the SQLite database file. Defaults to '.progress.db' in the current directory.
        """
        self.db_path = Path(db_path) if db_path else Path('.progress.db')
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_table()

    def _create_table(self):
        """
        Creates the `processed_files` table in the database if it does not exist.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_files (
                file_path TEXT PRIMARY KEY
            )
        ''')
        self.conn.commit()

    def is_processed(self, file_path: str) -> bool:
        """
        Checks if a file has already been processed.

        Args:
            file_path (str): Path of the file to check.

        Returns:
            bool: True if the file has been processed, False otherwise.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM processed_files WHERE file_path = ?', (file_path,))
        return cursor.fetchone() is not None

    def mark_processed(self, file_path: str):
        """
        Marks a file as processed by adding its path to the database.

        Args:
            file_path (str): Path of the file to mark as processed.
        """
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)', (file_path,))
        self.conn.commit()

    def close(self):
        """
        Closes the connection to the SQLite database.
        """
        self.conn.close()
