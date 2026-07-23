# nlp_core.py
import urllib.request
import urllib.error
import json
import math
import stanza
from config import OLLAMA_API_URL

def init_stanza_pipeline(lang):
    """Initializes and returns the Stanza sentence segmentation pipeline."""
    stanza.download(lang, processors='tokenize')
    return stanza.Pipeline(lang=lang, processors='tokenize', use_gpu=False)

def extract_sentences(pipeline, text):
    """Divides the text into sentences using Stanza."""
    doc = pipeline(text)
    return [sentence.text for sentence in doc.sentences]

def generate_embedding(text, model_name):
    """Generates an embedding using a local Ollama model."""
    url = f"{OLLAMA_API_URL}/embeddings"
    payload = json.dumps({"model": model_name, "prompt": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('embedding', [])
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama embedding request failed: {e}")

def normalize_vector(vector):
    """Normalizes an embedding vector."""
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]

def cosine_distance(vec1, vec2):
    """Calculates the semantic distance between two normalized vectors."""
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    return 1.0 - dot_product

def ollama_generate(prompt, model_name):
    """Executes a local Ollama text generation prompt for summarization."""
    url = f"{OLLAMA_API_URL}/generate"
    payload = json.dumps({
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '').strip()
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama generation request failed: {e}")
