---
name: text-summarizer
description: Summarizes text pasted directly in the prompt into an introduction, key bullet points, and a conclusion. Use when the user explicitly asks to summarize, shorten, condense, or extract key points, or indirectly asks for the main ideas, key events, overall takeaway, gist, quick rundown, what the text is about, or the most important information. Write the summary in the same language as the source text unless another language is requested. If the user also wants the summary turned into a visual design, poster, infographic, or PDF, summarize with this Skill first, then hand the summary off to the canvas-design Skill.
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

If the user asks to turn the summary into a visual design, poster, infographic, or PDF, follow the normal process below and then continue with the "Turning a Summary into a Visual Design" workflow at the end of this document. If the user only asks for a summary, ignore that workflow and return the text summary.

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

## Turning a Summary into a Visual Design

This workflow is optional. Only use it when the user asks to turn the summary into a visual design, poster, infographic, or PDF. Do not invoke canvas-design for a plain summary request — in that case, just return the text summary as described above.

When a visual or designed output is requested:

1. First, summarize the source text following the standard process above (How to Summarize, Output Structure, Language Rule).
2. Once the summary is complete, invoke the canvas-design Skill, using the finished summary as the content to be designed.
3. The final design should be clear, visually organized, and focused only on the most important information in the summary — do not try to fit in every detail.
4. If the user asked for a PDF, export the final design from canvas-design as a PDF.