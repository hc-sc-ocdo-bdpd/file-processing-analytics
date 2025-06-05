# file_processing_analytics/progress.py
import json
from pathlib import Path
from typing import Set

class ProgressTracker:
    def __init__(self, state_file: str | Path | None = ".analytics_progress.jsonl"):
        self.state_file = Path(state_file) if state_file else None
        self._processed: Set[str] = set()
        if self.state_file and self.state_file.exists():
            with self.state_file.open(encoding="utf-8") as fh:
                for line in fh:
                    self._processed.add(line.strip())

    # existing helpers …
    def is_processed(self, file_path: str | Path) -> bool:
        return str(file_path) in self._processed

    def mark_processed(self, file_path: str | Path) -> None:
        fp = str(file_path)
        if fp not in self._processed:
            with self.state_file.open("a", encoding="utf-8") as fh:
                fh.write(fp + "\n")
            self._processed.add(fp)

    # --- NEW ---------------------------------------------------------
    def reset(self) -> None:
        """Erase progress state so the next run processes everything."""
        if self.state_file.exists():
            self.state_file.unlink()
        self._processed.clear()
