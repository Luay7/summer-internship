# config.py

# File Paths
REGISTRY_FILE = "processing_registry.json"
CHUNKS_DIR = "outputs/chunks"
SUMMARIES_DIR = "outputs/summaries"

# Model Configurations
EMBEDDING_MODEL = "mxbai-embed-large"
SUMMARIZATION_MODEL = "llama3" # Configurable local Ollama model

# NLP Processing Configurations
STANZA_LANG = "en"
BREAKPOINT_PERCENTILE = 80.0
BUFFER_SIZE = 1
CHUNKING_VERSION = 1

# Token Batching Limits
MIN_SUMMARIZATION_TOKENS = 1200
MAX_SUMMARIZATION_TOKENS = 1800

# Ollama API Configuration
OLLAMA_API_URL = "http://localhost:11434/api"