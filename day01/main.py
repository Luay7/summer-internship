from pathlib import Path
import ollama
from fpdf import FPDF

# --- 01 ---
print("\n--- 1: Get text from user ---")
text = input("Enter text to summarize: ")
print("Text received successfully.")
# --- -- ---

# --- 02 ---
print("\n--- 2: Determine output format ---")

while True:
    output_format = input("Enter output format (text or pdf) or type (exit) to quit: ")
    
    if output_format == "exit":
        print("Exiting the program.")
        exit()
        
    if output_format == "text" or output_format == "pdf":
        break
    else:
        print("Error: Invalid format. Please try again or type (exit).")
print(f"Format selected successfully. Your choice is: {output_format}")
# --- -- ---

# --- 03 ---
print("\n--- 3: Append prompt to text ---")

prompt_instruction = f"""
Role: Expert Information Architect and Professional Summarizer.
Task: Analyze the provided document and generate a high-density, clear summary.
Context: The user needs to understand the core messages and key takeaways of the text quickly without missing critical data.
Format: Use clean, organized bullet points for the main points.
Constraints: 
- Rely strictly on the provided text.
- Start directly with the explanation or bullet points, with absolutely no introductory filler (e.g., do NOT say "Here is the summary").
- Maintain an objective and professional tone.

Document Content:
{text}
"""
print("Process successful. Text is ready to be sent to the model.")
# --- -- ---

# --- 04 ---
print("\n--- 4: Send prompt and text to the model for summarization ---")

response = ollama.generate(
    model="gemma3:1b",
    prompt=prompt_instruction
)

summary_result = response["response"]
print("Process successful (Summary received from the model).")
# --- -- ---

# --- 05 ---
print("\n--- 5: Save output to file ---")

if output_format == "text":
    # Define the output text file path
    output_file = Path("summary.txt")
    
    output_file.write_text(summary_result)
    print(f"Success! Summary saved as a text file at: {output_file.name}")
elif output_format == "pdf":
    output_file = "summary.pdf"
    
    clean_summary = summary_result.replace('–', '-').replace('—', '-').replace('“', '"').replace('”', '"')
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text=clean_summary)
    pdf.output(output_file)
    print(f"Success! Summary saved as an A4 PDF file at: {output_file}")
print("File saved and program completed successfully.")
# --- -- ---