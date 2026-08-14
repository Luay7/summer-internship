import re
import ollama
import requests

# 1. Environment & Local Model Setup
MODEL_NAME = "gemma3:4b"

# 2. Tools Definition (Multi-Tool for Day 4)
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

# 4. Planning & Decomposition Prompt
PLANNING_PROMPT = """You are a currency exchange and conversion planning agent.

Your task is to analyze the user's request and create a clear execution plan.

Available Tools:
1. get_exchange_rate(from_curr, to_curr)
2. calculator(expression)

PLANNING RULES:
- Analyze every user request before execution.
- Break the complete request into the smallest required ordered steps.
- Each exchange-rate lookup must be a separate step.
- Each calculation must be a separate step.
- Do not combine multiple operations into one step.
- A simple request may contain only one step.
- Do not execute any tool.
- Do not write Thought, Action, Observation, or Final Answer.
- Return only the Plan.

For an unrelated request, create one step explaining that the request must be identified as outside the agent's assigned task.

Format:

Plan:
1. First required operation.
2. Second required operation.
3. Continue until all required operations are included.
"""

# 5. System Prompt & Execution Rules
SYSTEM_PROMPT = """You are a currency exchange and conversion AI agent with memory.

Your only task is to provide current exchange rates and convert amounts between currencies.

A Plan has already been created for the current request.
Follow that Plan exactly and execute one unfinished step at a time.

Available Tools:
1. get_exchange_rate(from_curr, to_curr)
   - Returns the current exchange rate between two currencies.

2. calculator(expression)
   - Performs mathematical calculations required for currency conversion.

EXECUTION RULES:
- Follow the existing Plan in order.
- Complete only one unfinished Plan step per response.
- Do not repeat the Plan.
- Do not skip any required step.
- Do not repeat a successfully completed step.
- Use the result of each Observation in later steps when required.
- Complete every required Plan step before returning the Final Answer.

TOOL SELECTION:
- Use get_exchange_rate whenever a current exchange rate is required.
- Use calculator whenever a mathematical calculation is required.
- Never calculate conversion results yourself when the calculator tool is available.
- Use only valid information returned by Observations.

ACTION RULES:
- Every response that requires a tool MUST begin with "Thought:".
- The Thought must briefly explain the current unfinished Plan step.
- After the Thought, write exactly one "Action:".
- Never write an Action without a Thought before it.
- Write only one Action per response.
- If an Action is required, STOP immediately after the Action line.
- Never write Action and Final Answer in the same response.
- Never predict or invent the result of an Action.
- Always wait for the Observation before continuing.
- After receiving an Observation, move to the next unfinished step in the Plan.

ACTION FORMAT:
- Always use positional arguments only.
- Never use parameter names such as from_curr=, to_curr=, or expression=.
- Never place calculator expressions inside quotes.

For exchange-rate lookup:
Action: get_exchange_rate(CURRENCY_1, CURRENCY_2)

For calculations:
Action: calculator(number * number)

CONVERSION RULES:
- Keep track of the original amount and source currency.
- Keep track of every intermediate amount and its correct currency.
- Keep each exchange rate separate from converted amounts.
- Never treat a converted amount as an exchange rate.
- Never label an amount with the wrong currency.
- For chained conversions, preserve the complete conversion sequence.
- Use the exact result of the previous calculation when it is required in the next conversion.

MEMORY RULES:
- Use previous conversation context when a new request depends on earlier information.
- If the user changes only the amount, keep the latest valid currency context.
- Reuse a previous exchange rate only when it is clearly stored as:
  1 CURRENCY = RATE CURRENCY
- Never use a previous converted amount as an exchange rate.
- Do not treat failed or invalid requests as valid conversion context.
- If the required valid exchange rate is not clearly available, use get_exchange_rate again.

UNRELATED REQUESTS:
- If the request is outside currency exchange or conversion, do not use any tool.
- Write:
  Thought: The request is outside the assigned currency task.
  Final Answer: This request is outside my task. I can only help with currency exchange rates and conversions.

ERROR HANDLING:
- If the source currency is invalid or unsupported, stop the dependent steps and explain the error.
- If the target currency is invalid or unsupported, stop the dependent steps and explain the error.
- If the exchange-rate service fails or cannot be reached, stop the dependent steps and explain the error.
- If the calculator returns an error, stop the dependent steps and explain the error.
- Never invent a result when a tool returns an error.
- Do not retry the same failed Action unless new information is provided.

FINAL ANSWER:
- Return the Final Answer only after every required Plan step is complete.
- The Final Answer must not contain an Action.
- For a simple exchange-rate request, clearly show the exchange rate.
- For a conversion, clearly show the original amount and final converted amount.
- For a chained conversion, show the complete conversion sequence with the correct currencies.
- Round displayed converted amounts to a reasonable number of decimal places.

For a chained conversion, use this structure:
Final Answer: ORIGINAL_AMOUNT SOURCE = INTERMEDIATE_AMOUNT CURRENCY = FINAL_AMOUNT TARGET.
"""

# 6. Agent Planning & Execution Loop
def run_agent(user_query: str, chat_memory: str) -> str:
    print(f"\n[User Query]: {user_query}\n" + "="*60)
    
    prompt_history = chat_memory + f"User: {user_query}\n"
    max_steps = 10
    
    # Step 1: Planning & Decomposition
    print("\n--- [Step 1: Planning & Decomposition] ---")
    
    plan_response = call_ollama(PLANNING_PROMPT, prompt_history)
    
    if not plan_response.strip():
        print("[Warning] Model output was empty.")
        return ""
    
    print(plan_response.strip())
    
    if "Plan:" not in plan_response:
        print("[Error] No Plan was generated.")
        return ""
    
    prompt_history += plan_response.strip() + "\n"
    
    # Step 2+: Execute the Plan
    for step in range(2, max_steps + 1):
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
        
        # 2. Check for Final Answer
        elif "Final Answer:" in response:
            print("\n[Success] Task Completed Successfully.")
            final_text = response.split("Final Answer:")[-1].strip()
            return final_text
        
        else:
            print("\n[Error] Neither Action nor Final Answer pattern was detected.")
            break
    
    return ""

# 7. Execution (Interactive Loop with Memory)
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
