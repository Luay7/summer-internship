import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Store prompts in a list instead of separate variables
prompts = [
    "Explain prompt engineering. Write your answer in approximately 120 words.",
    "Explain prompt engineering, including its core steps and requirements. Format your answer as an organized list. Write your answer in approximately 120 words.",
    "I am a student currently doing a summer internship in Artificial Intelligence. Explain prompt engineering to me, including its steps and requirements using an organized list. Write your answer in approximately 120 words.",
    "I am a student currently doing a summer internship in Artificial Intelligence. Act as an experienced Prompt Engineer. Explain prompt engineering in a creative, sequential manner and provide a brief example. Write your answer in approximately 120 words.",
    "Role: Expert Prompt Engineer. Context: Summer intern student in AI. Task: Explain prompt engineering sequentially with a brief example. Format: Clean bullet points. Constraints: Strictly under 120 words, with absolutely no introductory filler."
]

print("--- PROMPT ENGINEERING PROGRESSION TEST ---")

# Use a loop to iterate through the prompts
for index, prompt in enumerate(prompts, start=1):
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    print(f"Q{index}: {response.text.strip()}\n")
    print("-" * 50)
