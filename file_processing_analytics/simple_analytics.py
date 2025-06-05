"""
simple_analytics.py – minimal directory-to-CSV utility with optional
zero-shot document classification.

Example
-------
python -m file_processing_analytics.simple_analytics \
       --input sample_docs \
       --output result.csv \
       --enable-classification \
       --loglevel DEBUG
"""
from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path
from typing import List

from tqdm import tqdm
from file_processing import File  # ← core extractor

# ---------------------------------------------------- optional classification
try:
    from file_processing_classification import (
        DocumentClassifier,
        get_default_labels_yaml,
    )
except ImportError:  # plug-in not installed
    DocumentClassifier = None
    classify_file = None
    get_default_labels_yaml = lambda: None  # type: ignore

# ---------------------------------------------------- processing helper
def process_directory(
    input_dir: Path,
    output_csv: Path,
    *,
    enable_classification: bool,
    labels_yaml: str | None,
    logger: logging.Logger,
) -> None:
    if enable_classification and DocumentClassifier is None:
        raise ImportError(
            "Classification flag passed but file_processing_classification "
            "is not installed."
        )

    classifier = None
    if enable_classification:
        labels_yaml = labels_yaml or get_default_labels_yaml()
        classifier = DocumentClassifier(labels_yaml)

    files: List[Path] = [p for p in input_dir.iterdir() if p.is_file()]
    logger.info("Found %d files in %s", len(files), input_dir)

    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "file_name",
                "text",
                "classification_label",
                "classification_confidence",
                "error",
            ]
        )

        for p in tqdm(files, unit="file"):
            try:
                f = File(p)
                label, conf = "", ""

                if classifier:
                    raw_text = getattr(f, "text", f.metadata.get("text", ""))
                    label, conf = classifier.classify(raw_text, f.metadata)
                    logger.debug(
                        "CLASSIFIED %s → %s (%.4f)", p.name, label, conf
                    )

                writer.writerow(
                    [
                        p.name,
                        (getattr(f, "text", f.metadata.get("text", "")).replace("\n", "\\n")),
                        label,
                        conf,
                        "",
                    ]
                )
            except Exception as exc:
                logger.error("⚠ error %s: %s", p, exc)
                writer.writerow([p.name, "", "", "", str(exc)])


# ---------------------------------------------------- CLI scaffolding
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("simple-analytics")
    p.add_argument("--input", required=True, help="Directory of documents")
    p.add_argument("--output", required=True, help="CSV output path")
    p.add_argument(
        "--enable-classification",
        action="store_true",
        help="Run zero-shot document classification",
    )
    p.add_argument("--labels-yaml", help="Custom labels YAML (optional)")
    p.add_argument(
        "--loglevel",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return p


def main() -> None:  # pragma: no cover
    args = build_parser().parse_args()

    logger = logging.getLogger("simple-analytics")
    logger.setLevel(getattr(logging, args.loglevel))
    logging.basicConfig(format="[%(levelname)s] %(message)s")

    process_directory(
        input_dir=Path(args.input).expanduser().resolve(),
        output_csv=Path(args.output).expanduser().resolve(),
        enable_classification=args.enable_classification,
        labels_yaml=args.labels_yaml,
        logger=logger,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
