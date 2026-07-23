# utils.py
import hashlib
import json
import os
from pathlib import Path

def calculate_file_hash(filepath):
    """Calculates the SHA-256 hash of a file's binary content."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_text_hash(text):
    """Calculates the SHA-256 hash of a given text string."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_registry(registry_path):
    """Loads the JSON processing registry or creates an empty one."""
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_registry(registry_path, registry_data):
    """Saves the processing registry to a JSON file."""
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=2)

def ensure_directory(directory_path):
    """Ensures that the specified directory exists."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def approximate_tokens(text):
    """Provides a basic token approximation (standard 1 token ~ 4 chars / 0.75 words)."""
    return len(text.split()) + (len(text) // 4) // 2