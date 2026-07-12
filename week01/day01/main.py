import os
from dotenv import load_dotenv
from google import genai

# Part 1: Setup and Initialization
load_dotenv() 
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: API Key missing. Check .env file.")
    exit(1)

client = genai.Client(api_key=api_key)

prompt_1 = "Explain Saudi Arabia in 10 words or less."
prompt_2 = "What is its capital?"

print("Starting Context Memory Tests...\n")

# Part 2: No Context (Stateless)
print("--- TEST 1: NO CONTEXT (Stateless API) ---")
response_1_stateless = client.models.generate_content(
    model='gemini-2.5-flash-lite', 
    contents=prompt_1
)
print(f"User: {prompt_1}")
print(f"Gemini: {response_1_stateless.text.strip()}\n")

response_2_stateless = client.models.generate_content(
    model='gemini-2.5-flash-lite', 
    contents=prompt_2
)
print(f"User: {prompt_2}")
print(f"Gemini (Fails to link 'its'): {response_2_stateless.text.strip()}\n")


# Part 3: With Context (Stateful Chat Session)
print("--- TEST 2: WITH CONTEXT (Stateful Chat) ---")
chat = client.chats.create(model="gemini-2.5-flash-lite")

response_1_stateful = chat.send_message(prompt_1)
print(f"User: {prompt_1}")
print(f"Gemini: {response_1_stateful.text.strip()}\n")

response_2_stateful = chat.send_message(prompt_2)
print(f"User: {prompt_2}")
print(f"Gemini (Remembers context): {response_2_stateful.text.strip()}\n")
