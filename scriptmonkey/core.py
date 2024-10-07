import sys
import traceback
from .openai_client import chatgpt_json, chatgpt, ScriptMonkeyResponse, ProjectStructureResponse, ProjectFile, default_prompts
from .openai_client.prompting import load_prompt
from .file_handler import read_file, write_file
import platform
import tempfile
import subprocess
import threading
import itertools
import time
from pprint import pprint
import os
import platform

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


# - - - - - API KEY MANAGEMENT - - - - -

def save_api_key(api_key: str):
    """Save the OpenAI API key to the configuration file and environment variable."""
    with open(CONFIG_FILE, 'w') as file:
        file.write(api_key)
    os.environ['OPENAI_API_KEY'] = api_key
    print(f"✅ OpenAI API key saved to {CONFIG_FILE}.")

def get_openai_api_key() -> str:
    """Retrieve the OpenAI API key from environment or configuration file."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # Check for API key in the configuration file
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                api_key = file.read().strip()

    # Prompt user for API key if not found
    if not api_key:
        print("🐒 ScriptMonkey requires an OpenAI API key to function.")
        api_key = getpass.getpass("Please enter your OpenAI API key (input hidden): ")
        
        if api_key:
            save_api_key(api_key)
    
    if not api_key:
        print("❌ No API key provided. Exiting ScriptMonkey.")
        sys.exit(1)
    
    return api_key

def update_api_key():
    """Prompt the user to update the OpenAI API key."""
    api_key = getpass.getpass("Enter the new OpenAI API key (input hidden): ")
    if api_key:
        save_api_key(api_key)
        print("✅ OpenAI API key updated successfully.")
    else:
        print("❌ No API key provided. The API key was not updated.")

# - - - - - NEW FEATURES - - - - -

def get_multiline_input_with_editor() -> str:
    """
    Opens the user's default text editor for entering multi-line input.
    The user is provided with instructions within the temporary file,
    adjusted based on the detected editor.
    """
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        # Detect the editor from the environment or default based on the OS
        editor = os.environ.get('EDITOR')

        # If no editor is set, choose a default based on the platform
        if not editor:
            if platform.system() == 'Windows':
                editor = 'notepad'
            else:
                editor = 'nano'  # Default for Unix-like systems

        # Adjust instructions based on the detected editor
        if 'vim' in editor.lower():
            instructions = (
                "!# 🐒 Welcome to ScriptMonkey's project generator!\n"
                "!# Please describe your project in detail below.\n"
                "!# Use 'i' to start editing, and when you're done, press 'Esc',\n"
                "!# type ':wq' to save and exit.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        elif 'nano' in editor.lower():
            instructions = (
                "!# 🐒 Welcome to ScriptMonkey's project generator!\n"
                "!# Please describe your project in detail below.\n"
                "!# When you're done, press 'Ctrl+O' to save and 'Ctrl+X' to exit.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        elif 'notepad' in editor.lower():
            instructions = (
                "!# 🐒 Welcome to ScriptMonkey's project generator!\n"
                "!# Please describe your project in detail below.\n"
                "!# When you're done, save and close the Notepad window.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        elif 'code' in editor.lower():
            instructions = (
                "!# 🐒 Welcome to ScriptMonkey's project generator!\n"
                "!# Please describe your project in detail below.\n"
                "!# When you're done, save the file and close the editor window.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        else:
            instructions = (
                "!# 🐒 Welcome to ScriptMonkey's project generator!\n"
                "!# Please describe your project in detail below.\n"
                "!# Save and close the editor when you're done.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )

        # Write the instructions to the temporary file
        temp_file.write(instructions.encode('utf-8'))
        temp_file.flush()

        # Open the temporary file in the detected editor
        subprocess.call([editor, temp_file.name])

        # Read the user's input, ignoring lines starting with '!#'
        temp_file.seek(0)
        user_input = temp_file.read().decode('utf-8')
        user_input = "\n".join(line for line in user_input.splitlines() if not line.startswith("!#"))

    return user_input.strip()

def generate_project_structure(description: str) -> ProjectStructureResponse:
    """Generates the project structure based on the user's project description using OpenAI."""
    instructions = (
        "Generate a detailed project structure for a multi-level application. The project will be placed directly inside a folder named 'generated_project'."
        "\n- Do NOT include 'generated_project/' as part of the paths. All paths should be relative to the root of the project directory, meaning they should start directly with the file or folder names as if they are inside 'generated_project'."
        "\n- Provide a list of directories and files with their full relative paths."
        "\n- Each directory should end with a '/' to indicate that it is a folder."
        "\n- For each file or directory, include a 'description' that explains its purpose."
        "\n- If the file is a Python code file, also include a 'functions' list. For each function, include:"
        "\n  - 'function_name': The name of the function."
        "\n  - 'description': A description of what the function does."
        "\n  - 'inputs': A list of the function's expected inputs, including data types."
        "\n  - 'outputs': A list of the function's expected outputs, including data types."
        "\n- Do not include any extra explanations, commentary, or introductory text. Only provide the structured data as requested."
    )

    # Call the chatgpt_json function to get structured project plan
    project_structure = chatgpt_json(
        instructions=instructions, 
        content=description, 
        response_format=ProjectStructureResponse
    )
    
    return project_structure

def create_project_structure(project_structure_response: dict, base_directory: str = "./generated_project"):
    """Creates the directories and files for the project and generates code content for code files."""
    for project_file in project_structure_response['files']:
        file_path = os.path.join(base_directory, project_file['path'].lstrip('/'))

        # Check if it's a directory or file (directories end with '/')
        if file_path.endswith('/'):
            os.makedirs(file_path, exist_ok=True)
            print(f"🐒 ScriptMonkey created directory: {file_path}")
        else:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # If it's a Python code file, generate code and write to the file
            if file_path.endswith('.py'):
                generated_code = generate_code_for_file(project_file)
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        f.write(generated_code)
                    print(f"🐒 ScriptMonkey created file with generated code at: '{file_path}'.")
                else:
                    print(f"File already exists, skipping: {file_path}")
            else:
                # Create other file types (HTML, CSS, etc.)
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        pass  # Create an empty file for non-code files
                    print(f"🐒 ScriptMonkey reated file: {file_path}")
                else:
                    print(f"File already exists, skipping: {file_path}")


def generate_code_for_file(file_description: dict) -> str:
    """Generates code content for a given file based on its description using the chatgpt() function."""
    # Prepare instructions for OpenAI to generate code based on the file description
    instructions = (
        "Write the complete Python code based on the following file description without adding any additional commentary or explanation. "
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
    
    # Strip out any unintended extra explanations that might still slip through
    if "```python" in generated_code:
        generated_code = generated_code.split("```python")[1].split("```")[0].strip()
    
    return generated_code

def generate_readme(description: str, project_structure: dict) -> str:
    """Generates a README.md content based on the project description and structure."""
    instructions = (
        "Write a complete README.md file based on the following project details. "
        "The README should include the project overview, installation instructions, usage guide, file structure summary, key features, and configuration details. "
        "Make sure the README is well-structured and formatted using Markdown without wrapping the entire README in backticks or any other non-readme commentary."
        "Do not include any commentary, explanations, or text outside of the README content."
        f"\n\nProject Description: {description}\n"
        f"\nProject Structure: {project_structure}\n"
    )

    readme_content = chatgpt(prompt=instructions)
    readme_content = readme_content.strip("```markdown").strip("```")
    return readme_content


# Example usage
def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--set-api-key':
        update_api_key()
    else:
        print(f"\n- - 🐒 WELCOME TO SCRIPT MONKEY 🐒 - - -\n")
        print(f"Opening prompt editor... ")
        time.sleep(2)

        # Step 1: Get multi-line project description from user
        project_description = get_multiline_input_with_editor()
        if not project_description:
            print(f"\nNo Project Description Provided (Tip: Did you save before closing the editor?).\n🐒 Quitting ScriptMonkey...")
            exit()
        print(f"Project Description: {project_description}")

        # Step 2: Generate the project structure using OpenAI API
        project_structure = generate_project_structure(project_description)
        print(f"\n🐒 ScriptMonkey created a project blueprint:")
        pprint(project_structure)

        # Step 3: Create the project structure (directories and files) on the filesystem
        print(f"\n🐒 ScriptMonkey is coding...")
        create_project_structure(project_structure)
        print("\nProject structure creation complete.")

        # Step 4: Generate the README.md content based on the project description and structure
        readme_content = generate_readme(project_description, project_structure)
        readme_path = "./generated_project/README.md"
        with open(readme_path, 'w') as readme_file:
            readme_file.write(readme_content)
        print(f"🐒 ScriptMonkey wrote a README.md file at: '{readme_path}'")