import re
import ollama
import requests

# 1. Environment & Local Model Setup
MODEL_NAME = "gemma3:4b"

# 2. Tools Definition (Single Tool for Day 2)
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

TOOLS = {
    "get_exchange_rate": get_exchange_rate
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
SYSTEM_PROMPT = """You are a currency exchange rate AI agent.

Your only task is to provide current exchange rates between currencies.

Available Tool:
get_exchange_rate(from_curr, to_curr)

You must follow one of these two response formats exactly.

FORMAT 1 - Currency exchange request:

Thought: Briefly explain which exchange rate is needed.
Action: get_exchange_rate(CURRENCY_1, CURRENCY_2)

After receiving the Observation:

Final Answer: 1 CURRENCY_1 = RATE CURRENCY_2

FORMAT 2 - Unrelated request:

Thought: Briefly explain that the request is outside the currency exchange task.
Final Answer: This request is outside my task. I can only help with currency exchange rates.

Rules:
- Always begin with "Thought:".
- Use the tool only for currency exchange rate requests.
- Never use the tool for unrelated requests.
- Do not write an Action for unrelated requests.
- Do not invent an Observation.
- Write only one Action per response.
- After receiving a successful Observation, return a clear Final Answer containing both currency codes and the rate.

ERROR HANDLING:
- If the source currency is invalid or unsupported, explain that the source currency code is not valid or supported.
- If the target currency is invalid or unsupported, explain that the target currency code is not valid or supported.
- If the exchange-rate service fails or cannot be reached, explain that the service is currently unavailable or encountered an error.
- Never invent an exchange rate when the tool returns an error.
- Do not retry the same failed tool call unless new information is provided.
"""

def run_agent(user_query: str):
    print(f"\n[User Query]: {user_query}\n" + "="*60)
    
    prompt_history = f"User Question: {user_query}\n"
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
            break
        
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
                    
                    if not result.startswith("Error:"):
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

# 5. Execution
if __name__ == "__main__":
    english_query = "What is the exchange rate from SAR to USD?"
    run_agent(english_query)
