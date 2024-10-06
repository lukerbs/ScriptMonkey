import sys
import traceback
from .openai_client import chatgpt_json, chatgpt, ScriptMonkeyResponse, ProjectStructureResponse, ProjectFile, default_prompts
from .openai_client.prompting import load_prompt
from .file_handler import read_file, write_file
import platform
import threading
import itertools
import time
from pprint import pprint
import os


def get_platform():
    os_name = platform.system()
    os_version = platform.release()
    return f"# Operating System: {os_name}, Version: {os_version}\n\n"


class Spinner:
    def __init__(self, message="Processing"):
        self.spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        self.stop_running = threading.Event()
        self.spin_thread = None
        self.message = message

    def spin(self):
        while not self.stop_running.is_set():
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        self.spin_thread = threading.Thread(target=self.spin)
        self.spin_thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_running.set()
        self.spin_thread.join()


def codemonkey_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    print(f"\n🐒 ScriptMonkey Detected an Error:")
    print(error_message, "\n")

    frame = traceback.extract_tb(exc_traceback)[-1]
    file_path = frame.filename

    original_code = read_file(file_path)
    content = f"{get_platform()}# Original Code:\n```\n{original_code}\n```\n\n# Error Message:\n{error_message}"

    solution = None
    with Spinner("🐒 ScriptMonkey is working on a solution"):
        solution = chatgpt_json(
            instructions=default_prompts.fix_error, content=content, response_format=ScriptMonkeyResponse
        )

    print(f"\n🐒 ScriptMonkey Fixed It:\nProblem:\n{solution['problem']}\n")
    print(f"Suggested Solution:\n{solution['solution']}\n")

    corrected_code = solution["corrected_code"].replace("```python", "").replace("```", "")
    write_file(file_path, corrected_code)
    print(f"🐒 ScriptMonkey automatically fixed your code at: '{file_path}'.")


def run():
    sys.excepthook = codemonkey_exception_handler

# - - - - - NEW FEATURES - - - - -

def generate_project_structure(description: str) -> ProjectStructureResponse:
    """Generates the project structure based on the user's project description using OpenAI."""
    instructions = (
        "Generate a detailed project structure for a multi-level application. The response should include:"
        "\n- A list of directories and files with full paths."
        "\n- Descriptions of each file and directory."
        "\n- If the file is a code file, list any functions/classes it contains, along with the inputs, outputs, and descriptions."
    )

    # Call the chatgpt_json function to get structured project plan
    project_structure = chatgpt_json(
        instructions=instructions, 
        content=description, 
        response_format=ProjectStructureResponse
    )
    
    return project_structure

def create_project_structure(project_structure_response: dict, base_directory: str = "./generated_project"):
    """Creates the directories and files for the project based on the generated project structure, without overwriting existing ones."""
    for project_file in project_structure_response['files']:  # Access 'files' key in the dictionary
        # Prepend the base directory to avoid writing to root
        file_path = os.path.join(base_directory, project_file['path'].lstrip('/'))  # Remove leading '/' from the path

        # Check if it's a directory or file (directories end with '/')
        if file_path.endswith('/'):
            # Create directory if it doesn't already exist
            os.makedirs(file_path, exist_ok=True)
            print(f"Created directory: {file_path}")
        else:
            # Create an empty file if it doesn't already exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
            if not os.path.exists(file_path):  # Only create file if it doesn't exist
                with open(file_path, 'w') as f:
                    pass  # Create an empty file
                print(f"Created file: {file_path}")
            else:
                print(f"File already exists, skipping: {file_path}")
                

def generate_code_for_file(file_description: dict) -> str:
    """Generates code content for a given file based on its description using the chatgpt() function."""
    # Prepare instructions for OpenAI to generate code based on the file description
    instructions = (
        "Generate well-structured Python code based on the following file description. "
        "Ensure the code follows PEP8 standards, includes type hints, and contains relevant docstrings."
        f"\n\nFile Description: {file_description['description']}"
    )

    # Check if the file has functions to include in the code
    if file_description.get('functions'):
        instructions += "\n\nFunctions:\n"
        for function in file_description['functions']:
            instructions += (
                f"- {function['function_name']}: {function['description']} "
                f"(Inputs: {function['inputs']}, Outputs: {function['outputs']})\n"
            )

    # Call the chatgpt function to generate the code
    generated_code = chatgpt(prompt=instructions)
    
    return generated_code


# Example usage
if __name__ == "__main__":
    project_description = load_prompt(path="./prompts/project_description.txt")  # Adjust path if needed
    print(f"Project Description: {project_description}")

    # Step 2: Generate the project structure using OpenAI API
    project_structure = generate_project_structure(project_description)
    print(f"\nGenerated Project Structure:")
    pprint(project_structure)

    # Step 3: Create the project structure (directories and files) on the filesystem
    create_project_structure(project_structure)
    print("Project structure creation complete.")