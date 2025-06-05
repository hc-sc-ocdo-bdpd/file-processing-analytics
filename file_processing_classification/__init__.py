# file_processing_classification/__init__.py
"""
file-processing-classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Zero-shot document classification plugin for the *file-processing* suite.
"""

from importlib import resources, import_module

from .classifier import DocumentClassifier, classify_file

__all__ = [
    "DocumentClassifier",
    "classify_file",
    "get_default_labels_yaml",
    "ClassificationDecorator",   # exported after lazy import
]


def get_default_labels_yaml() -> str:
    """Absolute path to built-in *labels.yaml* (no other imports needed)."""
    return str(resources.files(__package__) / "labels.yaml")


# ── lazy import to avoid circular dependencies ─────────────────────────
ClassificationDecorator = import_module(
    "file_processing_classification.decorator"
).ClassificationDecorator
