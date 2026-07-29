---
name: text-summarizer
description: Summarizes text pasted directly in the prompt into an introduction, key bullet points, and a conclusion. Use when the user explicitly asks to summarize, shorten, condense, or extract key points, or indirectly asks for the main ideas, key events, overall takeaway, gist, quick rundown, what the text is about, or the most important information. Write the summary in the same language as the source text unless another language is requested.
---

# Text Summarizer

Summarizes long text pasted directly in the prompt, such as articles and reports, into a clear and consistent format.

## When to Use

Use this Skill when the user provides text and directly or indirectly asks for a shorter explanation of its content.

Direct requests may include:

- Summarize this text.
- Shorten this article.
- Extract the key points.
- Give me a TL;DR.

Indirect requests may include:

- What are the main ideas?
- What are the key events?
- What is the overall takeaway?
- What is this text mainly about?
- Give me a quick rundown.
- What is the most important information here?

Do not require the user to use the exact word `summarize`.

Do not use this Skill for pure translation requests.

If the Skill is invoked but no source text is included, ask the user to paste the text they want summarized.

## How to Summarize

Read the entire text carefully before writing the summary.

Understand its main ideas, structure, and the relationships between its parts. Do not summarize sentence by sentence while reading.

Base the summary only on the provided text. Do not add outside facts, context, opinions, or assumptions.

Preserve important names, dates, numbers, facts, and technical terms when they are necessary to understand the text.

## Output Structure

For very short text, provide a brief direct summary without forcing the full intro, bullet points, and conclusion structure.

For longer text, use this structure by default unless the user explicitly requests another format, length, or structure:

1. **Intro** (2-3 sentences): Explain what the text is about.
2. **Bullet points**: Give each point a short bold heading followed by 1-2 explanatory sentences. Use approximately 3-8 points depending on the text length.
3. **Conclusion** (1-2 sentences): State the overall takeaway.

## Language Rule

Write the summary in the same language as the source text unless the user explicitly requests another language.

## Example

```text
[Intro]

- **[Header]**: [Explanation]
- **[Header]**: [Explanation]

[Conclusion]
```