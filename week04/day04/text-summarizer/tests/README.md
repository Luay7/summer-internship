# Text Summarizer Skill Tests

## Testing Objective

The purpose of these tests is to verify that the completed `text-summarizer` Skill performs its intended task successfully.

The Skill will be tested in two languages:

- English
- Arabic

Two tests will be performed for each language:

1. An implicit request that does not use the word `summarize`. This checks whether Claude can recognize the user's intent and apply the Skill's default output structure.
2. An explicit request that directly asks for a summary and specifies a custom length, focus, and output format. This checks whether explicit user instructions take priority over the default structure.

Each test is performed in a separate Claude conversation so that previous prompts and responses do not affect the result.

## Test Structure

```text
tests/
├── README.md
├── english/
│   └── test-results.md
└── arabic/
    └── test-results.md
```

The full source text is pasted directly into Claude during each test. It is not repeated inside the result files because the English source is long and the same text is reused for both tests in each language.

## English Tests

The English tests use Chapter I, *Down the Rabbit-Hole*.

- [English test results](english/test-results.md)

## Arabic Tests

The Arabic tests use an Arabic version of the same main events.

- [Arabic test results](arabic/test-results.md)

## Evaluation Criteria

The results are checked for:

- Correct recognition of explicit and implicit summarization requests.
- Use of the same language as the source text.
- Correct use of the default structure when no custom format is requested.
- Compliance with custom length and formatting instructions.
- Preservation of important names, events, objects, numbers, and facts.
- Avoidance of unsupported information that is not present in the source text.

