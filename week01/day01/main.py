import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load environment variables
load_dotenv() 
api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialize the client
client = genai.Client(api_key=api_key)

print("Sending request...\n")

# 3. Send the request with Temperature and Max Tokens configured
response = client.models.generate_content(
    model='gemini-2.5-flash-lite',
    contents='This is my CLI API test. Confirm it is working and give me a welcome message.',
    config=types.GenerateContentConfig(
        temperature=0.8,         # Higher value = more creative/random
        max_output_tokens=30     # Strict limit on response length
    )
)

# 4. Print the result
print(response.text)
