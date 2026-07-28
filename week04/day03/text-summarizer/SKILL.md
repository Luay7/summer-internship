---
name: text-summarizer
description: Summarizes long text into an intro, key bullet points, and a conclusion, in the same language as the source text. Use whenever the user provides a long text and asks to summarize it, shorten it, or extract key points.
---

# Text Summarizer

Summarizes long text (articles, reports, or any long text) into a clear, consistent format.

## When to use

Trigger when the user gives a long text and asks to summarize, shorten, or extract key points from it. Skip this for very short text or pure translation requests.

## Output structure

1. **Intro** (2-3 sentences): what the text is about.
2. **Bullet points**: each with a bold header + 1-2 sentences. Number of points scales with text length (roughly 3-8).
3. **Conclusion** (1-2 sentences): the overall takeaway.

## Language rule

Write the summary in the same language as the source text unless the user explicitly requests another language.

## Example

```
[Intro]

- **[Header]**: [explanation]
- **[Header]**: [explanation]

[Conclusion]
```
