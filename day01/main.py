import os
from dotenv import load_dotenv
from google import genai

# Part 1: Setup and Initialization
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt_1 = "Explain prompt engineering. Write your answer in approximately 120 words"
prompt_2 = "Explain prompt engineering in detail, including its steps and requirements using an organized list. Write your answer in approximately 120 words"
prompt_3 = "I am a student currently doing a summer internship in Artificial Intelligence. Explain prompt engineering in detail, including its steps and requirements using an organized list. Write your answer in approximately 120 words"
prompt_4 = "I am a student currently doing a summer internship in Artificial Intelligence. Act as an experienced Prompt Engineer. Explain prompt engineering in a creative, sequential manner with clear examples. Write your answer in approximately 120 words"
prompt_5 = "Role: Expert Prompt Engineer. Context: Summer intern student in AI. Task: Explain prompt engineering sequentially with examples. Format: Clean bullet points. Constraints: Strictly under 120 words, with absolutely no introductory filler."

# Part 2: No Context (Stateless)
print("--- TEST 1: NO CONTEXT ---")

response_1_stateless = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=prompt_1
)
print(f"Q1: {response_1_stateless.text.strip()}")

response_2_stateless = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=prompt_2
)
print(f"Q2: {response_2_stateless.text.strip()}\n")

response_3_stateless = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=prompt_3
)
print(f"Q3: {response_3_stateless.text.strip()}\n")

response_4_stateless = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=prompt_4
)
print(f"Q4: {response_4_stateless.text.strip()}\n")

response_5_stateless = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=prompt_5
)
print(f"Q5: {response_5_stateless.text.strip()}\n")