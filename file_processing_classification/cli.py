# ─────────────────────────────────────────────────────────────────────────────-
# file_processing_classification/cli.py
# ─────────────────────────────────────────────────────────────────────────────-

import argparse
from pathlib import Path

from file_processing import File
from .classifier import DocumentClassifier, classify_file, get_default_labels_yaml


def _build() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("file-processing-classification tester")
    p.add_argument("file", help="Path to a document to classify")
    p.add_argument(
        "--labels",
        type=Path,
        default=get_default_labels_yaml(),
        help="Optional custom labels YAML",
    )
    p.add_argument("--threshold", type=float, default=0.55)
    return p


def main() -> None:  # pragma: no cover
    args = _build().parse_args()
    clf = DocumentClassifier(args.labels, threshold=args.threshold)
    f = File(args.file)
    label, conf = classify_file(f, clf)
    print(f"{args.file} → {label} ({conf:.2f})")


if __name__ == "__main__":  # pragma: no cover
    main()