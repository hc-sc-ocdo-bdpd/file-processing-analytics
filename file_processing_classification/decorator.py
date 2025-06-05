# ──────────────────────────────────────────────────────────────────────────────
# file_processing_classification/decorator.py
# ─────────────────────────────────────────────────────────────────────────────-

"""Plugin‑decorator so users can enable classification just like OCR."""

from __future__ import annotations

import logging
from importlib import resources
from pathlib import Path
from typing import Any, Callable

from .classifier import DocumentClassifier, classify_file
from . import get_default_labels_yaml      # ← correct location

LOGGER = logging.getLogger("file_processing_classification.decorator")

def _default_labels_yaml() -> str:
    return str(resources.files(__package__) / "labels.yaml")

class ClassificationDecorator:
    """Wrap a *File* object and inject classification metadata."""

    name: str = "classification"

    def __init__(
        self,
        *,
        labels_yaml: str | Path | None = None,
        threshold: float = 0.55,
        classifier: DocumentClassifier | None = None,
    ) -> None:
        labels_yaml = str(labels_yaml or _default_labels_yaml())
        self.classifier = classifier or DocumentClassifier(
            labels_yaml, threshold=threshold
        )

    # ------------------------------------------------------------------ #
    # file-processing calls *apply* after extraction                      #
    # ------------------------------------------------------------------ #
    def apply(self, file_obj: Any) -> Any:  # noqa: D401
        try:
            # use .text if present, otherwise fall back to metadata["text"]
            raw_text = getattr(file_obj, "text", file_obj.metadata.get("text", ""))
            label, conf = self.classifier.classify(raw_text, file_obj.metadata)
            file_obj.metadata.setdefault("classification", {})
            file_obj.metadata["classification"].update({"label": label, "confidence": conf})
            LOGGER.debug("%s → %s (%.4f)", file_obj.path, label, conf)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("classification failed for %s: %s", file_obj.path, exc)
        return file_obj

    __call__: Callable[[Any], Any] = apply  # alias so it behaves like a function