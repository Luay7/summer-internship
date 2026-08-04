import re
import ollama
import requests

# 1. Environment & Local Model Setup
MODEL_NAME = "gemma3:1b"

# 2. Tools Definition (Single Tool for Day 2)
def get_exchange_rate(from_curr: str, to_curr: str) -> str:
    """Tool 1: Fetches LIVE exchange rate between two currencies using an API."""
    from_curr = from_curr.strip().upper()
    to_curr = to_curr.strip().upper()
    
    url = f"https://open.er-api.com/v6/latest/{from_curr}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("result") == "success":
            rate = data["rates"].get(to_curr)
            if rate:
                return str(rate)
            return f"Error: Target currency '{to_curr}' not found in API response."
        else:
            return f"Error: API returned failure for '{from_curr}'."
            
    except Exception as e:
        return f"Error: Failed to fetch live rate - {e}"

TOOLS = {
    "get_exchange_rate": get_exchange_rate
}

# 3. Ollama API Communication
def call_ollama(system_prompt: str, prompt_history: str) -> str:
    """Sends prompts to Ollama with separated system and user roles."""
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
        print(f"\n[Connection Error]: {e}")
        return ""

# 4. System Prompt & Reasoning Loop
SYSTEM_PROMPT = """You are a strict step-by-step reasoning AI agent.

Available Tools:
1. get_exchange_rate(from_curr, to_curr) -> Returns the current exchange rate between two currencies.

Rules:
- Write ONLY ONE "Thought:" and ONE "Action:" per response.
- DO NOT invent or write "Observation:". You must stop generation immediately after the Action line.
- The Action must be written exactly in this format: Action: get_exchange_rate(CURRENCY_1, CURRENCY_2)
- When you have the required information from the observation, output "Final Answer:" with the direct answer to the user.
"""

def run_agent(user_query: str):
    print(f"\n[User Query]: {user_query}\n" + "="*60)
    
    # User prompt is completely separated from the system prompt
    prompt_history = f"User Question: {user_query}\n"
    max_steps = 6
    
    for step in range(1, max_steps + 1):
        print(f"\n--- [Step {step}] ---")
        
        # Passing system and user prompts separately
        response = call_ollama(SYSTEM_PROMPT, prompt_history)
        
        if not response.strip():
            print("[Warning] Model output was empty.")
            break
            
        print(response.strip())
        
        # 1. Parse Action
        action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response)
        
        if action_match:
            tool_name = action_match.group(1).strip()
            raw_args = action_match.group(2).strip()
            args = [arg.strip().strip("'\"") for arg in raw_args.split(",") if arg.strip()]
            
            clean_resp = response.split("Action:")[0] + f"Action: {tool_name}({', '.join(args)})"
            prompt_history += clean_resp + "\n"
            
            # Execute python tool
            if tool_name in TOOLS:
                observation = TOOLS[tool_name](*args)
            else:
                observation = f"Error: Tool '{tool_name}' does not exist."
                
            obs_text = f"Observation: {observation}"
            print(f"[Observation] {observation}")
            
            prompt_history += f"{obs_text}\n"
            
        # 2. Parse Final Answer
        elif "Final Answer:" in response:
            print("\n[Success] Task Completed Successfully.")
            break
        else:
            print("\n[Error] Neither Action nor Final Answer pattern was detected.")
            break

# 5. Execution
if __name__ == "__main__":
    english_query = "What is the exchange rate from SAR to USD?"
    run_agent(english_query)
