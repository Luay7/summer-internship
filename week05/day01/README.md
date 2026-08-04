# Day 01: Agents vs. Chatbots

## Learning Objective

The goal of Day 1 was to understand the difference between chatbots and AI agents and learn how the ReAct loop works.

## Chatbots and AI Agents

A chatbot mainly answers user questions.

An AI agent can go further by using tools, making decisions, and completing one or more tasks.

## Agent Design

### Project Name

Currency Exchange Rate and Conversion Agent

### Objective

The agent helps users check current exchange rates and convert money from one currency to another.

### Inputs

The user can ask for:

* The exchange rate between two currencies.
* The conversion of a specific amount.

Example:

```text
Convert 100 USD to SAR.
```

### Tools

* Exchange Rate Tool: Gets the current exchange rate.
* Calculator Tool: Calculates the converted amount.

### Outputs

The agent returns:

* The current exchange rate.
* The final converted amount.

## Decision Process

1. The agent reads the user's request.
2. It checks whether the user wants only the exchange rate or a full conversion.
3. It uses the Exchange Rate Tool to get the current rate.
4. If an amount is provided, it uses the Calculator Tool.
5. It returns the final result.

## ReAct Example

```text
User Request:
Convert 100 USD to SAR.

Thought:
The agent needs the current USD to SAR rate.

Action:
Use the Exchange Rate Tool.

Observation:
The rate is 3.75.

Thought:
The user provided an amount, so calculation is required.

Action:
Calculate 100 × 3.75.

Observation:
The result is 375.

Final Answer:
100 USD is equal to 375 SAR.
```

## Conclusion

Day 1 introduced the difference between chatbots and AI agents.

The currency conversion agent was designed with a clear objective, two tools, and a simple decision process based on the ReAct loop.
