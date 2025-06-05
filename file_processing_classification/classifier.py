# ──────────────────────────────────────────────────────────────────────────────
# file_processing_classification/classifier.py
# ─────────────────────────────────────────────────────────────────────────────-

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

import numpy as np
import yaml
from sentence_transformers import SentenceTransformer, util
import torch

LOGGER = logging.getLogger("file_processing_classification.classifier")

#DEFAULT_MODEL = "sentence-transformers/all-mpnet-base-v2"
# Moving to a large model to improve accuracy
# python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# python -m pip install sentence-transformers>=2.7
#DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"
DEFAULT_MODEL = "intfloat/e5-large-v2"
DEFAULT_THRESHOLD = 0.48   




class DocumentClassifier:
    """Zero‑shot classifier: document → (label, confidence)."""

    def __init__(
        self,
        labels_yaml: str | Path,
        *,
        threshold: float = DEFAULT_THRESHOLD,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        batch_size: int = 1,  # reserved for future batching
    ) -> None:
        import torch

        # pick the requested device or auto-detect CUDA
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    
        # self.model = SentenceTransformer(model_name, device=self.device)
        self.model = SentenceTransformer(
            model_name,
            device="cuda",
            # 8-bit is optional; remove if you prefer fp16
            #load_in_8bit=True,  # using 16 bit precision
            # ↓ key line: never touch .bin files → no torch.load → no CVE guard
            model_kwargs={"trust_remote_code": True},
        )
        self.batch_size = batch_size
        self.threshold = threshold

        with open(labels_yaml, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        self.labels: List[str] = list(cfg.keys())
        prompts: List[str] = list(cfg.values())

        LOGGER.info("Embedding %d label prompts on %s …", len(prompts), self.device)
        # pre-compute label embeddings on *the same device* as the model
        self.label_emb = self.model.encode(
            prompts,
            convert_to_tensor=True,
            normalize_embeddings=True,
            batch_size=self.batch_size,
        )

    # ---------------------------------------------------------------------
    def classify(self, text: str, meta: Optional[Dict] = None) -> Tuple[str, float]:
        if not text:
            return "Other", 0.0

        meta_tokens: List[str] = []
        if meta:
            meta_tokens.extend(
                [
                    str(meta.get("author", "")),
                    str(meta.get("file_type", "")),
                    str(meta.get("producer", "")),
                ]
            )
        joined = f"{text} {' '.join(meta_tokens)}".strip()

        emb = self.model.encode(
            joined,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        # cosine similarity stays on GPU; use torch ops, then .item()
        scores     = util.cos_sim(emb, self.label_emb)[0]      # 1-D tensor
        best_idx   = int(torch.argmax(scores).item())
        best_score = float(scores[best_idx].item())

        if best_score < self.threshold:
            return "Other", best_score
        return self.labels[best_idx], best_score


# -------------------------------------------------------------------------

def classify_file(file_obj, classifier: DocumentClassifier) -> Tuple[str, float]:
    """Helper that writes classification result into *file_obj.metadata*."""
    label, conf = classifier.classify(file_obj.text, getattr(file_obj, "metadata", {}))
    file_obj.metadata.setdefault("classification", {})
    file_obj.metadata["classification"].update(
        {
            "label": label,
            "confidence": round(conf, 4),
        }
    )
    return label, conf