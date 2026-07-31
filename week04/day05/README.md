# Day 05: Test & Chain Skills

## Learning Objective

The goal of the fifth day of Week 4 was to combine the work completed during the week and use more than one Skill in a single workflow.

This day continued the work from Day 4. The `text-summarizer` Skill was updated so that it could summarize the source text first and then pass the completed summary to a design Skill when the user requested a visual output or PDF.

## Updating the Skill

The existing `text-summarizer` Skill was kept with all of its previous summarization instructions.

A new optional chaining workflow was added:

- If the user asks only for a summary, the Skill returns the text summary normally.
- If the user asks for a visual design, poster, infographic, or PDF, the Skill summarizes the source text first.
- The completed summary is then passed to the `canvas-design` Skill.
- If a PDF is requested, the final visual design is exported as a PDF.
- The design Skill is not used when the user requests only a text summary.

This kept the original Skill focused on summarization while allowing it to work with another Skill when needed.

## Chained Workflow

The completed workflow was:

```text
Source Text
    ↓
text-summarizer
    ↓
Structured Summary
    ↓
canvas-design
    ↓
One-Page Infographic PDF
```

## Testing the Chain

The chaining workflow was tested twice using the same prompt and the same source text.

Each test was performed in a separate Claude conversation after the updated version of the `text-summarizer` Skill was installed.

### Test Prompt

```text
Summarize the following text and turn the summary into a clear one-page visual infographic.

Focus only on the most important ideas and events. Use a clean and readable layout with short text sections, and export the final design as a PDF.

[The source text is available in inputs/source.txt.]
```

## Results

Both tests completed the requested workflow successfully.

Claude first used the `text-summarizer` Skill to identify and organize the most important ideas and events. It then continued to the visual design stage and generated a one-page infographic PDF.

### Test 1

Output file:

```text
outputs/alice_chapter1_infographic_01.pdf
```

The first output:

- Summarized the main events from *Down the Rabbit-Hole*.
- Used a clear one-page layout.
- Organized the events into short visual sections.
- Included the White Rabbit, the fall, the locked doors, the golden key, `DRINK ME`, and `EAT ME`.
- Included a final takeaway.
- Was exported successfully as a PDF.

### Test 2

Output file:

```text
outputs/alice_chapter1_infographic_02.pdf
```

The second output:

- Summarized the same source text successfully.
- Focused on the main sequence of events.
- Used a clean one-page visual design.
- Kept the text short and organized.
- Included a final takeaway.
- Was exported successfully as a PDF.

## Test Evaluation

The two tests showed that the chained workflow worked correctly.

The `text-summarizer` Skill handled the content first, and the design stage converted the summary into a visual PDF.

The two outputs were not identical in their design, but both followed the same requested workflow and produced a clear one-page infographic.

## Folder Structure

```text
week04/
└── day05/
    ├── README.md
    ├── text-summarizer/
    │   └── SKILL.md
    ├── inputs/
    │   └── source.txt
    └── outputs/
        ├── alice_chapter1_infographic_01.pdf
        └── alice_chapter1_infographic_02.pdf
```

## What I Learned

I learned how to connect two Skills in one workflow.

The first Skill handled the content by summarizing the source text, while the second Skill handled the visual design and PDF output.

I also learned how to make the chained workflow optional so that the design Skill is only used when the user requests a visual result.

Running the same workflow twice also showed that the Skill could complete the same task successfully in separate conversations.

## Conclusion

Day 5 completed the work of Week 4 by combining Skill development, testing, and Skill chaining.

The updated `text-summarizer` Skill successfully worked with a design Skill to transform a long source text into a clear one-page infographic PDF.