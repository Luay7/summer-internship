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

## Next Iteration

After revising the three project documents, the same implementation request will be submitted again.

The second generated result will be compared with the updated specification to determine whether the documentation changes reduced ambiguity and improved compliance.
