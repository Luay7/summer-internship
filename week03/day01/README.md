# Day 01: Learning Markdown for AI Workflows

## Learning Objective

The goal of the first day of Week 3 was to learn the fundamentals of Markdown and understand why clear structure matters when working with artificial intelligence systems.

After exploring headings, lists, tables, and code blocks, the practical task was to transform an unstructured project description into a clean and well-organized Markdown document.

## Why Structure Matters

Clear structure helps both humans and machines understand information more effectively. Headings identify topic boundaries, lists group related items, tables organize comparable information, and code blocks separate technical content from regular prose.

For AI systems, structured content is easier to split, retrieve, summarize, and process consistently.

## Before: Unstructured Project Description

The goal of the project is to develop a local file-summarization system that works without an internet connection to protect document privacy. The initial version accepted one text input from the user and sent it directly to a language model for summarization. Although it was a useful starting point, it could not process long documents or multiple files efficiently.

To improve the project, a multi-stage processing pipeline was designed. The system first receives the files and checks whether they have been processed previously. It then extracts the text and uses Stanza to divide it into individual sentences. Sentence embeddings are generated, and the semantic distances between them are used to create coherent semantic chunks.

The intermediate results are stored together with a hash for each file to prevent unnecessary repeated processing. Neighboring chunks are then packed according to minimum and maximum token limits. The language model summarizes each packed group independently using a Map-Reduce strategy, after which the partial summaries are combined into one coherent final summary.

## After: Structured Project Description

### Project Overview

The project aims to build a local system that summarizes multiple text files using a language model served through Ollama without requiring an internet connection.

Local execution helps protect document privacy and allows the system to process long documents through a multi-stage pipeline.

### Project Architecture

The project is divided into two main phases:

1. Preparing the data, generating semantic chunks, and storing the intermediate results.
2. Packing the chunks according to token limits and summarizing them with a language model.

Each phase is completed for all input files before the next phase begins.

### Currently Supported Files

- Plain-text files with the `.txt` extension
- Multiple files can be processed in the same run

### Development Objectives

- Process multiple files.
- Support long documents.
- Divide extracted text into sentences.
- Generate embeddings that represent sentence meaning.
- Create chunks based on semantic relationships.
- Prevent duplicate processing by storing file hashes.
- Pack chunks according to the model's token limits.
- Improve the accuracy and coherence of the final summary.
- Save the generated summary in a structured file.

### Tools, Models, and Techniques

| Tool | Function | Purpose |
|---|---|---|
| Python | Implements the processing pipeline | Main programming language |
| Stanza | Divides text into sentences | Detects sentence boundaries before embedding |
| Ollama | Runs models locally | Keeps document processing offline |
| mxbai-embed-large | Generates sentence embeddings | Represents sentence meaning as numerical vectors |
| Semantic chunking | Groups related sentences | Produces semantically coherent chunks |
| File hashing | Detects previously processed files | Avoids repeating expensive processing stages |
| Map-Reduce | Summarizes long documents | Produces partial summaries and combines them |

### Processing Pipeline

#### Phase 1: Data Preparation

1. Receive a text file.
2. Calculate the file hash.
3. Check whether the file has already been processed.
4. Extract the text from the file.
5. Divide the text into sentences using Stanza.
6. Generate an embedding for each sentence.
7. Measure the semantic relationships between sentences.
8. Create semantic chunks.
9. Store the chunks, file hash, and related metadata.

#### Phase 2: Summarization

1. Load the stored semantic chunks.
2. Calculate the token count of each chunk.
3. Combine neighboring chunks according to minimum and maximum token limits.
4. Summarize each packed group independently.
5. Collect the partial summaries.
6. Generate one coherent final summary.
7. Save the result as a text file.

### Summarization Strategy

#### Map-Reduce

During the Map stage, the model summarizes each packed group independently.

During the Reduce stage, the partial summaries are sent to the model to produce one final summary that preserves important information and removes repetition.

When the complete source fits into a single model input, the system can generate the final summary without combining multiple partial summaries.