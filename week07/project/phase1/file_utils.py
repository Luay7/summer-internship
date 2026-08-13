import hashlib
import json
import os
from config import TEXT_ENCODING, REGISTRY_PATH

def calculate_file_hash(filepath: str) -> str:
    # Read file in 64KB chunks to optimize speed and memory
    chunk_size = 65536
    hasher = hashlib.sha256()

    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(chunk_size), b""):
            hasher.update(byte_block)

    return hasher.hexdigest()

def calculate_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode(TEXT_ENCODING)).hexdigest()

def load_registry() -> dict:
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding=TEXT_ENCODING) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Registry file is corrupted. Starting fresh.")
            return {}
        except Exception as error:
            print(f"Error reading registry: {error}")
            return {}

    return {}

def save_registry(registry_data: dict):
    # Use atomic write to prevent data corruption
    temp_path = f"{REGISTRY_PATH}.tmp"
    
    try:
        with open(temp_path, "w", encoding=TEXT_ENCODING) as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        
        # Replace the old file with the new complete file atomically
        os.replace(temp_path, REGISTRY_PATH)
    except Exception as error:
        print(f"Failed to save registry: {error}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
