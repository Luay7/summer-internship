import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Store prompts in a list instead of separate variables
prompts = [
    "Explain prompt engineering. Write your answer in approximately 120 words",
    "Explain prompt engineering in detail, including its steps and the requirements needed to write an excellent prompt. Write your answer in approximately 120 words",
    "I am a student currently doing a summer internship in Artificial Intelligence. Act as an expert instructor and explain prompt engineering to me in an organized and understandable way. Clarify its requirements, the steps to follow, and how to get the best possible output from a prompt. Write your answer in approximately 120 words",
    "Act as an experienced Prompt Engineer. Explain prompt engineering in a creative, organized, and sequential manner, using clear examples to illustrate your points. Write your answer in approximately 120 words",
    "Role: Expert Prompt Engineer. Task: Explain prompt engineering in an organized and sequential manner with clear examples. Constraints:\n- Keep the entire response strictly under 120 words.\n- Use bullet points for readability.\n- Start directly with the explanation without any introductory or greeting filler."
]

print("--- PROMPT ENGINEERING PROGRESSION TEST ---")

# Use a loop to iterate through the prompts
for index, prompt in enumerate(prompts, start=1):
    response = client.models.generate_content(
        model='gemini-3.5-flash', 
        contents=prompt
    )
    print(f"Q{index}: {response.text.strip()}\n")
    print("-" * 50)
