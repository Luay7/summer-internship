# Offline Multi-File Semantic Text Summarizer

## Project Background

This project extends the Local AI Text Summarizer developed on Day 04.

The Day 04 version receives one text input, generates a summary with a local Ollama model, and saves the result as a TXT or PDF file. The new version is designed to process multiple and longer documents through a staged pipeline.

## Problems Identified in the Day 04 Version

* The user must paste one text directly into the terminal.
* Only one input is processed at a time.
* Long documents may exceed the model context window.
* Reprocessing the same document repeats unnecessary work.
* A one-request summary may omit information or mix unrelated sections.

## Proposed Solution

The improved pipeline reads TXT files from a directory, divides them into semantic chunks, tracks processed files with SHA-256, summarizes token-aware groups of chunks, and finally organizes the intermediate summaries.

## Development Stages

### Stage 1: Multi-File Semantic Chunking and Cache

The first stage is now implemented.

The program:

* Creates `input_docs` and `chunked_docs` when they do not exist.
* Reads only `.txt` files from `input_docs`.
* Sorts the input files by filename before processing them.
* Validates UTF-8 text and skips empty or unreadable files.
* Splits each document into paragraphs using blank lines.
* Creates paragraph embeddings with `mxbai-embed-large` through Ollama.
* Calculates cosine distance between consecutive paragraph embeddings.
* Uses a distance percentile to identify semantic topic changes.
* Combines related paragraphs into semantic chunks.
* Saves the chunks inside `chunked_docs`.
* Calculates a SHA-256 hash for every source file.
* Stores the file hash and chunking settings in `processed_hashes.json`.
* Reuses saved chunks when the source file and chunking configuration are unchanged.

### Why Semantic Chunking Is Normally Performed Once

For an unchanged document, semantic chunking normally runs only during the first successful processing.

On later runs, the program calculates the same file hash and chunk signature, verifies that the saved chunk file still exists, and loads the existing chunks instead of creating the embeddings again. This is useful because the same text and the same chunking settings are expected to produce the same semantic boundaries.

Semantic chunking runs again only when:

* The source file content changes.
* The embedding model changes.
* The breakpoint percentile changes.
* The chunking version changes.
* The saved chunk file is missing, empty, or invalid.

### Stage 2: Token-Aware Batch Summarization

The next stage will group consecutive chunks according to the available context size and summarize each group with a local language model.

### Stage 3: Final Summary Organization

The final stage will organize the sequential batch summaries into one complete summary for each document.

## Current Workflow

1. Create the required project directories.
2. Discover and sort all `.txt` files inside `input_docs`.
3. Validate each input document.
4. Calculate its SHA-256 hash and chunk signature.
5. Reuse valid saved chunks or perform semantic chunking.
6. Save the semantic chunks inside `chunked_docs`.
7. Update `processed_hashes.json` safely.
8. Print the cache hit and cache miss report.

## Current Project Structure

```text
day05/
├── input_docs/
│   └── document.txt
├── chunked_docs/
│   └── document_chunks.txt
├── main.py
├── processed_hashes.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

* Python 3
* Ollama
* `mxbai-embed-large`

Install the Python packages:

```bash
pip install -r requirements.txt
```

Download the embedding model:

```bash
ollama pull mxbai-embed-large
```

## Running the Current Stage

Place one or more UTF-8 TXT files inside `input_docs`.

Use numbered names when order matters:

```text
01_introduction.txt
02_main_topic.txt
03_conclusion.txt
```

Run the program:

```bash
python main.py
```

Run it again without changing the files to confirm that the output reports a cache hit and reuses the saved semantic chunks.
