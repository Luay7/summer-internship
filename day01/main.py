import os
from dotenv import load_dotenv
from google import genai

# Part 1: Setup and Initialization
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt_1 = "Explain Saudi Arabia in 10 words."
prompt_2 = "What is the capital ?"

# Part 2: No Context (Stateless)
print("--- TEST 1: NO CONTEXT ---")

response_1_stateless = client.models.generate_content(
    model='gemini-2.5-flash-lite', 
    contents=prompt_1
)
print(f"Q1: {response_1_stateless.text.strip()}")

response_2_stateless = client.models.generate_content(
    model='gemini-2.5-flash-lite', 
    contents=prompt_2
)
print(f"Q2: {response_2_stateless.text.strip()}\n")

# Part 3: With Context (Chat Session)
print("--- TEST 2: WITH CONTEXT ---")

chat = client.chats.create(model="gemini-2.5-flash-lite")

response_1_stateful = chat.send_message(prompt_1)
print(f"Q1: {response_1_stateful.text.strip()}")

response_2_stateful = chat.send_message(prompt_2)
print(f"Q2: {response_2_stateful.text.strip()}")