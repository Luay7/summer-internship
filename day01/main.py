import os
from dotenv import load_dotenv
from google import genai

# Part 1: Setup and Initialization
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt_1="Explain prompt engineering. Write your answer in approximately 120 words"
prompt_2="Explain prompt engineering in detail, including its steps and the requirements needed to write an excellent prompt. Write your answer in approximately 120 words"
prompt_3="I am a student currently doing a summer internship in Artificial Intelligence. Act as an expert instructor and explain prompt engineering to me in an organized and understandable way. Clarify its requirements, the steps to follow, and how to get the best possible output from a prompt. Write your answer in approximately 120 words"
prompt_4="Act as an experienced Prompt Engineer. Explain prompt engineering in a creative, organized, and sequential manner, using clear examples to illustrate your points. Write your answer in approximately 120 words"
prompt_5="Role: Expert Prompt Engineer. Task: Explain prompt engineering in an organized and sequential manner with clear examples. Constraints:\nKeep the entire response strictly under 120 words.\nUse bullet points for readability.\nStart directly with the explanation without any introductory or greeting filler."

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