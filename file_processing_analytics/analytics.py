# file_processing_analytics/analytics.py
"""
Process many files → CSV, with optional zero-shot classification.
"""

from __future__ import annotations
import argparse, csv, logging
from pathlib import Path
from typing import List, Optional, Union

from tqdm import tqdm
from file_processing import File
from .errors import InvalidInputError
from .input_collections import DirectoryInput, InputCollection, ListInput
from .progress import ProgressTracker

try:
    from file_processing_classification import ClassificationDecorator
except ImportError:
    ClassificationDecorator = None  # plug-in is optional


# ───────────────────────────────────────────────────────────────
class AnalyticsProcessor:
    def __init__(
        self,
        input_collection: Union[str, List[str], InputCollection, Path],
        output_csv_path: str | Path,
        *,
        progress_tracker: Optional[ProgressTracker] = None,
        log_level: int = logging.INFO,
        enable_classification: bool = False,
        labels_yaml: str | None = None,
        reset_progress: bool = False,
    ) -> None:

        # inputs ---------------------------------------------------
        self.input_collection = self._init_input_collection(input_collection)
        self.output_csv_path = Path(output_csv_path)

        # progress tracker ----------------------------------------
        self.progress_tracker = progress_tracker    # may be None
        if reset_progress and self.progress_tracker:
            if getattr(self.progress_tracker, "state_file", None):
                Path(self.progress_tracker.state_file).unlink(missing_ok=True)
            if hasattr(self.progress_tracker, "_processed"):
                self.progress_tracker._processed.clear()

        # logging -------------------------------------------------
        self.logger = self._init_logger(log_level)
        self._validate_output_path()

        # decorators ----------------------------------------------
        self.decorators: list = []
        if enable_classification:
            if ClassificationDecorator is None:
                raise ImportError("file-processing-classification not installed")
            self.decorators.append(ClassificationDecorator(labels_yaml=labels_yaml))

        self.logger.debug(
            "Decorators configured: %s",
            [getattr(d, "name", str(d)) for d in self.decorators],
        )

    # ───────── helpers ─────────
    @staticmethod
    def _init_logger(level: int) -> logging.Logger:
        logger = logging.getLogger("AnalyticsProcessor")
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.handlers.clear()
        logger.addHandler(handler)
        return logger

    def _init_input_collection(
        self, src: Union[str, List[str], InputCollection, Path]
    ) -> InputCollection:
        if isinstance(src, InputCollection):
            return src
        if isinstance(src, (str, Path)):
            return DirectoryInput(str(src))
        if isinstance(src, list):
            return ListInput(src)
        raise InvalidInputError("Invalid input collection type.")

    def _validate_output_path(self) -> None:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    def _apply_decorators(self, file_obj: File) -> File:
        for deco in self.decorators:
            file_obj = deco(file_obj)
        return file_obj

    # ───────── main loop ───────
    def process_files(self) -> None:
        total = len(self.input_collection)
        self.logger.info("Starting processing of %s files.", total)

        summary_rows: list[tuple[str, str, str]] = []

        # clear in-memory list if tracker is reset this run
        if self.progress_tracker and hasattr(self.progress_tracker, "_processed"):
            self.progress_tracker._processed.clear()

        # open CSV once
        with open(self.output_csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(  # header
                ["file_name", "text", "classification_label",
                 "classification_confidence", "error"]
            )

            for file_path in tqdm(self.input_collection, total=total, unit="file"):
                if self.progress_tracker and self.progress_tracker.is_processed(file_path):
                    self.logger.debug("Skipping already processed file: %s", file_path)
                    continue

                try:
                    f = File(file_path)
                    f = self._apply_decorators(f)

                    text = getattr(f, "text", f.metadata.get("text", "")).replace("\n", "\\n")
                    cls  = f.metadata.get("classification", {})
                    label = cls.get("label", "")
                    conf  = cls.get("confidence", "")

                    writer.writerow([Path(file_path).name, text, label, conf, ""])
                    if self.progress_tracker:
                        self.progress_tracker.mark_processed(file_path)

                    summary_rows.append(  # success row
                        (Path(file_path).name[:40].ljust(40),
                         label.ljust(20),
                         f"{float(conf):6.2f}" if conf else "  --- ")
                    )

                    self.logger.debug(
                        "CLASSIFIED %s → %s (%.4f)", Path(file_path).name, label, conf or 0.0
                    )

                except Exception as exc:
                    self.logger.error("Error processing %s: %s", file_path, exc)
                    writer.writerow([Path(file_path).name, "", "", "", str(exc)])
                    if self.progress_tracker:
                        self.progress_tracker.mark_processed(file_path)

                    summary_rows.append(  # error row
                        (Path(file_path).name[:40].ljust(40),
                         "Error".ljust(20),
                         "  --- ")
                    )

        # ─── pretty-print summary table ─────────────────────────
        if summary_rows:
            print("\n" + "─" * 8)
            print(" Document".ljust(42) + "│ Predicted label       │ Conf")
            print("─" * 78)
            for fn, lab, conf in summary_rows:
                print(f" {fn} │ {lab} │ {conf}")
            print("─" * 78)

        self.logger.info(
            "Processing completed. Wrote %d rows → %s",
            len(summary_rows),
            self.output_csv_path,
        )


# ───────── CLI ─────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("file-processing-analytics")
    p.add_argument("--input", required=True, help="Directory or list file")
    p.add_argument("--output", required=True, help="CSV output path")
    p.add_argument("--enable-classification", action="store_true",
                   help="Run zero-shot document classification")
    p.add_argument("--labels-yaml", help="Custom labels YAML (optional)")
    p.add_argument("--resume", action="store_true",
                   help="Resume from .analytics_progress.jsonl")
    p.add_argument("--loglevel", default="INFO",
                   choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p


def main() -> None:  # pragma: no cover
    args = _build_parser().parse_args()
    level = getattr(logging, args.loglevel.upper(), logging.INFO)

    tracker = ProgressTracker() if args.resume else None

    AnalyticsProcessor(
        input_collection=args.input,
        output_csv_path=args.output,
        log_level=level,
        enable_classification=args.enable_classification,
        labels_yaml=args.labels_yaml,
        progress_tracker=tracker,
    ).process_files()


if __name__ == "__main__":  # pragma: no cover
    main()
