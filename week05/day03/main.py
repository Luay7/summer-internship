import re
import ollama
import requests

# 1. Environment & Local Model Setup
MODEL_NAME = "gemma3:1b"

# 2. Tools Definition (Multi-Tool for Day 3)
def get_exchange_rate(from_curr: str, to_curr: str) -> str:
    """Tool 1: Fetches LIVE exchange rate between two currencies."""
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
            return f"Error: Target currency '{to_curr}' not found."
        else:
            return f"Error: API returned failure for '{from_curr}'."
            
    except Exception as e:
        return f"Error: Failed to fetch live rate - {e}"

def calculator(expression: str) -> str:
    """Tool 2: Evaluates mathematical expressions."""
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
SYSTEM_PROMPT = """You are a strict step-by-step reasoning AI agent with memory of previous conversations.

Available Tools:
1. get_exchange_rate(from_curr, to_curr) -> Returns the current exchange rate.
2. calculator(expression) -> Evaluates math expressions.

CRITICAL RULES:
- You MUST ALWAYS write a "Thought:" explaining your reasoning BEFORE writing an "Action:".
- You MUST write "Thought:" on one line, and "Action:" on a NEW line.
- Write ONLY ONE "Thought:" and ONE "Action:" per response.
- DO NOT calculate math yourself. ALWAYS use the calculator tool.
- DO NOT invent or write "Observation:". Stop generation immediately after the Action line.
- The Action must be written exactly in this format: Action: tool_name(arguments)
- When you have the final calculated number, output "Final Answer:" with the direct answer.

FORMATTING EXAMPLE (Multi-step using fictional currencies):
User Question: Convert 500 AAA to ZZZ.
Thought: First, I need to check the current exchange rate between the fictional currency AAA and ZZZ.
Action: get_exchange_rate(AAA, ZZZ)
Observation: 2.5
Thought: Now I need to multiply the amount (500) by the exchange rate (2.5) using the calculator.
Action: calculator(500 * 2.5)
Observation: 1250.0
Thought: I have the final calculated result.
Final Answer: 500 AAA is equal to 1250.0 ZZZ.
"""

def run_agent(user_query: str, chat_memory: str) -> str:
    print("\n" + "="*60)
    
    # We combine the past memory with the new user query
    prompt_history = chat_memory + f"User: {user_query}\n"
    max_steps = 6
    
    for step in range(1, max_steps + 1):
        print(f"\n--- [Step {step}] ---")
        
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
            # Extract and return only the final text to store in memory
            final_text = response.split("Final Answer:")[-1].strip()
            return final_text
        else:
            print("\n[Error] Neither Action nor Final Answer pattern was detected.")
            break
            
    return ""

# 5. Execution (Interactive Loop with Memory)
if __name__ == "__main__":
    print("Agent started. Type 'exit' to quit.")
    
    # This string holds the memory of the conversation
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
            # Add the new interaction to the memory for the next turn
            global_memory += f"User: {user_input}\nAgent: {final_answer}\n"
