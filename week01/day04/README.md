# Local AI Text Summarizer

## Project Overview

This project is a command-line text summarization application powered by a local LLM through Ollama.

The final application will allow the user to enter raw text, select an output format, generate a summary using a local AI model, and save the result as either a TXT or PDF file.

The project is developed gradually through multiple Git commits to clearly demonstrate each stage of the development process.

## Project Objectives

The main objectives of this project are to:

* Build a complete Python command-line application.
* Receive and validate user input.
* Connect Python with a local Ollama model.
* Apply prompt engineering to improve summary quality.
* Print and save generated summaries.
* Support TXT and PDF output formats.
* Package the final application using Docker.
* Document the development process clearly using Git and GitHub.

## Development Stages

### Stage 1: User Input and Output Format Selection

The first stage creates the basic command-line structure of the application.

The program currently:

* Receives raw text from the user.
* Asks the user to select an output format.
* Supports `text` and `pdf` options.
* Validates the selected format.
* Displays an error message when the input is invalid.
* Allows the user to exit the program.

At this stage, the application does not yet generate or save a summary.

### Stage 2: AI Summarization and File Export

The second stage adds the main text summarization functionality.

The program now:

* Creates a structured prompt using Role, Task, Context, Format, and Constraints.
* Combines the predefined prompt with the user's input text.
* Connects to the local Ollama service.
* Uses the `gemma3:1b` model to generate the summary.
* Prints the generated summary in the terminal.
* Saves the summary as either a TXT or PDF file based on the user's selection.

The application uses the `ollama` Python package to communicate with the local model and `fpdf2` to generate PDF files.

## Current Application Workflow

The current version follows these steps:

1. Receive raw text from the user.
2. Ask the user to select TXT or PDF.
3. Validate the selected output format.
4. Combine the user's text with a structured summarization prompt.
5. Send the complete prompt to the local Ollama model.
6. Receive and print the generated summary.
7. Save the summary in the selected file format.
