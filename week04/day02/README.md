# Day 02: Using Existing Skills

## Learning Objective

The goal of the second day of Week 4 was to use existing Claude Skills in practice and observe how the same Skill changes its behavior depending on the user request.

The lesson explained that testing a Skill with only one prompt is not enough. A Skill should be tested with several prompts to confirm that it is triggered in the correct situations and that its output changes correctly according to the requested task.

The practical task was to execute existing Claude Skills using different inputs and compare their outputs and behavior.

## Testing Method

Two existing Skills were selected:

- `internal-comms`
- `brand-guidelines`

Each Skill was tested with three prompts.

Every prompt was used in a separate Claude conversation. This prevented a previous prompt or response from affecting the next test.

The same main information was reused when possible, while the requested format or design purpose was changed.

The visual outputs from the `brand-guidelines` tests are saved in the `outputs/` folder. The `internal-comms` results are included directly in this README.

## Internal Communications Skill

The `internal-comms` Skill is used to write internal communications for companies or teams.

Its files provide three specific formats:

- `3P updates`
- `company newsletters`
- `FAQ answers`

It also provides `general-comms` for requests that do not clearly match one of the three specific formats.

### Test 1: 3P Update

**Prompt:**

```text
Write a 3P internal update using the following information:

This is Week 4 of my AI engineering training.

Completed:
- Learned what Claude Skills are.
- Analyzed the PDF, internal-comms, and mcp-builder Skills.
- Learned how Skills are triggered using their descriptions.

Current work:
- Testing existing Skills using different prompts.

Next:
- Compare the outputs and document the results.

Problem:
- It was initially unclear how to install and confirm that a Skill was being used.
```

**Output:**

```text
Progress: Learned what Claude Skills are and how they get triggered via their descriptions. Analyzed the PDF, internal-comms, and mcp-builder Skills to understand their structure.

Plans: Test existing Skills across a range of different prompts, then compare outputs and document findings.

Problems: Initial confusion on how to install a Skill and confirm it was actually being triggered or used.
```

The result matched the requested format and organized the information into `Progress`, `Plans`, and `Problems`.

### Test 2: FAQ

**Prompt:**

```text
Create a short internal FAQ based on the following information:

This is Week 4 of my AI engineering training.

Completed:
- Learned what Claude Skills are.
- Analyzed the PDF, internal-comms, and mcp-builder Skills.
- Learned how Skills are triggered using their descriptions.

Current work:
- Testing existing Skills using different prompts.

Next:
- Compare the outputs and document the results.

Problem:
- It was initially unclear how to install and confirm that a Skill was being used.
```

**Output excerpt:**

```text
Q: What have you learned so far this week?
A: I learned what Claude Skills are and analyzed three examples.

Q: How do Skills know when to activate?
A: Skills are triggered based on their descriptions.

Q: What are you working on right now?
A: I am testing existing Skills using different prompts.
```

The result changed the same information into questions and answers, which matched the requested FAQ format.

### Test 3: Leadership Update

**Prompt:**

```text
Write a short leadership update using the following information:

This is Week 4 of my AI engineering training.

Completed:
- Learned what Claude Skills are.
- Analyzed the PDF, internal-comms, and mcp-builder Skills.
- Learned how Skills are triggered using their descriptions.

Current work:
- Testing existing Skills using different prompts.

Next:
- Compare the outputs and document the results.

Problem:
- It was initially unclear how to install and confirm that a Skill was being used.

Focus on progress, current status, and the next step.
```

**Initial Response:**

```text
This is a personal training update (individual, not a team), so I'll follow the 3P format but adapt it slightly for an individual context. I have all the content already provided.

What name should I use for the update header
(e.g., your name or "AI Engineering Training")?
```

**My Response:**

```text
AI Engineering Training
```

**Final Output:**

```text
AI Engineering Training (Week 4)

Progress: Learned what Claude Skills are and how they're triggered via their descriptions; analyzed the PDF, internal-comms, and mcp-builder Skills to understand their structure.

Plans: Currently testing existing Skills with a range of prompts; next step is comparing outputs and documenting the results.

Problems: Initial unclear on how to install a Skill and confirm it was actually being used — now resolved through testing.
```

Although the prompt requested a leadership update, Claude identified the content as a personal training update rather than a team or company update.

It selected an adapted 3P format, asked for the name to use in the header, and then organized the information into `Progress`, `Plans`, and `Problems`.

In this test, Claude did not simply follow the phrase `leadership update`. It also analyzed the individual training context and selected an adapted 3P format, which it considered more suitable for the provided information.

### Internal Communications Comparison

| Test | Requested Format | Output Behavior |
|---|---|---|
| 3P Update | Explicit 3P structure | Organized the content into Progress, Plans, and Problems |
| FAQ | Explicit FAQ structure | Converted the same information into questions and answers |
| Leadership Update | Requested a leadership-focused update | Identified the individual context and used an adapted 3P format |

## Brand Guidelines Skill

The `brand-guidelines` Skill applies Anthropic's visual identity to artifacts.

It keeps consistent brand elements such as colors, typography, and visual style, while changing the layout according to the purpose of the requested artifact.

The same five Week 4 tasks were used in all three tests.

### Test 1: Project Progress Update

**Prompt:**

```text
Create a one-page project update using Anthropic's official brand colors and typography.

Title: AI Engineering Training — Week 4
Subtitle: Claude Skills Progress Update

Completed:
- Day 1 — What is a skill

In Progress:
- Day 2 — Using existing skills

Next:
- Day 3 — The SKILL.md structure
- Day 4 — Build your own skill
- Day 5 — Test & chain skills
```

**Output:**

Claude created an HTML project-update design with three sections:

- `Completed`
- `In Progress`
- `Next`

The design focused on the current status of the Week 4 plan.

Full output: [`outputs/brand-guidelines-project-update.html`](outputs/brand-guidelines-project-update.html)

### Test 2: Weekly Training Poster

**Prompt:**

```text
Create a simple internal training poster using Anthropic's official brand style.

Title: Week 4 — Claude Skills
Subtitle: Weekly Training Topics

Include:
01 — What is a skill
02 — Using existing skills
03 — The SKILL.md structure
04 — Build your own skill
05 — Test & chain skills
```

**Output:**

Claude created a different HTML design that displayed the five tasks as a numbered curriculum list.

The result did not show task status because the purpose was to present the week's topics rather than progress.

Full output: [`outputs/brand-guidelines-training-poster.html`](outputs/brand-guidelines-training-poster.html)

### Test 3: Weekly Roadmap

**Prompt:**

```text
Create a weekly roadmap for Week 4 using Anthropic's official brand colors and typography.

Day 1 — What is a skill — Completed
Day 2 — Using existing skills — In Progress
Day 3 — The SKILL.md structure — Next
Day 4 — Build your own skill — Next
Day 5 — Test & chain skills — Next
```

**Output:**

Claude created a timeline that displayed the five days in sequence.

The design used different colors to distinguish `Completed`, `In Progress`, and `Next`.

Full output: [`outputs/brand-guidelines-roadmap.png`](outputs/brand-guidelines-roadmap.png)

### Brand Guidelines Comparison

| Test | Purpose | Output Structure |
|---|---|---|
| Project Progress Update | Show current progress | Status-based sections |
| Weekly Training Poster | Present the Week 4 topics | Numbered curriculum list |
| Weekly Roadmap | Show sequence and status | Timeline |

The Skill kept a consistent Anthropic visual identity across all outputs, but it changed the layout according to the purpose of each prompt.

## What I Learned

The tests showed that the same Skill can produce different outputs depending on the requested format or purpose.

The `internal-comms` Skill changed its behavior between a 3P update, FAQ, and leadership update.

The `brand-guidelines` Skill kept the same visual identity but changed the design between a project update, poster, and roadmap.

Using a new conversation for every prompt made the comparison more reliable because each result was independent of the previous conversation context.

## Conclusion

Existing Skills should be tested with multiple prompts rather than only one successful example.

The actual outputs are important because they provide evidence of how the Skill behaved and make it possible to compare the results clearly.
