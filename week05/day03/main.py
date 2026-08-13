import re
import ollama
import requests

# 1. Environment & Local Model Setup
MODEL_NAME = "gemma3:4b"

# 2. Tools Definition (Multi-Tool for Day 3)
def get_exchange_rate(from_curr: str, to_curr: str) -> str:
    """Fetches the current exchange rate between two currencies using an external API."""
    from_curr = from_curr.strip().upper()
    to_curr = to_curr.strip().upper()
    
    url = f"https://open.er-api.com/v6/latest/{from_curr}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("result") != "success":
            return f"Error: Source currency '{from_curr}' is invalid or not supported."
        
        rate = data["rates"].get(to_curr)
        
        if rate is not None:
            return str(rate)
        return f"Error: Target currency '{to_curr}' is invalid or not supported."
            
    except requests.RequestException as e:
        return f"Error: Failed to connect to the exchange-rate service - {e}"
    except Exception as e:
        return f"Error: Failed to fetch current rate - {e}"

def calculator(expression: str) -> str:
    """Evaluates a mathematical expression."""
    try:
        clean_expr = expression.strip().replace(" ", "")
        result = eval(clean_expr)
        return str(result)
    except Exception as e:
        return f"Math Error: {e}"

TOOLS = {
    "get_exchange_rate": get_exchange_rate,
    "calculator": calculator
}

# 3. Local Ollama Model Communication
def call_ollama(system_prompt: str, prompt_history: str) -> str:
    """Sends the system prompt and conversation history to the local Ollama model."""
    try:
        response = ollama.generate(
            model=MODEL_NAME,
            system=system_prompt,
            prompt=prompt_history,
            options={
                "temperature": 0.0,
                "stop": ["Observation:", "\nObservation"]
            }
        )
        return response.get("response", "")
    except Exception as e:
        print(f"\n[Ollama Error]: {e}")
        return ""

# 4. System Prompt & Reasoning Loop
SYSTEM_PROMPT = """You are a currency exchange and conversion AI agent with memory of previous conversations.

Your only task is to provide current exchange rates and convert amounts between currencies.

Available Tools:
1. get_exchange_rate(from_curr, to_curr)
   - Returns the current exchange rate between two currencies.

2. calculator(expression)
   - Performs mathematical calculations required for currency conversion.

TOOL SELECTION:
- Use get_exchange_rate when a current exchange rate is required.
- Use calculator when a mathematical calculation is required.
- A currency conversion may require both tools in sequence.
- Do not calculate the conversion yourself. Use the calculator tool.

MEMORY RULES:
- Use previous conversation context when a new request depends on earlier information.
- Previous amounts, currencies, exchange rates, and results may be used to understand the new request.
- If the user changes only the amount, keep the previous source and target currencies.
- Reuse a previous exchange rate only if it is clearly stored in the form "1 CURRENCY = RATE CURRENCY".
- Never treat a previous converted amount as an exchange rate.
- If the required exchange rate is not clearly available in memory, use get_exchange_rate again.

ACTION FORMAT RULES:
- Always use positional arguments only.
- Never use parameter names such as from_curr=, to_curr=, or expression=.
- Never put the calculator expression inside quotes.
- For get_exchange_rate, use this format:
  Action: get_exchange_rate(CURRENCY_1, CURRENCY_2)
- For calculator, use this format:
  Action: calculator(number * number)
- Always use the exact amount provided in the current user request.
- Use the exchange rate from the latest relevant Observation.
- Never copy amounts or exchange rates from the system prompt.

CONVERSION RULES:
- Identify and remember the exact amount from the user's current request.
- First obtain the required exchange rate if it is not already clearly available in memory.
- After receiving the exchange rate, multiply the exact requested amount by that exchange rate using the calculator tool.
- Before calling calculator, verify that the amount matches the user's current request.
- Never use a previous converted result as the exchange rate.

FORMAT - Tool required:

Thought: Briefly explain what needs to be done next.
Action: tool_name(arguments)

After receiving an Observation, decide whether another tool is required or whether the task is complete.

FORMAT - Completed conversion:

Thought: Briefly explain that the required result is available.
Final Answer: Using 1 SOURCE = RATE TARGET, AMOUNT SOURCE = RESULT TARGET.

FORMAT - Exchange rate only:

Thought: Briefly explain that the exchange rate is available.
Final Answer: 1 SOURCE = RATE TARGET.

FORMAT - Unrelated request:

Thought: Briefly explain that the request is outside the currency exchange and conversion task.
Final Answer: This request is outside my task. I can only help with currency exchange rates and conversions.

RULES:
- Always begin with "Thought:".
- Use tools only for currency exchange and conversion requests.
- Never use tools for unrelated requests.
- Do not write an Action for unrelated requests.
- Do not invent an Observation.
- Write only one Action per response.
- Continue until all required information and calculations are complete.
- Always include the source currency, target currency, exchange rate, original amount, and converted result in the Final Answer for a conversion.

ERROR HANDLING:
- If the source currency is invalid or unsupported, explain that the source currency code is not valid or supported.
- If the target currency is invalid or unsupported, explain that the target currency code is not valid or supported.
- If the exchange-rate service fails or cannot be reached, explain that the service is currently unavailable or encountered an error.
- If the calculator returns an error, explain that the calculation could not be completed.
- Never invent an exchange rate or calculation result when a tool returns an error.
- Do not retry the same failed tool call unless new information is provided.
"""

def run_agent(user_query: str, chat_memory: str) -> str:
    print(f"\n[User Query]: {user_query}\n" + "="*60)
    
    prompt_history = chat_memory + f"User: {user_query}\n"
    max_steps = 6
    
    for step in range(1, max_steps + 1):
        print(f"\n--- [Step {step}] ---")
        
        response = call_ollama(SYSTEM_PROMPT, prompt_history)
        
        if not response.strip():
            print("[Warning] Model output was empty.")
            break
            
        print(response.strip())
        
        # 1. Check for Final Answer
        if "Final Answer:" in response:
            print("\n[Success] Task Completed Successfully.")
            final_text = response.split("Final Answer:")[-1].strip()
            return final_text
        
        # 2. Parse Action
        action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response)
        
        if action_match:
            tool_name = action_match.group(1).strip()
            raw_args = action_match.group(2).strip()
            args = [arg.strip().strip("'\"") for arg in raw_args.split(",") if arg.strip()]
            
            clean_resp = response.split("Action:")[0] + f"Action: {tool_name}({', '.join(args)})"
            prompt_history += clean_resp + "\n"
            
            # Execute python tool
            if tool_name in TOOLS:
                try:
                    result = TOOLS[tool_name](*args)
                    
                    if tool_name == "get_exchange_rate" and not result.startswith("Error:"):
                        observation = f"1 {args[0]} = {result} {args[1]}"
                    else:
                        observation = result
                except TypeError:
                    observation = "Error: Invalid arguments were provided to the tool."
            else:
                observation = f"Error: Tool '{tool_name}' does not exist."
            
            obs_text = f"Observation: {observation}"
            print(f"[Observation] {observation}")
            prompt_history += f"{obs_text}\n"
            
        else:
            print("\n[Error] Neither Action nor Final Answer pattern was detected.")
            break
    
    return ""

# 5. Execution (Interactive Loop with Memory)
if __name__ == "__main__":
    print("Agent started. Type 'exit' to quit.")
    
    global_memory = ""
    
    while True:
        user_input = input("\n[You]: ")
        
        if not user_input.strip():
            continue
        
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        final_answer = run_agent(user_input, global_memory)
        
        if final_answer:
            global_memory += f"User: {user_input}\nAgent: {final_answer}\n"
