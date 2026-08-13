import re
import stanza
from config import STANZA_LANGUAGE, STANZA_USE_GPU

# Global variable to hold the pipeline instance
_STANZA_PIPELINE = None

def get_stanza_pipeline():
    global _STANZA_PIPELINE

    if _STANZA_PIPELINE is None:
        try:
            # Loading only the "tokenize" processor to save memory and time
            _STANZA_PIPELINE = stanza.Pipeline(
                lang=STANZA_LANGUAGE,
                processors="tokenize",
                use_gpu=STANZA_USE_GPU,
                verbose=False,
                download_method=None,
            )
        except Exception as error:
            raise RuntimeError(
                "Could not load the local Stanza tokenizer. "
                "Make sure the required Stanza model is installed."
            ) from error

    return _STANZA_PIPELINE

def unload_stanza_pipeline():
    """Frees up RAM/VRAM by deleting the pipeline instance."""
    global _STANZA_PIPELINE
    if _STANZA_PIPELINE is not None:
        del _STANZA_PIPELINE
        _STANZA_PIPELINE = None
        print("Stanza pipeline unloaded from memory.")

def prepare_paragraph_text(text: str) -> str:
    # Standardize line endings without changing text structure.
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()

def extract_sentences(text: str) -> list:
    if not text.strip():
        return []

    pipeline = get_stanza_pipeline()
    doc = pipeline(text)
    sentences = []

    for sentence in doc.sentences:
        # Clean extra spaces within the extracted sentence
        clean_sentence = re.sub(r"[ \t]+", " ", sentence.text).strip()
        
        if clean_sentence:
            sentences.append(clean_sentence)

    return sentences
