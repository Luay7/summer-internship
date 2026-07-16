# Offline Multi-File Semantic Text Summarizer

## Project Background

This project is an extension of the Local AI Text Summarizer developed on Day 04.

The Day 04 application receives one text input from the user, sends it to a local Ollama model, and saves the generated summary as a TXT or PDF file. It successfully demonstrates local model integration, prompt engineering, output validation, and file export.

## Problems Identified in the Day 04 Version

The original application works well for short and medium-sized text, but it has several limitations when the input becomes larger or when multiple documents need to be processed:

* The user must paste one text directly into the terminal.
* The application processes only one input at a time.
* A long document may exceed the model context window.
* Sending a complete long document in one request may reduce summary quality or omit information.
* Repeating the program processes the same document again even when it has not changed.
* A single summarization request may mix unrelated sections or lose the original document order.

## Proposed Day 05 Solution

The Day 05 version is designed as a multi-stage local summarization pipeline.

The proposed improvements are:

* Read all UTF-8 `.txt` files from an `input_docs` directory.
* Process the files in filename order.
* Divide each document into semantic chunks using paragraph embeddings.
* Use `mxbai-embed-large` locally through Ollama for semantic comparison.
* Calculate a SHA-256 hash for every input file.
* Store the hash and chunking configuration in `processed_hashes.json`.
* Reuse saved semantic chunks when the source file and settings have not changed.
* Estimate chunk sizes and group them according to the available token budget.
* Use a first model stage to summarize consecutive groups of chunks.
* Separate the system prompt from the user prompt for clearer model instructions.
* Use a final model stage to organize the intermediate summaries without summarizing them aggressively again.
* Preserve the original logical and chronological order of each document.

## Planned Development Stages

### Stage 1: Semantic Chunking and Cache

The first stage will read multiple TXT files, create semantic chunks, save the results, and avoid repeating the same chunking work for unchanged files.

### Stage 2: Token-Aware Batch Summarization

The second stage will estimate the size of every chunk, build batches that fit the model context window, and generate one summary for each batch.

### Stage 3: Final Summary Organization

The final stage will merge the sequential batch summaries into one organized final summary for every input document.

## Current Status

The Day 05 project is currently in the planning and documentation stage. The implementation will be added gradually through separate Git commits to make the development process clear.
