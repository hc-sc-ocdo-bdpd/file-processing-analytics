import sqlite3
from pathlib import Path

class ProgressTracker:
    """
    Tracks progress using a SQLite database.
    """
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else Path('.progress.db')
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_files (
                file_path TEXT PRIMARY KEY
            )
        ''')
        self.conn.commit()

    def is_processed(self, file_path: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM processed_files WHERE file_path = ?', (file_path,))
        return cursor.fetchone() is not None

    def mark_processed(self, file_path: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)', (file_path,))
        self.conn.commit()

    def close(self):
        self.conn.close()
