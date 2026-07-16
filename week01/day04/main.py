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
    output_format = input(
        "Enter output format (text or pdf) or type (exit) to quit: "
    ).strip().lower()

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
print("\n--- 3: Prepare the summarization prompt ---")

prompt = f"""
Role: Expert Information Architect and Professional Summarizer.

Task: Analyze the provided text and generate a clear, high-density summary.

Context: The user needs to understand the main ideas and key information quickly.

Format: Use clear and organized bullet points.

Constraints:
- Use only information from the provided text.
- Do not add an introduction such as "Here is the summary."
- Maintain an objective and professional tone.

Text:
{text}
"""

print("Prompt prepared successfully.")
# --- -- ---


# --- 04 ---
print("\n--- 4: Generate the summary ---")

response = ollama.generate(
    model="gemma3:1b",
    prompt=prompt
)

summary = response["response"]

print("Summary generated successfully.")

print("\n--- Generated Summary ---")
print(summary)
# --- -- ---


# --- 05 ---
print("\n--- 5: Save the summary ---")

if output_format == "text":
    output_file = Path("summary.txt")
    output_file.write_text(summary, encoding="utf-8")

elif output_format == "pdf":
    output_file = "summary.pdf"

    clean_summary = (
        summary
        .replace("–", "-")
        .replace("—", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("•", "-")
    )

    clean_summary = clean_summary.encode(
        "latin-1",
        errors="replace"
    ).decode("latin-1")

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text=clean_summary)
    pdf.output(output_file)

print(f"Summary saved successfully as: {output_file}")
print("\nProgram completed successfully.")
# --- -- ---
