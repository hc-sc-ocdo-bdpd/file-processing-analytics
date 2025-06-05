import torch
print("Torch CUDA available? ", torch.cuda.is_available())   # → True

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
print("Loaded onto:", model.device)         