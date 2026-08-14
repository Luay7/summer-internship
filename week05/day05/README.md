# Day 05: Failure Modes & Guardrails

## Learning Objective

The goal of Day 5 of Week 5 was to identify possible failure scenarios in the existing agent and improve how it handles requests that cannot be completed normally.

## Failure Modes & Guardrails

A failure mode is a situation where the agent cannot continue the normal workflow correctly.

A guardrail defines how the agent should respond to that situation instead of producing an incorrect result.

For this agent, I focused on three failure scenarios:

1. A request outside the agent's assigned task.
2. An invalid or unsupported currency code.
3. A failure in the external exchange-rate API.

## Agent Guardrails

### 1. Out-of-Scope Requests

The agent is designed only for currency exchange rates and currency conversions.

If the user asks for something outside this task, the agent should identify that the request is unrelated and return a clear message without using any tool.

Example request:

```text
What is the capital of Saudi Arabia?
```

Expected behavior:

```text
Thought: The request is outside the assigned currency task.
Final Answer: This request is outside my task. I can only help with currency exchange rates and conversions.
```

This prevents the agent from trying to use currency tools for unrelated tasks.

### 2. Invalid Currency Codes

The exchange-rate tool checks whether the requested source and target currencies are supported.

If a currency is invalid, the tool returns an error instead of an exchange rate.

The existing tool handles this using:

```python
rate = data["rates"].get(to_curr)

if rate is not None:
    return str(rate)

return f"Error: Target currency '{to_curr}' is invalid or not supported."
```

Example request:

```text
Convert 250 SAR to XYZ
```

The tool returns:

```text
[Observation] Error: Target currency 'XYZ' is invalid or not supported.
```

The agent should stop the dependent conversion steps and explain that the currency is invalid instead of generating a value.

### 3. Exchange-Rate API Failure

The agent depends on an external API to retrieve current exchange rates.

The tool uses a timeout and exception handling:

```python
response = requests.get(url, timeout=10)
response.raise_for_status()
```

If the service cannot be reached, the tool returns an error:

```python
except requests.RequestException as e:
    return f"Error: Failed to connect to the exchange-rate service - {e}"
```

The agent should stop the remaining conversion steps when this error occurs and inform the user that the exchange-rate service is unavailable.

## Testing

### Test 1: Out-of-Scope Request

```text
[User Query]: What is the capital of Saudi Arabia?
============================================================

--- [Step 1: Planning & Decomposition] ---
Plan:
1. The request asks for a factual answer, not a currency exchange. This request falls outside the agent's assigned task.
```

The planning stage correctly identified that the request was outside the currency exchange and conversion task.

### Test 2: Invalid Currency

```text
[User Query]: Convert 250 SAR to XYZ
============================================================

--- [Step 1: Planning & Decomposition] ---
Plan:
1. Get the exchange rate from SAR to XYZ.
2. Calculate the converted amount in XYZ.

--- [Step 2] ---
Thought: The user wants to convert 250 SAR to an unknown currency, XYZ. I need to first get the current exchange rate between SAR and XYZ.
Action: get_exchange_rate(SAR, XYZ)
[Observation] Error: Target currency 'XYZ' is invalid or not supported.
```

The exchange-rate tool correctly detected that `XYZ` was not a supported target currency and returned an error instead of an exchange rate.

### Test 3: Exchange-Rate API Failure

The API failure was tested by running the agent while the exchange-rate service could not be reached.

```text
--- [Step 2] ---
Thought: I need to get the current exchange rate from SAR to USD.
Action: get_exchange_rate(SAR, USD)
[Observation] Error: Failed to connect to the exchange-rate service - HTTPSConnectionPool(...)
```

The tool detected the connection failure and returned an error instead of generating an exchange rate.

## Conclusion

Day 5 focused on failure modes and guardrails for the existing currency agent.

The selected guardrails cover requests outside the agent's task, invalid currency codes, and failures in the external exchange-rate service.

These checks help prevent the agent from producing unsupported currency results when the requested task cannot be completed normally.
