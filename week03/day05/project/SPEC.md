# Day 03: Writing Clear Specifications for AI Workflows

## Project Overview

The project aims to build a local system that summarizes multiple text files using models served through Ollama without requiring an internet connection.

Local execution protects document privacy and allows the system to process long files through a multi-stage pipeline.

The project is divided into two main phases:

1. Preparing the files, generating semantic chunks, and storing the intermediate results.
2. Loading the stored chunks, packing them according to token limits, and producing the final summary using Map-Reduce.

The first phase must be completed or validated for all valid input files before the second phase begins.

## Project Objective

The system must:

* Process multiple UTF-8 `.txt` files during the same run.
* Avoid repeating completed data-preparation operations.
* Divide long text into semantically related chunks.
* Preserve every original sentence in its correct order.
* Store and reuse valid intermediate results.
* Group neighboring chunks according to token limits.
* Summarize each packed group independently using `llama3`.
* Combine the partial summaries into one coherent final summary for each file.
* Save the intermediate and final results in structured files.
* Run locally without external language-model APIs.

## Required Project Structure

The implementation must contain exactly four Python source files:

```text
config.py
phase1.py
phase2.py
main.py
```

A `requirements.txt` file may also be included.

The system must not create additional Python modules unless the project requirements are explicitly changed.

### `config.py`

The configuration file must contain the shared project settings, including:

* Input directory.
* Processing-registry path.
* Semantic-chunks output directory.
* Summaries output directory.
* UTF-8 text encoding.
* Stanza language.
* Stanza GPU setting.
* Embedding model name.
* Summarization model name.
* Sentence context-window size.
* Semantic-breakpoint percentile.
* Chunking version.
* Minimum and maximum summarization-token limits.
* Ollama keep-alive setting when required.

The required model settings are:

```text
EMBEDDING_MODEL = "mxbai-embed-large"
SUMMARIZATION_MODEL = "llama3"
```

The Stanza GPU setting must remain enabled:

```text
STANZA_USE_GPU = True
```

### `phase1.py`

This file must contain all file validation, hashing, registry validation, paragraph preparation, sentence segmentation, embedding, semantic-distance, breakpoint, chunk-building, and Phase 1 output operations.

### `phase2.py`

This file must contain all token estimation, oversized-chunk handling, batching, Map summarization, Reduce summarization, and Phase 2 output operations.

### `main.py`

This file must discover the input files, initialize shared resources, run Phase 1 for all files, collect the successfully prepared files, and then run Phase 2.

## Supported Files

The current version must support:

* Plain-text files with the `.txt` extension.
* UTF-8 encoded text only.
* Multiple files during the same execution.

Each file must be validated and processed independently.

A file that cannot be decoded as UTF-8 must:

1. Be rejected.
2. Produce a clear error.
3. Not be marked as completed.
4. Not continue to Phase 2.

All generated JSON and text files must also use UTF-8 encoding.

## Inputs

The system receives:

* One or more UTF-8 `.txt` files from the configured input directory.
* The processing-registry path.
* The directory used to store semantic chunks.
* The directory used to store partial and final summaries.
* The Stanza language.
* The embedding model name.
* The summarization model name.
* The sentence context-window size.
* The semantic-breakpoint percentile.
* The minimum and maximum token limits used for summarization batches.

## Local Model Integration

The system must use the `ollama` Python package directly.

Embedding generation must use:

```python
ollama.embed(
    model=EMBEDDING_MODEL,
    input=context_windows,
    truncate=False,
    keep_alive=OLLAMA_KEEP_ALIVE,
)
```

Summarization must use an appropriate text-generation function from the local `ollama` Python package.

The implementation must not:

* Construct manual Ollama HTTP requests using `urllib` or similar libraries.
* Store an Ollama API URL in the configuration.
* Use an external language-model API.
* Send document content to an internet service.
* Download Ollama models during normal execution.
* Download Stanza resources during normal execution.

The required models and Stanza resources must already be installed locally.

## GPU Usage

Stanza must be initialized with GPU usage enabled:

```python
stanza.Pipeline(
    lang=STANZA_LANGUAGE,
    processors="tokenize",
    use_gpu=STANZA_USE_GPU,
    verbose=False,
)
```

`STANZA_USE_GPU` must be set to `True`.

The implementation must not force CPU-only processing or disable Ollama's normal local hardware acceleration.

## Phase 1: Data Preparation

For each input file, the system must:

1. Confirm that the file exists.
2. Confirm that the file uses the `.txt` extension.
3. Confirm that the file is not empty.
4. Read the file using UTF-8.
5. Calculate a SHA-256 hash from the binary file content.
6. Search the processing registry for previously saved results.
7. Validate the saved results when a matching record exists.
8. Load the stored semantic chunks when the previous results are complete and valid.
9. Run the complete data-preparation phase when valid saved results are unavailable.

The data-preparation phase includes:

1. Preparing the source text in paragraph form.
2. Dividing the prepared text into sentences using Stanza.
3. Normalizing whitespace in every returned sentence.
4. Creating a buffer-1 context window for each sentence.
5. Generating embeddings using `mxbai-embed-large`.
6. Validating the embedding response.
7. Applying L2 normalization to the embeddings.
8. Calculating semantic distances between neighboring sentence representations.
9. Detecting semantic breakpoints using the configured percentile.
10. Creating semantic chunks from the original normalized sentences.
11. Saving the chunks and their related metadata.
12. Calculating the semantic-chunks file hash.
13. Updating the processing registry.

## Paragraph Text Preparation

Before Stanza sentence segmentation, the system must prepare the paragraph input variant.

The preparation method must:

1. Normalize `\r\n` and `\r` to `\n`.
2. Remove surrounding whitespace.
3. Detect paragraphs using one or more blank lines.
4. Replace line breaks inside each paragraph with a single space.
5. Normalize repeated spaces and tabs.
6. Remove empty paragraphs.
7. Preserve separate paragraphs using two newline characters.

The required behavior is:

```python
def prepare_paragraph_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not text:
        return ""

    raw_paragraphs = re.split(r"\n[ \t]*\n+", text)
    paragraphs = []

    for paragraph in raw_paragraphs:
        paragraph = re.sub(r"[ \t]*\n[ \t]*", " ", paragraph)
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()

        if paragraph:
            paragraphs.append(paragraph)

    return "\n\n".join(paragraphs)
```

## Stanza Sentence Segmentation

The Stanza pipeline must:

* Use the configured language.
* Use only the `tokenize` processor.
* Keep GPU usage enabled.
* Disable unnecessary verbose output.
* Not call `stanza.download()` during normal execution.

The system must normalize repeated whitespace in each returned sentence and remove empty sentence results.

## Context-Window Construction

The current version must use:

```text
BUFFER_SIZE = 1
```

One context window must be created for every sentence.

For each sentence, the window must contain:

```text
previous sentence + current sentence + next sentence
```

The first and final windows must use only the neighboring sentences that are available.

## Embedding Generation and Normalization

All context windows must be embedded in one local call when possible.

The system must validate that:

* The Ollama response contains embeddings.
* The embeddings form a two-dimensional numeric array.
* The embedding count matches the number of context windows.
* No embedding has a zero norm.

The embeddings must be converted to a NumPy `float32` array.

L2 normalization must be applied to every embedding row.

## Semantic-Distance Calculation

Because the embeddings are normalized, adjacent cosine similarities must be calculated using the dot product:

```python
similarities = np.sum(
    embeddings[:-1] * embeddings[1:],
    axis=1,
)
```

Similarity values must be clipped between `-1.0` and `1.0`.

Cosine distance must be calculated as:

```text
distance = 1.0 - similarity
```

Only neighboring context-window representations may be compared.

## Semantic Breakpoints

The breakpoint threshold must be calculated using:

```python
np.percentile(distances, BREAKPOINT_PERCENTILE)
```

A breakpoint at index `i` means that the system cuts after sentence `i`.

A breakpoint must be created only when:

```text
distance > threshold
```

A distance equal to the threshold must not create a breakpoint.

## File Hashing

The system must use SHA-256 through Python's `hashlib` module.

The original file hash must:

* Be calculated from the binary file content.
* Not depend on the filename or file path.
* Be calculated before Stanza and embedding processing begins.
* Be stored as `input_sha256`.

The generated semantic-chunks file must also receive its own binary SHA-256 hash, stored as `chunks_sha256`.

The input hash identifies the original source content, while the chunks hash verifies the integrity of the generated semantic-chunks file.

## Processing Registry

The system must store processing information in a UTF-8 JSON registry.

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

| Field                   | Function                                                   |
| ----------------------- | ---------------------------------------------------------- |
| `input_sha256`          | Identifies the content of the original file                |
| `processing_status`     | Indicates whether Phase 1 is pending, completed, or failed |
| `embedding_model`       | Stores the embedding model used during processing          |
| `breakpoint_percentile` | Stores the percentile used to detect semantic breakpoints  |
| `buffer_size`           | Stores the sentence context-window size                    |
| `chunking_version`      | Stores the version of the semantic-chunking process        |
| `chunks_file`           | Stores the path to the generated semantic-chunks file      |
| `chunks_sha256`         | Verifies the integrity of the generated chunks file        |

The possible processing statuses are:

```text
pending
completed
failed
```

The system must:

* Create an empty registry when the JSON file does not exist.
* Treat invalid JSON or incomplete processing records as invalid.
* Update each file record independently.
* Mark a file as `pending` before new Phase 1 processing begins.
* Mark a file as `completed` only after Phase 1 finishes successfully.
* Mark a file as `failed` when Phase 1 cannot be completed.
* Reprocess the file when its content or processing settings change.
* Compare the embedding model, breakpoint percentile, buffer size, and chunking version.
* Search by content hash when differently named files contain identical content.
* Prevent failed or invalid files from continuing to Phase 2.

When valid matching content exists under another filename, the chunks may be reused, but the current filename must receive its own registry record.

## File-Processing Scenarios

### Scenario 1: New File

A file is considered new when no matching content hash exists in the processing registry.

The system must:

1. Calculate the original file hash.
2. Set the processing status to `pending`.
3. Run the complete data-preparation phase.
4. Generate and save the semantic chunks.
5. Calculate the chunks-file hash.
6. Save all required processing information.
7. Set the processing status to `completed`.
8. Mark the file as ready for Phase 2.

Phase 2 must not begin until Phase 1 has finished for all input files.

### Scenario 2: Existing File with Incomplete Phase 1 Results

A file may exist in the processing registry while its first-phase results do not satisfy all validation requirements.

The system must:

1. Calculate the current file hash.
2. Treat the previous results as invalid.
3. Prevent the file from continuing to Phase 2.
4. Set the processing status to `pending`.
5. Run the complete data-preparation phase again.
6. Generate and save a new semantic-chunks file.
7. Calculate the chunks-file hash.
8. Update the JSON registry with complete processing information.
9. Set the processing status to `completed` only after all Phase 1 operations succeed.
10. Mark the file as ready for Phase 2.

If reprocessing fails, the status must be changed to `failed`.

### Scenario 3: Existing File with Complete Results

A file is considered complete when:

* Its current content hash matches `input_sha256`.
* Its processing status is `completed`.
* Its stored embedding model matches the current model.
* Its stored breakpoint percentile matches the current setting.
* Its stored buffer size matches the current setting.
* Its stored chunking version matches the current version.
* Its semantic-chunks file exists and can be read.
* Its current chunks-file hash matches `chunks_sha256`.
* All required registry fields are available.

The system must:

1. Skip Stanza processing.
2. Skip embedding generation.
3. Skip semantic-distance calculation.
4. Skip semantic-chunk generation.
5. Load the saved semantic chunks.
6. Mark the file as ready for Phase 2.

## Semantic Chunking

The semantic-chunking process must preserve the original sentence order.

The system must:

1. Create one buffer-1 context window for each sentence.
2. Generate an embedding for every context window.
3. Validate and normalize the generated embeddings.
4. Calculate semantic distances between neighboring representations.
5. Calculate a breakpoint threshold using the configured percentile.
6. Create breakpoints where `distance > threshold`.
7. Group the original normalized sentences between the breakpoints into semantic chunks.
8. Add all sentences after the final breakpoint to the final chunk.

Each semantic chunk must contain:

* A sequential chunk number.
* The first sentence position.
* The final sentence position.
* The sentence count.
* The character count.
* The estimated token count.
* The complete chunk text.

Every source sentence must appear exactly once. The system must not remove, duplicate, or reorder source sentences.

## Saved Semantic Chunks

The semantic chunks for each file must be stored in a structured UTF-8 JSON file.

The saved information must include:

* The source filename.
* The original file hash.
* The processing settings.
* The total sentence count.
* The total chunk count.
* The metadata and text of every semantic chunk.

The field used for token information must be named:

```text
estimated_token_count
```

The file must be saved and validated successfully before the processing status is changed to `completed`.

## Phase Coordination

The system must complete or validate Phase 1 for every input file before beginning Phase 2.

The required order is:

```text
Phase 1: file 1
Phase 1: file 2
Phase 1: file 3

Phase 2: ready file 1
Phase 2: ready file 2
Phase 2: ready file 3
```

A failure in one file must not prevent other valid files from continuing.

Only files that successfully completed or reused Phase 1 may continue to Phase 2.

## Phase 2: Token-Based Batching

After Phase 1 has been completed for all input files, the system must load the semantic chunks for each ready file.

Neighboring semantic chunks must be combined according to configurable estimated-token limits.

The initial limits are:

```text
MIN_SUMMARIZATION_TOKENS = 1200
MAX_SUMMARIZATION_TOKENS = 1800
```

The current implementation may use a documented local token-estimation method.

The estimated count must not be described as an exact tokenizer result unless an exact local Llama 3 tokenizer is implemented.

The batching process must:

* Preserve the original chunk order.
* Prefer batches that remain between the minimum and maximum limits.
* Avoid creating unnecessarily small batches.
* Avoid losing or duplicating source sentences.
* Keep the contents of different files separate.
* Handle oversized chunks safely using sentence boundaries.
* Avoid creating a batch above the maximum limit when a sentence-boundary split is possible.
* Preserve semantic relationships as much as possible.

## Map-Reduce Summarization

### Map Stage

During the Map stage, the system must summarize every packed batch independently using `llama3`.

The model must:

* Use only the supplied source text.
* Preserve important events and facts.
* Preserve chronological order when relevant.
* Avoid adding unsupported information.
* Remove repetition and minor details.
* Return only the partial summary.

The partial summaries must be:

* Stored in the same order as the original batches.
* Saved in a UTF-8 text file.

### Reduce Stage

During the Reduce stage, the partial summaries must be combined using `llama3`.

The system must:

* Preserve the original order.
* Retain important information from all partial summaries.
* Remove repeated information.
* Avoid adding new facts.
* Produce one final summary for the current source file.

When all partial summaries fit into one safe model request, they may be reduced directly.

When the partial summaries exceed the safe input limit, the system must combine them through multiple ordered Reduce steps until only one final summary remains.

## Outputs

For every successfully processed file, the system must produce:

* A SHA-256 hash for the original file.
* A complete processing-registry record.
* A structured semantic-chunks JSON file.
* A SHA-256 hash for the chunks file.
* Ordered partial summaries.
* One final summary file.

Suggested output paths:

```text
outputs/chunks/file_name_chunks.json
outputs/summaries/file_name_partial_summaries.txt
outputs/summaries/file_name_summary.txt
```

All generated text and JSON files must use UTF-8.

## Error Handling

The system must handle:

* Missing input files.
* Unsupported file types.
* Empty files.
* UTF-8 decoding failures.
* Missing or invalid processing registries.
* Incomplete processing records.
* Missing or corrupted semantic-chunks files.
* Stanza initialization and processing failures.
* Embedding-generation failures.
* Invalid embedding responses.
* Token-estimation or batching failures.
* Ollama summarization failures.
* Output-saving failures.

An error must never cause a file to be marked as completed incorrectly.

A failed file must not continue to Phase 2.

A failure in one file must not corrupt the saved results of other files.

## Constraints

* The project must use Python.
* The implementation must use exactly four Python source files.
* The implementation must use functions and modules without classes.
* File hashing must use `hashlib`.
* Sentence segmentation must use Stanza.
* Stanza GPU usage must remain enabled.
* Embeddings must be generated using `mxbai-embed-large`.
* Summaries must be generated using `llama3`.
* Models must run locally through the `ollama` Python package.
* The current version must support UTF-8 `.txt` files only.
* Files must be processed sequentially within each phase.
* External language-model APIs must not be used.
* Runtime model and Stanza-resource downloads must not be performed.
* Manual Ollama HTTP requests must not be used.
* The contents of different files must not be mixed.
* Expensive operations must not run before validating saved results.
* Phase 1 and Phase 2 must remain separate.
* Phase 1 must finish for all files before Phase 2 begins.
* The required paragraph and buffer-1 semantic-chunking method must not be replaced.
* A file must not be considered complete before all Phase 1 results have been saved successfully.

## Acceptance Criteria

The project is considered complete when:

* The implementation contains `config.py`, `phase1.py`, `phase2.py`, and `main.py`.
* Multiple UTF-8 `.txt` files can be processed during one run.
* Every input file is validated independently.
* Non-UTF-8 and unsupported files are rejected.
* New files are processed from the beginning and all results are saved.
* Files with incomplete or corrupted results are processed again.
* Files with complete and valid results skip Phase 1 processing.
* Valid saved chunks prevent unnecessary repeated processing.
* Changed files or processing settings trigger new data preparation.
* The required paragraph-preparation method is used.
* Stanza uses the tokenizer processor with GPU enabled.
* Buffer-1 context windows are created correctly.
* Embeddings are generated in a local call using `mxbai-embed-large`.
* Embeddings are validated and L2-normalized.
* Semantic distances are calculated only between adjacent representations.
* Breakpoints use the configured percentile and strict greater-than comparison.
* Semantic chunks preserve every original source sentence.
* Phase 1 finishes for all files before Phase 2 begins.
* Semantic chunks are packed safely according to estimated-token limits.
* Oversized chunks are handled using sentence boundaries.
* Every packed batch produces one partial summary using `llama3`.
* Ordered partial summaries are saved.
* Map-Reduce produces one coherent final summary for each file.
* All required outputs are saved successfully using UTF-8.
* Errors are reported clearly.
* Failed files never continue to Phase 2.
* Classes, additional Python modules, external APIs, manual Ollama HTTP requests, and runtime downloads are not used.
