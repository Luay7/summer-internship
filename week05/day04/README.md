# Day 04: Planning & Decomposition

## Learning Objective

The goal of Day 4 of Week 5 was to understand planning and task decomposition and apply them to the existing agent so it can handle multi-step requests in a more organized way.

## Planning & Decomposition

Task decomposition breaks a user request into smaller and more manageable steps.

Planning determines the correct and logical order for executing those steps.

In this version of the agent, planning and decomposition happen before execution. The complete user request is first analyzed and converted into an ordered Plan. The execution stage then follows that Plan one step at a time.

```text
User Request
    ↓
Planning & Decomposition
    ↓
Plan
    ↓
Execution
    ↓
Thought → Action → Observation
    ↓
Next Planned Step
    ↓
Final Answer
```

## Agent Development

The Day 3 agent already supported multiple tools and conversation memory. It could also perform more than one action, but it started executing the request directly.

For Day 4, I separated the workflow into two stages:

### 1. Planning Stage

The `PLANNING_PROMPT` analyzes the complete user request and generates an ordered Plan.

This stage does not execute any tools.

### 2. Execution Stage

The generated Plan is added to `prompt_history` and passed to the execution agent.

The `SYSTEM_PROMPT` then follows the Plan one step at a time using the available tools:

- `get_exchange_rate()` retrieves current exchange rates.
- `calculator()` performs the required conversion calculations.

Each tool result is returned as an Observation and added to the context before the agent continues to the next planned step.

## Maximum Agent Steps

The agent uses a maximum step limit:

```python
max_steps = 10
```

The required number of agent stages depends on the number of operations generated in the Plan.

For example, a Plan containing six operations can use:

```text
Step 1     → Planning & Decomposition
Steps 2–7  → Execute the six planned operations
Step 8     → Final Answer
```

Using `max_steps = 10` gives the agent enough execution space for this type of request while also preventing the execution loop from continuing indefinitely.

## Testing

I tested the agent with a chained currency conversion that requires several dependent operations.

### User Request

```text
Convert 1000 SAR to USD, then convert the resulting USD amount to EUR, then convert the resulting EUR amount to JPY.
```

### Output

```text
[User Query]: Convert 1000 SAR to USD, then convert the resulting USD amount to EUR, then convert the resulting EUR amount to JPY.
============================================================

--- [Step 1: Planning & Decomposition] ---
Plan:
1. Get the exchange rate from SAR to USD.
2. Calculate the equivalent amount in USD.
3. Get the exchange rate from USD to EUR.
4. Calculate the equivalent amount in EUR.
5. Get the exchange rate from EUR to JPY.
6. Calculate the equivalent amount in JPY.

--- [Step 2] ---
Thought: I need to start by getting the current exchange rate between SAR and USD.
Action: get_exchange_rate(SAR, USD)
[Observation] 1 SAR = 0.266667 USD

--- [Step 3] ---
Thought: Now that I have the exchange rate from SAR to USD, I can calculate the equivalent amount in USD.
Action: calculator(1000 * 0.266667)
[Observation] 266.667

--- [Step 4] ---
Thought: Next, I need to get the exchange rate between USD and EUR.
Action: get_exchange_rate(USD, EUR)
[Observation] 1 USD = 0.867027 EUR

--- [Step 5] ---
Thought: Now that I have the exchange rate from USD to EUR, I can calculate the equivalent amount in EUR.
Action: calculator(266.667 * 0.867027)
[Observation] 231.20748900899997

--- [Step 6] ---
Thought: Finally, I need to get the exchange rate between EUR and JPY.
Action: get_exchange_rate(EUR, JPY)
[Observation] 1 EUR = 183.716157 JPY

--- [Step 7] ---
Thought: Now that I have the exchange rates for all three conversions, I can calculate the final amount in JPY.
Action: calculator(231.20748900899997 * 183.716157)
[Observation] 42476.55135035321

--- [Step 8] ---
Final Answer: 1000 SAR = 266.667 USD = 231.207 EUR = 42476.55135035321 JPY

[Success] Task Completed Successfully.
```

The output shows that the agent first decomposed the request into six ordered operations and then executed each step according to the generated Plan.

## Conclusion

Day 4 extended the existing multi-tool agent with a separate planning and decomposition stage.

The agent now analyzes the complete request before execution, creates an ordered Plan, and then follows that Plan step by step using the required tools.
