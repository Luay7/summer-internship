# Day 02: Context Engineering for AI Workflows

## Learning Objective

The goal of the second day of Week 3 was to understand the fundamentals of context engineering and learn how to provide an artificial intelligence system with the information required to complete a software task accurately.

After reviewing the difference between a prompt and the wider context available to a model, the practical task was to create a structured context document for one feature of the local file-summarization project.

## Why Context Matters

A clear prompt explains what the model should do, while a complete context document explains the project background, current system state, relevant tools, technical decisions, constraints, and expected behavior.

Providing only the task description may force the model to guess missing details. A well-structured context document reduces ambiguity and helps the model make decisions that remain consistent with the existing project.

## Selected Software Task

The selected task is to add a file-hashing system to the data-preparation phase of the project.

The hashing system should determine whether the content of a file has already been processed. When valid saved results are available, the project should reuse them instead of repeating the expensive preprocessing operations.

## Project Overview

The project aims to build a local system that summarizes multiple text files without requiring an internet connection.

Local execution helps protect document privacy and allows the system to process long files through a multi-stage pipeline.

## Current Project Architecture

The project is divided into two main phases:

1. Preparing the files, generating semantic chunks, and storing the intermediate results.
2. Loading the stored chunks, packing them according to token limits, and producing the final summary.

Each phase is completed for all input files before the next phase begins.

### Phase 1: Data Preparation

1. Receive a text file.
2. Extract the text from the file.
3. Divide the text into sentences using Stanza.
4. Generate an embedding for each sentence.
5. Calculate the semantic distances between sentences.
6. Create semantic chunks.
7. Save the results for each file.

### Phase 2: Summarization

1. Load the saved semantic chunks.
2. Calculate the token count of each chunk.
3. Combine neighboring chunks according to minimum and maximum token limits.
4. Summarize each packed group independently.
5. Collect the partial summaries.
6. Generate one coherent final summary.
7. Save the result as a text file.

## Purpose of File Hashing

The filename alone is not enough to determine whether a file has already been processed.

A file may keep the same name while its content changes. In that case, the project must process it again.

Two files may also have different names while containing identical content. In that case, the project may reuse the same preprocessing results when the system can identify the matching content hash.

For this reason, the hash should be generated from the file content rather than only from the filename.

## Position in the Processing Pipeline

```text
Receive a Text File
        ↓
Calculate the File Content Hash
        ↓
Search for the Hash in the Processing Registry
        ↓
Does the Hash Exist?
        ├── Yes: Load the Saved Semantic Chunks
        │
        └── No: Extract the Text
                    ↓
              Divide the Text Using Stanza
                    ↓
              Generate Embeddings
                    ↓
              Create Semantic Chunks
                    ↓
              Save the Results and Hash
```

## Required Project Context

For the AI model to complete the task correctly, it needs to know that:

- The project is written in Python.
- The project runs locally without an internet connection.
- The project currently supports `.txt` files.
- Multiple files can be processed during the same run.
- Each file has its own saved semantic-chunk results.
- The hash must be calculated before running Stanza and the embedding model.
- The hash must be based on the file content.
- Saved results should be reused when the stored data is still valid.
- The first phase must run again when the file content changes.
- The project is organized using modules and functions without classes.
- The current task only affects the first phase.
- The summarization method does not need to change.

## Tools and Technologies

| Tool or Technology | Function | Purpose |
|---|---|---|
| Python | Implements the project pipeline | Calculates hashes and verifies processed files |
| `hashlib` | Generates a hash from file content | Identifies whether the content was processed previously |
| JSON | Stores file-processing data | Stores hashes and paths to saved results |
| Stanza | Divides text into sentences | Runs only when valid saved results are unavailable |
| `mxbai-embed-large` | Generates sentence embeddings | Performs one of the expensive operations that should not be repeated |
| Semantic chunking | Groups related sentences | Produces results that can be loaded and reused |

## Saved Processing Data

The processing data for each file is stored in a JSON registry using the filename as the main key.

The stored data follows this structure:

```json
{
  "file_name.txt": {
    "input_sha256": "file_content_hash",
    "chunk_signature": "chunking_process_signature",
    "embedding_model": "embedding_model_name",
    "breakpoint_percentile": 70.0,
    "chunking_version": 1,
    "chunks_file": "path/to/chunks_file.txt"
  }
}
```

The stored fields include:

| Field | Function |
|---|---|
| `input_sha256` | Stores the hash of the original file content and helps determine whether the content has changed |
| `chunk_signature` | Stores a signature for the semantic-chunking process and helps verify compatibility with the current settings |
| `embedding_model` | Stores the name of the embedding model used to process the sentences |
| `breakpoint_percentile` | Stores the percentile used to determine semantic breakpoints |
| `chunking_version` | Stores the version of the semantic-chunking method |
| `chunks_file` | Stores the path to the file containing the saved semantic chunks |

This information documents the file content, the semantic-chunking settings, and the location of the saved results. It can later be used to verify whether those results are still valid before they are reused.

## Expected Workflow

1. Receive the file path.
2. Read the file content in binary mode.
3. Generate a SHA-256 hash from the content.
4. Search for the hash in the processing registry.
5. If the hash exists, verify that the saved results file still exists.
6. If the saved results are available, load them.
7. If the hash does not exist, run the data-preparation phase.
8. Save the hash and the path to the generated results.
9. Continue to the summarization phase.

## Constraints

- The system must not rely only on the filename to determine whether a file has already been processed.
- The expensive operations in the first phase must not run before the hash is calculated and the saved results are checked.
- A file must not be considered fully processed when its hash exists but its semantic-chunk results file is missing.

## Task Scope

The current task focuses on validating and reusing the results of the data-preparation phase.

It does not include changing the semantic-chunking method or the summarization phase.

