#!/bin/bash

echo "1. Checking and creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
fi

echo "2. Activating virtual environment..."
source .venv/bin/activate

echo "3. Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "4. Downloading Stanza tokenizer model..."
python -c "import stanza; stanza.download('en', processors='tokenize')"

echo "5. Downloading Ollama embedding model..."
ollama pull mxbai-embed-large

echo "6. Downloading Ollama summarization model..."
ollama pull gemma3:4b

echo "========================================"
echo "Setup complete! Everything is ready."
echo "========================================"
