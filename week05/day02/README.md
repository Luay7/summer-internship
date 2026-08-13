# Day 02: Single-Tool Currency Exchange Agent

## Learning Objective

The goal of Day 2 of Week 5 was to move from the basic concept of AI agents to a practical implementation and build an agent that can use one external tool.

## Agent Implementation

I implemented a simple Currency Exchange Rate Agent using `gemma3:4b` through Ollama.

The agent has one main task: retrieving the current exchange rate between two currencies.

It uses one available tool:

- `get_exchange_rate(from_curr, to_curr)`

The tool is connected to an external exchange-rate API to retrieve the current rate.

## Agent Workflow

The agent first reads the user's request and decides whether it is related to currency exchange rates.

If the request is valid and related to its task:

1. The agent identifies the two currencies.
2. It uses the exchange-rate tool.
3. The tool retrieves the current rate from the API.
4. The result is returned to the agent as an observation.
5. The agent returns the final answer.

If the request is outside the agent's task, it does not use the tool and informs the user that the request is not related to currency exchange rates.

The agent also handles invalid or unsupported currency codes. If an invalid currency is detected or returned by the exchange-rate service, the agent explains the error instead of generating an exchange rate.

If more than one invalid currency is provided, the process can stop when the first invalid currency is identified because the exchange request cannot be completed.

## Test 1: Valid Exchange Rate Request

```text
[User Query]: What is the exchange rate from SAR to USD?
============================================================

--- [Step 1] ---
Thought: I need to find the current exchange rate between Saudi Riyal (SAR) and US Dollar (USD).
Action: get_exchange_rate(SAR, USD)
[Observation] 1 SAR = 0.266667 USD

--- [Step 2] ---
Final Answer: 1 SAR = 0.266667 USD

[Success] Task Completed Successfully.
```

The agent correctly identified the currencies, used the exchange-rate tool, received the API result, and returned the final exchange rate.

## Test 2: Invalid Currency

```text
[User Query]: What is the exchange rate from SAR to XYZ?
============================================================

--- [Step 1] ---
Thought: I need to find the current exchange rate between Saudi Riyal (SAR) and a currency called XYZ. However, the currency code "XYZ" is not valid.
Final Answer: The target currency code is not valid or supported.

[Success] Task Completed Successfully.
```

The agent identified that the requested currency code was invalid and returned an error instead of providing an incorrect exchange rate.

## Test 3: Unrelated Request

```text
[User Query]: What is the capital of Saudi Riyal?
============================================================

--- [Step 1] ---
Thought: The user is asking for the capital of the Saudi Riyal, which is a currency. I cannot answer this question as it is unrelated to currency exchange rates.
Final Answer: This request is outside my task. I can only help with currency exchange rates.

[Success] Task Completed Successfully.
```

The agent recognized that the request was outside its assigned task and completed the request without using the exchange-rate tool.

## Conclusion

Day 2 focused on implementing a working AI agent with one external tool.

The agent can retrieve current exchange rates through an external API, decide whether a request is related to its task, and handle valid, invalid, and unrelated requests without generating unsupported results.