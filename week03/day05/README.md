# Day 05: Testing and Iteration

## Learning Objective

The goal of the fifth day of Week 3 is to test whether an AI model can follow the project documentation correctly, identify ambiguous or missing requirements, revise the relevant documents, and repeat the test until the generated result becomes consistent with the expected behavior.

## Testing Approach

The testing process follows these steps:

1. Prepare clean versions of `README.md`, `spec.md`, and `system-prompt.md`.
2. Provide the three files to an AI model.
3. Request a complete implementation of the project.
4. Compare the generated code with the documented requirements.
5. Identify whether each issue was caused by unclear documentation or incomplete implementation.
6. Update only the relevant project documents.
7. Repeat the same test after the revisions.
8. Record the result of every iteration.

## Project Files Under Test

The following documents are used to guide the AI model:

* `project/README.md`
* `project/spec.md`
* `project/system-prompt.md`

The generated source code is stored inside:

```text
project/code/
```

## Expected Code Structure

The project must contain exactly four Python source files:

```text
project/code/
├── config.py
├── phase1.py
├── phase2.py
└── main.py
```

A separate `requirements.txt` file may be included for project dependencies.

## Iteration 1: Initial Implementation Test

### Test Setup

The introductory learning sections were removed from the three project documents. The cleaned `README.md`, `spec.md`, and `system-prompt.md` files were then provided to Google Gemini with a request to implement the complete project.

### Initial Result

Gemini generated a working Python structure containing configuration, core NLP functions, data preparation, summarization, utility functions, and a main execution file.

The generated solution followed the general project idea and included:

* Local Ollama model execution
* Stanza sentence segmentation
* SHA-256 file hashing
* Semantic chunking
* Processing-registry storage
* Token-based batching
* Map-Reduce summarization
* UTF-8 file reading and writing

### Issues Identified

The generated implementation did not fully match the intended design:

* The required source-file structure had not been defined, so the model created six Python modules instead of the intended four.
* The model used manual HTTP requests to the local Ollama service instead of the `ollama` Python package.
* Stanza model downloading was included in the runtime workflow.
* The exact paragraph preparation and semantic-chunking method was not specified.
* Phase 2 was started immediately after Phase 1 for each file instead of waiting for Phase 1 to finish for all files.
* The summarization model was selected by the AI because an exact model name had not been defined.
* Token counting was implemented as an approximation without being clearly documented as approximate.

### Analysis

Some differences were caused by missing or ambiguous documentation rather than incorrect interpretation by the AI model.

The initial documents explained the project architecture but did not define the exact Python file structure, the required Ollama integration method, or the complete Phase 1 algorithm.

### Planned Documentation Revisions

The next iteration will update:

* `README.md` with the exact project structure, local setup, supported encoding, and execution instructions.
* `spec.md` with the required four-file architecture, exact Phase 1 algorithm, UTF-8-only input policy, phase-order requirements, local Ollama library usage, and prohibition of runtime downloads.
* `system-prompt.md` with rules that prevent the AI model from creating additional modules or replacing explicitly required implementation methods.

### Iteration 1 Status

**Partially Passed — Documentation Revision Required**

The first test successfully identified requirements that must be made more explicit before the implementation can be evaluated reliably.

## Iteration 2: Final Implementation

Based on the issues found during the first test, the project documents were updated to clarify:

* The required four-file Python structure.
* The responsibility of each source file.
* UTF-8 input and output requirements.
* Local Ollama integration.
* The required embedding and summarization models.
* GPU-enabled Stanza processing.
* The exact semantic-chunking method.
* The required order of Phase 1 and Phase 2.
* Error handling and output requirements.

The updated documents were provided to the AI model again, and the second implementation followed the required architecture more accurately.

## Final Project Structure

```text
project/code/
├── config.py
├── main.py
├── phase1.py
├── phase2.py
├── requirements.txt
├── setup.sh
├── processing_registry.json
├── inputs/
└── outputs/
    ├── chunks/
    └── summaries/
```

The project uses:

* `mxbai-embed-large` for semantic embeddings.
* `llama3` for Map-Reduce summarization.
* Stanza with GPU enabled for sentence segmentation.
* UTF-8 `.txt` files as input.
* SHA-256 hashes to validate saved processing results.
* Semantic chunking with paragraph preparation and buffer-1 context windows.

## Execution Test

The project was tested using a UTF-8 text file containing Chapters I and II of *Alice’s Adventures in Wonderland*.

The setup script completed successfully, and the complete project ran without stopping.

The system successfully:

1. Validated and processed the input file.
2. Generated and saved the semantic chunks.
3. Updated the processing registry.
4. Created five ordered partial summaries.
5. Saved the partial summaries.
6. Combined them through the Reduce stage.
7. Generated and saved one final summary.

The final summary covered the main events in their original order. Minor wording issues appeared in the generated summary, but the complete technical pipeline worked successfully and produced all required outputs.

## Final Status

**Passed — The project was successfully set up, executed locally, and produced the required intermediate and final outputs.**

## Running the Project

Run the setup script first:

```bash
chmod +x setup.sh
./setup.sh
```

After the setup completes, run the project:

```bash
python main.py
```

The input UTF-8 `.txt` files must be placed inside the `inputs` directory before running `main.py`.

## Final Outcome

The testing process showed that clear documentation improves the accuracy of AI-generated software.

The first implementation revealed missing and ambiguous requirements. After updating `README.md`, `spec.md`, and `system-prompt.md`, the second implementation followed the intended architecture and processing workflow.

The final project was successfully installed, tested, and executed locally.