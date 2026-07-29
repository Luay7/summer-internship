# Day 04: Build Your Own Skill

## Learning Objective

The goal of the fourth day of Week 4 was to develop the custom Skill created on Day 3 into a more complete version and verify that it performs its intended task successfully.

This day continued the work from Day 3. The previous day focused on designing the folder structure and writing the first version of the `SKILL.md` file. Day 4 focused on improving the instructions, uploading the Skill to Claude, and testing its behavior with real text.

The practical task was to implement the `text-summarizer` Skill and verify that it could summarize text using both its default structure and user-specified settings.

## Developing the Skill

The first version of the `text-summarizer` Skill already included:

- The Skill name and description.
- When the Skill should be used.
- The default output structure.
- The language rule.
- A simple output example.

For Day 4, the Skill was expanded with clearer instructions.

The updated version now tells Claude to:

- Read the complete text before writing the summary.
- Understand the main ideas and relationships between the parts.
- Base the summary only on the provided text.
- Avoid adding outside facts, opinions, or assumptions.
- Preserve important names, dates, numbers, facts, and technical terms.
- Ask the user to provide the source text when no text is included.
- Use a short direct summary for very short text.
- Use the default structure unless the user requests another format, length, or structure.

The default output structure remains:

1. A short introduction.
2. Key points.
3. A short conclusion.

The summary is written in the same language as the source text unless the user explicitly requests another language.

## Improving Implicit Triggering

The first description focused mainly on direct summarization requests such as:

```text
Summarize this text.
Shorten this article.
Extract the key points.
```

During the first implicit test, it was not clear enough whether Claude matched the indirect request with the custom Skill.

The Skill description and the `When to Use` section were therefore updated to include indirect requests such as:

```text
What are the main ideas?
What are the key events?
What is the overall takeaway?
What is this text mainly about?
Give me a quick rundown.
```

After this change, the repeated implicit tests produced results that followed the main summarization behavior more clearly.

## Uploading the Skill

The completed Skill was placed inside its own folder:

```text
text-summarizer/
└── SKILL.md
```

The folder was compressed and uploaded successfully to Claude.

No templates, scripts, or additional resources were required because the Skill could be implemented using one Markdown file.

## Skill Verification

The Skill was tested in English and Arabic.

For each language, two test types were used:

1. An implicit request that did not use the word `summarize`.
2. An explicit request that specified a custom format and word limit.

Each test was performed in a separate Claude conversation to prevent previous context from affecting the result.

### Implicit Test

The implicit prompt asked for the main ideas, key events, and overall takeaway.

This test checked whether Claude could understand the summarization intent without an explicit command and then use the default structure.

The results were written in the same language as the source text and included the main parts of the default structure.

### Explicit Test

The explicit prompt requested:

- One paragraph.
- No more than 150 words.
- No headings or bullet points.
- Focus on the main events and important decisions.

This test checked whether the user's explicit instructions would take priority over the Skill's default structure.

The English and Arabic results followed the requested single-paragraph format and focused on the main events. The English result slightly exceeded the requested word limit, while the Arabic result stayed within it.

## Test Files

The test documentation is stored in the `tests` folder:

```text
tests/
├── README.md
├── english/
│   └── test-results.md
└── arabic/
    └── test-results.md
```

The result files include the prompts, actual outputs, and short evaluations.

- [English test results](tests/english/test-results.md)
- [Arabic test results](tests/arabic/test-results.md)

## Folder Structure

The Day 4 submission uses the following structure:

```text
week04/
└── day04/
    ├── README.md
    ├── text-summarizer/
    │   └── SKILL.md
    └── tests/
        ├── README.md
        ├── english/
        │   └── test-results.md
        └── arabic/
            └── test-results.md
```

## What I Learned

I learned that completing a Skill requires more than defining its output format.

The instructions must also explain how Claude should process the input, preserve accuracy, handle missing text, and respond when the user requests a different format.

I also learned that the Skill description affects how well Claude recognizes indirect requests. Adding clear indirect examples improved the Skill's matching behavior during testing.

The tests showed that the Skill could summarize English and Arabic text, use its default structure, and adapt to custom user requirements.

## Conclusion

Day 4 focused on developing the first Skill draft into a usable custom Skill.

The `text-summarizer` Skill was improved, uploaded successfully, and tested with implicit and explicit requests in English and Arabic.

The results confirmed that the Skill performed its main task successfully, while also revealing a minor issue with strict word-limit compliance that can be improved during further testing.