# Day 03: The SKILL.md Structure

## Learning Objective

The goal of the third day of Week 4 was to understand the structure of a `SKILL.md` file and apply it by creating the first version of a custom Claude Skill.

This day continued the concepts from Days 1 and 2. The previous days focused on understanding what Skills are and observing how existing Skills behave. Day 3 focused on how a Skill is designed and how its instructions are organized.

The practical task was to design the Skill folder structure and write the first version of its `SKILL.md` file.

## Understanding the SKILL.md Structure

A `SKILL.md` file contains two main parts:

1. YAML frontmatter.
2. The instruction body.

The YAML frontmatter contains the Skill name and description.

```yaml
---
name: skill-name
description: Explains what the Skill does and when it should be used.
---
```

Claude can use the Skill description to compare the user's request with the available Skills and determine whether the Skill is relevant.

The instruction body appears below the frontmatter. It contains the detailed instructions Claude should follow after the Skill is selected.

A Skill folder may also include optional files such as templates, resources, examples, or scripts. These files are only needed when the Skill requires additional guidance or functionality.

## Custom Skill Idea

The selected custom Skill was `text-summarizer`.

Its purpose is to summarize long text into a clear and consistent structure containing:

1. A short introduction.
2. Key bullet points.
3. A short conclusion.

The summary should use the same language as the source text unless the user explicitly requests another language.

## Folder Structure

The Day 3 submission uses the following structure:

```text
week04/
└── day03/
    ├── README.md
    └── text-summarizer/
        └── SKILL.md
```

The `README.md` file documents the work completed during Day 3.

The `text-summarizer` folder is the actual Skill folder. Its name matches the Skill name, and it contains the main `SKILL.md` file.

No additional folders were added because the first version does not require templates, resources, examples, or scripts.

## First Version of the Skill

The first version was written as a Markdown-only Skill:

```text
text-summarizer/
└── SKILL.md
```

The frontmatter defines the Skill name, purpose, and triggering conditions.

The instruction body defines when the Skill should be used, the expected summary structure, the language rule, and a simple output example.

This version focuses on the basic structure and instructions. It has not yet been expanded with supporting files because they are not required for the current task.

The next stage is to implement and test the Skill using real text inputs, then update its instructions if the results do not match the intended behavior.

## What I Learned

I learned that a Skill can begin with a simple folder containing only `SKILL.md`.

The frontmatter helps Claude identify the Skill and decide when it is relevant, while the instruction body defines how the task should be completed.

I also learned that supporting files are optional and should only be added when the Skill needs templates, examples, references, or scripts.

## Conclusion

Day 3 focused on applying the structure of a Claude Skill through a simple practical example.

The folder structure was designed, and the first version of the `text-summarizer` Skill was created using metadata and plain Markdown instructions.
