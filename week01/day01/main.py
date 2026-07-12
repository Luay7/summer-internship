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

# 3. Send the request
response = client.models.generate_content(
    model='gemini-2.5-flash-lite',
    contents='This is my first CLI API test. Confirm it is working. Use 10 words or fewer.'
)

# 4. Print the result
print(response.text)
