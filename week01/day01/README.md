# Day 01: Dev Environment & First API Call

## Task 1: Environment Setup
In this first task, I successfully set up the core development environment. This included:
* Installing and configuring **Visual Studio Code**, **Git**, and **Python**.
* Connecting Git and VS Code to my GitHub account.
* Creating an isolated Python virtual environment (`venv`) to keep project dependencies separate from my local system.
* Securing my credentials using a `.env` file and `.gitignore`.

## Task 2: First Successful API Request
I obtained a Gemini API key from Google AI Studio and wrote a Python script to interact with the model directly from the terminal. 

This initial script represents my very first successful API request using the CLI, confirming that the environment, API key, and tools are properly configured and working perfectly.

## Task 3: API Parameters Exploration
To build upon the first test, I updated the script to include specific API configuration parameters without changing the core task.
* **`temperature` (e.g., 0.7):** Controls the creativity of the response.
* **`max_output_tokens` (e.g., 30):** Specifies the maximum number of tokens (words or word pieces) the model can generate. Pre-setting this limit helps preserve token quotas and prevents them from running out quickly. In my test, the API forcibly cut off the output mid-sentence. While this resulted in incomplete text, the main educational goal was successfully achieved: demonstrating how to practically control token usage and limit the output.

## Task 4: The Memory Challenge (Stateless vs. Stateful)
A key part of understanding how LLM APIs work is understanding context memory.

* **The Challenge (Stateless):** The standard `generate_content` method treats every request as a brand-new interaction. When I asked about Saudi Arabia and then followed up with "What is its capital?", the model couldn't answer correctly because it forgot the first question.
* **The Solution (Stateful):** To solve this memory issue, I switched to using a chat session (`client.chats.create` and `chat.send_message`). This creates a **stateful** interaction where the API remembers the conversation history, allowing it to correctly answer "Riyadh" to the follow-up question.
