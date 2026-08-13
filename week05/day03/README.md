# Day 03: Adding Tools & Memory

## Learning Objective

The goal of Day 3 of Week 5 was to extend the existing agent by adding a second tool and conversation memory.

The agent should be able to use more than one tool in the same task and use previous conversation context when handling a new request.

## Agent Development

The Currency Exchange Agent from Day 2 was extended with a second tool for calculations.

The agent now has two tools:

- `get_exchange_rate(from_curr, to_curr)`: Retrieves the current exchange rate from an external API.
- `calculator(expression)`: Performs the calculation required to convert an amount between currencies.

For a currency conversion, the agent can first retrieve the exchange rate and then use the calculator to calculate the converted amount.

## Conversation Memory

Conversation memory was added so the agent can use information from previous interactions.

For example:

```text
User:
Convert 100 SAR to USD.

User:
What about 500?
```

The second request does not include the currencies again, but the agent can use the previous conversation context to understand that the user is still referring to SAR and USD.

## Memory Issue

During the first test, the agent remembered the previous conversation but confused the converted amount with the exchange rate.

The first conversion returned:

```text
100 SAR = 26.6667 USD
```

When the user later asked:

```text
What about 500?
```

the agent incorrectly attempted to use `26.6667` as the exchange rate instead of the actual rate `0.266667`.

This showed that storing conversation history alone was not enough. The information stored in memory also needed to be clear.

## Solution

The system prompt and memory format were improved so the agent could distinguish between:

- The source and target currencies.
- The exchange rate.
- The original amount.
- The converted result.

The final conversion response was also changed to include the exchange rate clearly:

```text
Using 1 SAR = 0.266667 USD, 100 SAR = 26.6667 USD.
```

Additional rules were added so the agent does not treat a previous converted amount as an exchange rate.

## Testing

### Test 1: Two-Tool Currency Conversion

Prompt:

```text
Convert 100 SAR to USD.
```

Output:

```text
[You]: Convert 100 SAR to USD.

[User Query]: Convert 100 SAR to USD.
============================================================

--- [Step 1] ---
Thought: I need to get the current exchange rate between SAR and USD and then use the calculator to convert 100 SAR to USD.
Action: get_exchange_rate(SAR, USD)
[Observation] 1 SAR = 0.266667 USD

--- [Step 2] ---
Thought: Now I have the exchange rate, I can use the calculator to convert 100 SAR to USD.
Action: calculator(100 * 0.266667)
[Observation] 26.6667

--- [Step 3] ---
Final Answer: Using 1 SAR = 0.266667 USD, 100 SAR = 26.6667 USD.

[Success] Task Completed Successfully.
```

The agent successfully used both tools in sequence.

### Test 2: Using Previous Context

Prompt:

```text
What about 500?
```

Output:

```text
[You]: What about 500?

[User Query]: What about 500?
============================================================

--- [Step 1] ---
Thought: The user wants to convert 500 SAR to USD. I need to get the current exchange rate between SAR and USD.
Action: get_exchange_rate(SAR, USD)
[Observation] 1 SAR = 0.266667 USD

--- [Step 2] ---
Thought: The user wants to convert 500 SAR to USD using the latest exchange rate. I will use the calculator tool to perform the conversion.
Action: calculator(500 * 0.266667)
[Observation] 133.3335

--- [Step 3] ---
Final Answer: Using 1 SAR = 0.266667 USD, 500 SAR = 133.3335 USD.

[Success] Task Completed Successfully.
```

The agent used the previous conversation to understand that the new amount should still be converted from SAR to USD.

### Test 3: Changing the Currency Context

Prompt:

```text
Convert 100 SAR to JPY
```

Output:

```text
[You]: Convert 100 SAR to JPY

[User Query]: Convert 100 SAR to JPY
============================================================

--- [Step 1] ---
Thought: I need to get the exchange rate from SAR to JPY and then perform the conversion.
Action: get_exchange_rate(SAR, JPY)
[Observation] 1 SAR = 42.480915 JPY

--- [Step 2] ---
Thought: Now that I have the exchange rate, I can convert 100 SAR to JPY.
Action: calculator(100 * 42.480915)
Final Answer: Using 1 SAR = 42.480915 JPY, 100 SAR = 4248.0915 JPY.

[Success] Task Completed Successfully.
```

The agent updated the conversation context from SAR-to-USD to SAR-to-JPY.

A follow-up request was then tested:

```text
What about 150?
```

Output:

```text
[You]: What about 150?

[User Query]: What about 150?
============================================================

--- [Step 1] ---
Thought: The user wants to convert 150 SAR to JPY. I need to get the exchange rate from SAR to JPY and then use the calculator tool to perform the conversion.
Action: get_exchange_rate(SAR, JPY)
[Observation] 1 SAR = 42.480915 JPY

--- [Step 2] ---
Thought: Now that I have the exchange rate, I can convert 150 SAR to JPY using the calculator tool.
Action: calculator(150 * 42.480915)
Final Answer: Using 1 SAR = 42.480915 JPY, 150 SAR = 6372.13725 JPY.

[Success] Task Completed Successfully.
```

The agent correctly understood that the new request referred to the latest SAR-to-JPY context.

### Test 4: Unsupported Currency

Prompt:

```text
What is the exchange rate from SAR to XYZ?
```

Output:

```text
[You]: What is the exchange rate from SAR to XYZ?

[User Query]: What is the exchange rate from SAR to XYZ?
============================================================

--- [Step 1] ---
Thought: The user is requesting an exchange rate between SAR and a currency that is not supported.
Action: get_exchange_rate(SAR, XYZ)
[Observation] Error: Target currency 'XYZ' is invalid or not supported.

--- [Step 2] ---
Thought: The target currency 'XYZ' is invalid. I need to inform the user about this error.
Final Answer: Target currency 'XYZ' is invalid or not supported.

[Success] Task Completed Successfully.
```

The agent used the exchange-rate tool, received an error for the unsupported currency, and returned the error instead of generating an exchange rate.

### Test 5: Unrelated Request

Prompt:

```text
What is the capital of Saudi Arabia?
```

Output:

```text
[You]: What is the capital of Saudi Arabia?

[User Query]: What is the capital of Saudi Arabia?
============================================================

--- [Step 1] ---
Thought: The user has asked a question unrelated to currency exchange and conversion.
Final Answer: This request is outside my task. I can only help with currency exchange rates and conversions.

[Success] Task Completed Successfully.
```

The agent recognized that the request was outside its assigned task and completed the interaction without using any tool.

## Conclusion

Day 3 extended the agent with a second tool and conversation memory.

The agent can now retrieve exchange rates, perform currency conversion calculations, and use previous conversation context to understand follow-up requests. Testing also showed the importance of storing clear information in memory so the agent can distinguish between exchange rates and converted results.