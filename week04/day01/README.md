# Day 01: What Is a Skill?

## Learning Objective

The goal of the first day of Week 4 was to understand what Claude Skills are, how they work, when Claude uses them, and why they are useful.

The lesson also explained that a Skill is stored inside a folder containing a main file called `SKILL.md`. This file includes the Skill name, its description, and the instructions Claude should follow when completing a related task.

The practical task was to analyze three existing Skills and explain when each Skill should be triggered and what problem it solves.

## What Are Skills?

Claude Skills are reusable instructions that teach Claude how to perform a specific task.

Instead of repeating the same instructions every time, the instructions can be written once inside a `SKILL.md` file. Claude then uses the Skill automatically when the user's request matches its description.

Each Skill contains a name and description in the frontmatter:

```yaml
---
name: skill-name
description: Explains what the Skill does and when it should be used.
---
```

Claude first reads the names and descriptions of the available Skills. When the user sends a request, Claude compares the request with the Skill descriptions and activates the most suitable Skill.

Skills can also include additional folders such as:

```text
examples/
reference/
scripts/
```

These files are loaded only when they are needed, which helps reduce unnecessary context usage.

## PDF Skill

The `pdf` Skill is used to handle PDF files. It should be triggered when the user provides a PDF file, mentions a file with the `.pdf` extension, or asks Claude to create a PDF.

The Skill supports different operations such as reading text, extracting tables, merging files, splitting pages, rotating pages, adding watermarks, creating new PDFs, filling forms, extracting images, and applying OCR to scanned documents.

This Skill solves the problem that PDF files cannot always be handled using the same method. Each type of task may require a different tool or library.

For example, extracting text is different from creating a PDF, and a scanned document may require OCR because it contains images instead of selectable text.

The Skill helps Claude select the correct method according to the user's request. It can also load additional instructions only when needed, such as form instructions or advanced PDF references.

## Internal Communications Skill

The `internal-comms` Skill is used to write internal communications for companies or teams.

It should be triggered when the user asks Claude to write a status report, project update, leadership update, company newsletter, FAQ, incident report, or a 3P update containing progress, plans, and problems.

This Skill solves the problem that different types of internal communication require different formats, tones, and content.

For example, a project update should not be written in the same way as a company newsletter or an incident report.

The Skill first identifies the communication type and then loads the correct guideline file from the `examples` directory.

It may use:

```text
examples/3p-updates.md
examples/company-newsletter.md
examples/faq-answers.md
examples/general-comms.md
```

This allows Claude to follow the correct format and writing style instead of producing all internal communications in the same general form.

## MCP Builder Skill

The `mcp-builder` Skill is used when creating an MCP Server that connects Claude or another language model to an external API or service.

It should be triggered when the user asks Claude to build an MCP Server using Python, FastMCP, Node.js, or TypeScript.

This Skill solves the problem that building an MCP Server requires more than writing code that connects to an API.

The tools provided by the server must have clear names, accurate descriptions, organized inputs and outputs, useful error messages, and suitable testing.

The Skill guides Claude through four main stages:

1. Research and planning.
2. Implementation.
3. Review and testing.
4. Creating evaluations.

It also uses different reference files depending on the selected language and development stage.

For example, it can load a Python guide when the server is being created with FastMCP, or a TypeScript guide when the MCP SDK is being used.

This helps Claude create an MCP Server that works correctly and is also easy for a language model to understand and use.

## Conclusion

Claude Skills provide reusable instructions for specific tasks.

They help reduce repeated explanations, improve consistency, and allow Claude to use the correct workflow according to the user's request.

The three analyzed Skills show that Skills can be designed for different purposes:

- The `pdf` Skill handles a specific file type.
- The `internal-comms` Skill handles a specific type of writing.
- The `mcp-builder` Skill handles a technical development workflow.