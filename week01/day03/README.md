# Day 03: The AI Dev Toolchain

## Today's Goal
The goal of today's task was purely theoretical: to deeply solidify and understand the core concepts applied during the first two days of the training. By learning how the tools operate behind the scenes, building AI applications becomes much clearer and more professional.

## Task 1: Exploring the Development Tools
I researched and studied the core tools that make up the AI development environment:
* IDE (Integrated Development Environment): A program used to write, run, and debug code efficiently.
* CLI (Command Line Interface): A text-based interface used to execute commands directly in the terminal instead of using a graphical interface.
* API (Application Programming Interface): The bridge that connects different applications and systems, allowing them to communicate and share data seamlessly.

## Task 2: Mapping the AI Data Flow
I mapped out the complete 6-stage workflow of how a prompt travels from the user until the final output is generated and displayed. The steps are:
1. Sends Prompt: The user types a question or instruction into the application.
2. API Request: The application packages the prompt and sends it through the API.
3. Forwards Prompt: The API carries the prompt over the internet to the LLM Server.
4. Generates & Returns Response: The LLM Server processes the prompt, creates the answer, and sends it back to the API.
5. Delivers Data Back: The API takes the answer from the server and delivers it back to the application.
6. Displays Output to User: The application receives the final answer and shows it nicely on the screen.

## Task 3: Workflow Diagram & Overcoming Challenges
To document this data flow, I created a visual diagram which is uploaded in this folder as `Day03.pdf`. 

Challenges Solved:
* Understanding Code Integration: It was initially difficult to understand how the data flow works when putting AI into real code instead of just using a ready-made website like ChatGPT.
* How I Solved It: I broke down the data flow into a simple step-by-step diagram and reviewed practical Python script examples to see exactly how these connections operate programmatically.
