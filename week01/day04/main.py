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

print("\nInput and output format setup completed successfully.")
