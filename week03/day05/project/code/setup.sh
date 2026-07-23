#!/bin/bash

echo "1. Activating virtual environment..."
source .venv/bin/activate

echo "2. Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "3. Downloading Stanza tokenizer model..."
python -c "import stanza; stanza.download('en', processors='tokenize')"

echo "4. Downloading Ollama embedding model..."
ollama pull mxbai-embed-large

echo "5. Downloading Ollama summarization model..."
ollama pull llama3

echo "========================================"
echo "Setup complete! Everything is ready."
echo "========================================"
