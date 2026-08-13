import os


ENV_PREFIX = "LOCAL_SUMMARIZER_"


def get_env_text(name: str, default: str) -> str:
    value = os.environ.get(f"{ENV_PREFIX}{name}")
    return value if value is not None else default


def get_env_int(name: str, default: int) -> int:
    return int(get_env_text(name, str(default)))


def get_env_float(name: str, default: float) -> float:
    return float(get_env_text(name, str(default)))


def get_env_bool(name: str, default: bool) -> bool:
    value = get_env_text(name, str(default)).strip().lower()

    if value in {"1", "true", "yes", "on"}:
        return True

    if value in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"Invalid boolean value for {name}: {value}")


# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = get_env_text("INPUT_DIR", os.path.join(BASE_DIR, "inputs"))
OUTPUT_DIR = get_env_text("OUTPUT_DIR", os.path.join(BASE_DIR, "outputs"))
CHUNKS_DIR = get_env_text("CHUNKS_DIR", os.path.join(OUTPUT_DIR, "chunks"))
SUMMARIES_DIR = get_env_text(
    "SUMMARIES_DIR",
    os.path.join(OUTPUT_DIR, "summaries"),
)
AGENT_DECISIONS_DIR = get_env_text(
    "AGENT_DECISIONS_DIR",
    os.path.join(OUTPUT_DIR, "agent_decisions"),
)
REGISTRY_PATH = get_env_text(
    "REGISTRY_PATH",
    os.path.join(BASE_DIR, "processing_registry.json"),
)

# Input files
INPUT_FILE_EXTENSION = get_env_text("INPUT_FILE_EXTENSION", ".txt")
TEXT_ENCODING = get_env_text("TEXT_ENCODING", "utf-8")

# Phase 1: sentence segmentation and semantic chunking
STANZA_LANGUAGE = get_env_text("STANZA_LANGUAGE", "en")
STANZA_USE_GPU = get_env_bool("STANZA_USE_GPU", False)
EMBEDDING_MODEL = get_env_text("EMBEDDING_MODEL", "mxbai-embed-large")
BREAKPOINT_PERCENTILE = get_env_float("BREAKPOINT_PERCENTILE", 80.0)
BUFFER_SIZE = get_env_int("BUFFER_SIZE", 2)
CHUNKING_VERSION = get_env_int("CHUNKING_VERSION", 1)

# Local Ollama models
SUMMARIZATION_MODEL = get_env_text("SUMMARIZATION_MODEL", "gemma3:4b")
OLLAMA_KEEP_ALIVE = get_env_text("OLLAMA_KEEP_ALIVE", "5m")

# Phase 1 routing agent
ROUTING_AGENT_MODEL = get_env_text("ROUTING_AGENT_MODEL", "gemma3:4b")
ROUTING_AGENT_VERSION = get_env_int("ROUTING_AGENT_VERSION", 6)
ROUTING_AGENT_SAMPLE_CHARS = get_env_int("ROUTING_AGENT_SAMPLE_CHARS", 9000)
ROUTING_AGENT_MAX_STEPS = get_env_int("ROUTING_AGENT_MAX_STEPS", 6)
ROUTING_AGENT_CONTEXT = get_env_int("ROUTING_AGENT_CONTEXT", 8192)
ROUTING_AGENT_NUM_PREDICT = get_env_int("ROUTING_AGENT_NUM_PREDICT", 180)
ROUTING_AGENT_TEMPERATURE = get_env_float(
    "ROUTING_AGENT_TEMPERATURE",
    0.0,
)

# Phase 2: batching and Map-Reduce summarization
MAX_TOKENS_PER_BATCH = get_env_int("MAX_TOKENS_PER_BATCH", 2200)
MAX_REDUCE_ROUNDS = get_env_int("MAX_REDUCE_ROUNDS", 20)
