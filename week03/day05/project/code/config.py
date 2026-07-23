# config.py
import os

# File Paths
INPUT_DIR = "inputs"
REGISTRY_PATH = "processing_registry.json"
CHUNKS_DIR = os.path.join("outputs", "chunks")
SUMMARIES_DIR = os.path.join("outputs", "summaries")

# Text Encoding
TEXT_ENCODING = "utf-8"

# Model Configurations
EMBEDDING_MODEL = "mxbai-embed-large"
SUMMARIZATION_MODEL = "llama3"
OLLAMA_KEEP_ALIVE = "5m"

# NLP Processing Configurations
STANZA_LANGUAGE = "en"
STANZA_USE_GPU = True
BREAKPOINT_PERCENTILE = 80.0
BUFFER_SIZE = 1
CHUNKING_VERSION = 1

# Token Batching Limits
MIN_SUMMARIZATION_TOKENS = 1200
MAX_SUMMARIZATION_TOKENS = 1800
