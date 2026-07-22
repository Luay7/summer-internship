# Day 03: Writing Clear Specifications for AI Workflows

## Learning Objective

The goal of the third day of Week 3 was to learn how to transform a general software idea into a clear and complete specification that an AI model or developer can follow without guessing important requirements.

The practical task was to write a structured specification for the complete local file-summarization project using clear objectives, inputs, outputs, constraints, expected behavior, and acceptance criteria.

## Why Clear Specifications Matter

A project description explains the general idea of a system, while a specification defines exactly what the system must do.

Clear specifications reduce ambiguity by describing the required behavior, the order of the main processing stages, the expected inputs and outputs, and the conditions that determine whether the implementation is correct.

The specification does not need to describe every line of code. It should provide enough information to guide implementation while leaving minor programming decisions to the developer or AI model.

## Project Overview

The project aims to build a local system that summarizes multiple text files using models served through Ollama without requiring an internet connection.

Local execution protects document privacy and allows the system to process long files through a multi-stage pipeline.

The project is divided into two main phases:

1. Preparing the files, generating semantic chunks, and storing the intermediate results.
2. Loading the stored chunks, packing them according to token limits, and producing the final summary using Map-Reduce.

The first phase must be completed for all valid input files before the second phase begins.

## Project Objective

The system must:

* Process multiple `.txt` files during the same run.
* Avoid repeating completed data-preparation operations.
* Divide long text into semantically related chunks.
* Store and reuse valid intermediate results.
* Group neighboring chunks according to token limits.
* Summarize each packed group independently.
* Combine the partial summaries into one coherent final summary for each file.
* Save the intermediate and final results in structured files.

## Supported Files

The current version must support:

* Plain-text files with the `.txt` extension.
* Multiple files during the same execution.
* Common text encodings when they can be read safely.

Each file must be validated and processed independently.

## Inputs

The system receives:

* One or more `.txt` file paths.
* The processing-registry path.
* The directory used to store semantic chunks.
* The directory used to store final summaries.
* The Stanza language.
* The embedding model name.
* The summarization model name.
* The sentence context-window size.
* The semantic-breakpoint percentile.
* The minimum and maximum token limits used for summarization batches.

## Phase 1: Data Preparation

For each input file, the system must:

1. Confirm that the file exists.
2. Confirm that the file uses the `.txt` extension.
3. Reject empty or unreadable files.
4. Calculate a SHA-256 hash from the binary file content.
5. Search the processing registry for previously saved results.
6. Validate the saved results when a matching record exists.
7. Load the stored semantic chunks when the previous results are complete and valid.
8. Run the complete data-preparation phase when valid saved results are unavailable.

The data-preparation phase includes:

1. Reading and cleaning the text.
2. Dividing the text into sentences using Stanza.
3. Creating a context window for each sentence.
4. Generating embeddings using `mxbai-embed-large`.
5. Normalizing the embeddings.
6. Calculating semantic distances between neighboring sentence representations.
7. Detecting semantic breakpoints using a configurable percentile.
8. Creating semantic chunks.
9. Saving the chunks and their related metadata.

## File Hashing

The system must use SHA-256 through Python’s `hashlib` module.

The original file hash must:

* Be calculated from the binary file content.
* Not depend on the filename or file path.
* Be calculated before the first processing phase begins.
* Be stored as `input_sha256`.

The generated semantic-chunks file must also receive its own SHA-256 hash, stored as `chunks_sha256`.

The input hash identifies the original source content, while the chunks hash verifies the integrity of the generated semantic-chunks file.

## Processing Registry

The system must store processing information in a JSON registry.

The stored data follows this structure:

```json
{
  "file_name.txt": {
    "input_sha256": "original_file_hash",
    "processing_status": "completed",
    "embedding_model": "mxbai-embed-large",
    "breakpoint_percentile": 80.0,
    "buffer_size": 1,
    "chunking_version": 1,
    "chunks_file": "outputs/chunks/file_name_chunks.json",
    "chunks_sha256": "chunks_file_hash"
  }
}
```

The stored fields include:

| Field                   | Function                                                           |
| ----------------------- | ------------------------------------------------------------------ |
| `input_sha256`          | Identifies the content of the original file                        |
| `processing_status`     | Indicates whether the first phase is pending, completed, or failed |
| `embedding_model`       | Stores the embedding model used during processing                  |
| `breakpoint_percentile` | Stores the percentile used to detect semantic breakpoints          |
| `buffer_size`           | Stores the sentence context-window size                            |
| `chunking_version`      | Stores the version of the semantic-chunking process                |
| `chunks_file`           | Stores the path to the generated semantic-chunks file              |
| `chunks_sha256`         | Verifies the integrity of the generated chunks file                |

The system must:

* Create an empty registry when the JSON file does not exist.
* Treat incomplete processing records as invalid.
* Update each file record independently.
* Mark a file as completed only after the first phase finishes successfully.
* Reprocess the file when its content or processing settings change.
* Search by content hash when differently named files contain identical content.

## File-Processing Scenarios

### Scenario 1: New File

A file is considered new when no matching content hash exists in the processing registry.

The system must:

1. Calculate the original file hash.
2. Run the complete data-preparation phase.
3. Generate and save the semantic chunks.
4. Calculate the chunks-file hash.
5. Save all required processing information.
6. Set the processing status to `completed`.
7. Continue to the summarization phase.

### Scenario 2: Existing File with Incomplete Phase 1 Results

A file may exist in the processing registry while its first-phase results do not satisfy all validation requirements.

The system must:

1. Calculate the current file hash and confirm whether the source content has changed.
2. Treat the previous results as invalid.
3. Prevent the file from continuing to the summarization phase.
4. Run the complete data-preparation phase again.
5. Generate and save a new semantic-chunks file.
6. Calculate the chunks-file hash.
7. Update the JSON registry with complete processing information.
8. Set the processing status to `completed` only after all first-phase operations succeed.
9. Continue to the second phase after the new results have been validated.

### Scenario 3: Existing File with Complete Results

A file is considered complete when:

* Its current content hash matches `input_sha256`.
* Its processing status is `completed`.
* Its saved processing settings match the current settings.
* Its semantic-chunks file exists and can be read.
* Its current chunks-file hash matches `chunks_sha256`.
* All required registry fields are available.

The system must:

1. Skip Stanza processing.
2. Skip embedding generation.
3. Skip semantic-distance calculation.
4. Skip semantic-chunk generation.
5. Load the saved semantic chunks.
6. Continue directly to the second phase.

## Semantic Chunking

The semantic-chunking process must preserve the original sentence order.

The system must:

1. Create a local context window for each sentence.
2. Generate an embedding for every context window.
3. Normalize the generated embeddings.
4. Calculate semantic distances between neighboring representations.
5. Calculate a breakpoint threshold using the configured percentile.
6. Create breakpoints where meaningful topic changes are detected.
7. Group the sentences between the breakpoints into semantic chunks.

Each semantic chunk must contain:

* A sequential chunk number.
* The first sentence position.
* The final sentence position.
* The sentence count.
* The character count.
* The token count.
* The complete chunk text.

Every source sentence must appear exactly once. The system must not remove, duplicate, or reorder source sentences.

## Saved Semantic Chunks

The semantic chunks for each file must be stored in a structured file.

The saved information must include:

* The source filename.
* The original file hash.
* The processing settings.
* The total sentence count.
* The total chunk count.
* The metadata and text of every semantic chunk.

The file must be saved successfully before the processing status is changed to `completed`.

## Phase 2: Token-Based Batching

After Phase 1 has been completed for all valid files, the system must load the semantic chunks for each file.

Neighboring semantic chunks must be combined according to configurable token limits.

The initial limits are:

```text
MIN_SUMMARIZATION_TOKENS = 1200
MAX_SUMMARIZATION_TOKENS = 1800
```

The batching process must:

* Preserve the original chunk order.
* Prefer batches that remain between the minimum and maximum token limits.
* Avoid creating unnecessarily small batches.
* Avoid losing or duplicating source sentences.
* Keep the contents of different files separate.
* Handle oversized chunks safely using sentence boundaries.
* Preserve semantic relationships as much as possible.

A small number of neighboring sentences may be included as boundary context to clarify transitions between batches. Boundary context must not be treated as independent source content.

## Map-Reduce Summarization

### Map Stage

During the Map stage, the system must summarize every packed batch independently.

The model must:

* Use only the supplied source text.
* Preserve important events and facts.
* Preserve chronological order when relevant.
* Avoid adding unsupported information.
* Remove repetition and minor details.
* Return only the partial summary.

The partial summaries must be stored in the same order as the original batches.

### Reduce Stage

During the Reduce stage, the partial summaries must be combined into one coherent final summary.

The system must:

* Preserve the original order.
* Retain important information from all partial summaries.
* Remove repeated information.
* Avoid adding new facts.
* Produce one final summary for the current source file.

When all partial summaries fit into one model request, they may be reduced directly.

When the partial summaries exceed the safe input limit, the system must combine them through multiple ordered Reduce steps until only one final summary remains.

## Outputs

For every successfully processed file, the system must produce:

* A SHA-256 hash for the original file.
* A complete processing-registry record.
* A structured semantic-chunks file.
* A SHA-256 hash for the chunks file.
* Ordered partial summaries.
* One final summary file.

Suggested output paths:

```text
outputs/chunks/file_name_chunks.json
outputs/summaries/file_name_summary.txt
```

## Error Handling

The system must handle:

* Missing input files.
* Unsupported file types.
* Empty files.
* Text-decoding failures.
* Missing or invalid processing registries.
* Incomplete processing records.
* Missing or corrupted semantic-chunks files.
* Stanza failures.
* Embedding-generation failures.
* Token-counting or batching failures.
* Ollama request failures.
* Output-saving failures.

An error must never cause a file to be marked as completed incorrectly.

A failure in one file must not corrupt the saved results of other files.

## Constraints

* The project must use Python.
* The implementation must use functions and modules without classes.
* File hashing must use `hashlib`.
* Sentence segmentation must use Stanza.
* Embeddings must be generated using `mxbai-embed-large`.
* Models must run locally through Ollama.
* The current version must support `.txt` files only.
* Files must be processed sequentially.
* External APIs must not be used during document processing.
* The contents of different files must not be mixed.
* Expensive operations must not run before validating saved results.
* Data preparation and summarization must remain separate phases.
* A file must not be considered complete before all Phase 1 results have been saved successfully.

## Acceptance Criteria

The project is considered complete when:

* Multiple `.txt` files can be processed during one run.
* Every input file is validated independently.
* New files are processed from the beginning and all results are saved.
* Files with incomplete results are processed again.
* Files with complete and valid results skip the first phase.
* Valid saved chunks prevent unnecessary repeated processing.
* Changed files or processing settings trigger new data preparation.
* Stanza divides the text into ordered sentences.
* Semantic chunks preserve every original source sentence.
* Semantic chunks are packed safely according to token limits.
* Oversized chunks are handled using sentence boundaries.
* Every packed batch produces one partial summary.
* Map-Reduce produces one coherent final summary for each file.
* All required outputs are saved successfully.
* Errors are reported clearly.
* Classes are not used.
* The project runs locally through Ollama.
