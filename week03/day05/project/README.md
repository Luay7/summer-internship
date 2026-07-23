# Day 04: System Prompts and Project Documentation

## Project Overview

The project aims to build a local system that summarizes multiple plain-text files using models served through Ollama.

The system works without external language-model APIs, which helps protect document privacy and allows long files to be processed through a structured multi-stage pipeline.

The project uses `mxbai-embed-large` for semantic embeddings and `llama3` for summarization. Both models run locally through Ollama.

## Main Objectives

The project is designed to:

* Process multiple UTF-8 `.txt` files.
* Support long documents.
* Avoid repeating completed data-preparation operations.
* Divide text into semantically related chunks.
* Preserve the original sentence order.
* Pack chunks according to token limits.
* Summarize each packed group independently.
* Combine partial summaries into one coherent final summary.
* Save intermediate and final results for each file.
* Keep the contents and outputs of different source files separate.

## Project Structure

The implementation contains four Python source files:

```text
code/
├── config.py
├── phase1.py
├── phase2.py
├── main.py
└── requirements.txt
```

The files have the following responsibilities:

| File               | Responsibility                                                     |
| ------------------ | ------------------------------------------------------------------ |
| `config.py`        | Stores the general project settings                                |
| `phase1.py`        | Contains the complete data-preparation and semantic-chunking phase |
| `phase2.py`        | Contains the complete token-batching and summarization phase       |
| `main.py`          | Runs and coordinates the complete project                          |
| `requirements.txt` | Lists the required Python packages                                 |

The implementation uses functions and modules without classes.

## Project Workflow

The project is divided into two main phases.

### Phase 1: Data Preparation

During the first phase, the system:

1. Validates each input file.
2. Confirms that the file is a UTF-8 `.txt` file.
3. Calculates a SHA-256 hash from the file content.
4. Checks for valid saved processing results.
5. Prepares the source text in paragraph form.
6. Divides the text into sentences using Stanza.
7. Creates a buffer-1 context window for each sentence.
8. Generates sentence-context embeddings.
9. Applies L2 normalization to the embeddings.
10. Calculates semantic distances between neighboring sentence representations.
11. Detects semantic breakpoints using the configured percentile.
12. Creates and saves semantic chunks.
13. Updates the processing registry.

When complete and valid results already exist, the system loads the saved chunks instead of repeating the preprocessing operations.

Phase 1 must be completed or validated for all input files before Phase 2 begins.

### Phase 2: Summarization

During the second phase, the system:

1. Loads the saved semantic chunks.
2. Estimates the token count of each chunk.
3. Packs neighboring chunks according to token limits.
4. Handles oversized chunks using sentence boundaries.
5. Summarizes each packed group independently using `llama3`.
6. Collects and saves the ordered partial summaries.
7. Combines them using Map-Reduce.
8. Saves one final summary for each source file.

Files are processed sequentially within each phase.

## Tools and Technologies

| Tool or Technology      | Purpose                                                       |
| ----------------------- | ------------------------------------------------------------- |
| Python                  | Implements the project pipeline                               |
| Ollama                  | Runs models locally                                           |
| `ollama` Python package | Communicates with the locally running Ollama service          |
| Stanza                  | Divides text into sentences                                   |
| GPU acceleration        | Supports Stanza processing without forcing CPU-only execution |
| `mxbai-embed-large`     | Generates semantic embeddings                                 |
| `llama3`                | Produces partial and final summaries                          |
| NumPy                   | Normalizes embeddings and calculates semantic distances       |
| `hashlib`               | Calculates SHA-256 file hashes                                |
| JSON                    | Stores processing information and semantic chunks             |
| Semantic chunking       | Groups related sentences                                      |
| Map-Reduce              | Produces and combines partial summaries                       |

## Local Execution

The project runs locally on the user's device.

The implementation:

* Uses the `ollama` Python package directly.
* Uses locally installed Ollama models.
* Does not use external language-model APIs.
* Does not manually construct Ollama HTTP requests.
* Does not download Stanza resources during normal execution.
* Keeps GPU usage enabled for Stanza.
* Allows Ollama to use its normal local hardware acceleration.

The required Stanza resources and Ollama models must be installed locally before running the project.

## Supported Inputs

The current project supports:

* Plain-text files with the `.txt` extension.
* UTF-8 encoded text files only.
* Multiple files during the same execution.

A file that cannot be decoded as UTF-8 must be rejected and must not continue to the processing phases.

Each valid file is processed independently and produces its own saved chunks, partial summaries, and final summary.

## Generated Outputs

For every successfully processed file, the system produces:

* A SHA-256 hash representing the original file content.
* A processing-registry record.
* A structured semantic-chunks JSON file.
* A SHA-256 hash for the semantic-chunks file.
* Ordered partial summaries.
* One final summary file.

Suggested output paths:

```text
processing_registry.json
outputs/chunks/file_name_chunks.json
outputs/summaries/file_name_partial_summaries.txt
outputs/summaries/file_name_summary.txt
```

All JSON and text outputs are saved using UTF-8 encoding.
