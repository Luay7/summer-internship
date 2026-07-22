# Day 04: System Prompts and Project Documentation

## Learning Objective

The goal of the fourth day of Week 3 was to understand how system prompts and project documentation help an artificial intelligence model understand a software project and continue working on it consistently.

After reviewing the principles of clear instructions, role prompting, structured context, and output requirements, the practical task was to create a professional README and a system prompt for the local file-summarization project.

## Why Project Documentation Matters

A software project may contain clear code while still being difficult for another developer or AI model to understand.

Project documentation provides a general explanation of the system, including its purpose, workflow, tools, supported inputs, generated outputs, and current development state.

The README is intended to provide a quick and practical introduction to the project. Detailed technical requirements remain in `spec.md`, while instructions that control the behavior of an AI coding assistant are stored separately in `system-prompt.md`.

## Project Overview

The project aims to build a local system that summarizes multiple plain-text files using models served through Ollama.

The system works without external language-model APIs, which helps protect document privacy and allows long files to be processed through a structured multi-stage pipeline.

## Main Objectives

The project is designed to:

* Process multiple `.txt` files.
* Support long documents.
* Avoid repeating completed data-preparation operations.
* Divide text into semantically related chunks.
* Pack chunks according to token limits.
* Summarize each packed group independently.
* Combine partial summaries into one coherent final summary.
* Save intermediate and final results for each file.

## Project Workflow

The project is divided into two main phases.

### Phase 1: Data Preparation

During the first phase, the system:

1. Validates each input file.
2. Calculates a hash from the file content.
3. Checks for valid saved processing results.
4. Divides the text into sentences using Stanza.
5. Generates sentence embeddings.
6. Detects semantic relationships between neighboring sentences.
7. Creates and saves semantic chunks.

When complete and valid results already exist, the system loads the saved chunks instead of repeating the preprocessing operations.

### Phase 2: Summarization

During the second phase, the system:

1. Loads the saved semantic chunks.
2. Calculates the token count of each chunk.
3. Packs neighboring chunks according to token limits.
4. Summarizes each packed group independently.
5. Collects the partial summaries.
6. Combines them using Map-Reduce.
7. Saves one final summary for each source file.

## Tools and Technologies

| Tool or Technology  | Purpose                                 |
| ------------------- | --------------------------------------- |
| Python              | Implements the project pipeline         |
| Ollama              | Runs models locally                     |
| Stanza              | Divides text into sentences             |
| `mxbai-embed-large` | Generates semantic embeddings           |
| `hashlib`           | Calculates SHA-256 file hashes          |
| JSON                | Stores processing information           |
| Semantic chunking   | Groups related sentences                |
| Map-Reduce          | Produces and combines partial summaries |

## Supported Inputs

The current project supports:

* Plain-text files with the `.txt` extension.
* Multiple files during the same execution.

Each file is processed independently and produces its own saved chunks and final summary.

## Generated Outputs

For every successfully processed file, the system produces:

* A hash representing the original file content.
* A processing-registry record.
* A structured semantic-chunks file.
* Ordered partial summaries.
* One final summary file.
