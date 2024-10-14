import sys
import traceback
from collections import defaultdict
import argparse
from .openai_client import (
    chatgpt_json,
    chatgpt,
    ScriptMonkeyResponse,
    ProjectStructureResponse,
    ProjectFile,
    default_prompts,
)
from .openai_client.prompting import load_prompt
from .file_handler import read_file, write_file, ignored_dirs, important_extensions
import platform
import tempfile
import subprocess
import threading
import itertools
import time
from pprint import pprint
import os
import platform
import pyperclip

import re
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()

CONFIG_FILE = os.path.expanduser("~/.scriptmonkey_config")


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
    with open(CONFIG_FILE, "w") as file:
        file.write(api_key)
    os.environ["OPENAI_API_KEY"] = api_key
    print(f"✅ OpenAI API key saved to {CONFIG_FILE}.")


def get_openai_api_key() -> str:
    """Retrieve the OpenAI API key from environment or configuration file."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # Check for API key in the configuration file
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                api_key = file.read().strip()

    # Prompt user for API key if not found
    if not api_key:
        print("🐒 ScriptMonkey requires an OpenAI API key to function.")
        api_key = input("Please enter your OpenAI API key: ")

        if api_key:
            save_api_key(api_key)

    if not api_key:
        print("❌ No API key provided. Exiting ScriptMonkey.")
        sys.exit(1)

    return api_key


def update_api_key():
    """Prompt the user to update the OpenAI API key."""
    api_key = input("Enter the new OpenAI API key: ")
    if api_key:
        save_api_key(api_key)
        print("✅ OpenAI API key updated successfully.")
    else:
        print("❌ No API key provided. The API key was not updated.")


# - - - - - NEW FEATURES - - - - -


def get_multiline_input_with_editor(mode: str) -> str:
    """
    Opens the user's default text editor for entering multi-line input.
    The user is provided with instructions within the temporary file,
    adjusted based on the detected editor.

    :mode: enums['BUILD', 'ASK']
    """

    if mode == "BUILD":
        purpose = "Project Builder"
        user_prompt = "Please describe your project in detail below."
    elif mode == "ASK":
        purpose = "Prompt Editor"
        user_prompt = "Please write your question down below."

    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        # Detect the editor from the environment or default based on the OS
        editor = os.environ.get("EDITOR")

        # If no editor is set, choose a default based on the platform
        if not editor:
            if platform.system() == "Windows":
                editor = "notepad"
            else:
                editor = "nano"  # Default for Unix-like systems

        # Adjust instructions based on the detected editor
        if "vim" in editor.lower():
            instructions = (
                f"!# 🐒 Welcome to ScriptMonkey's {purpose}!\n"
                f"!# {user_prompt}\n"
                "!# Use 'i' to start editing, and when you're done, press 'Esc',\n"
                "!# type ':wq' to save and exit.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        elif "nano" in editor.lower():
            instructions = (
                f"!# 🐒 Welcome to ScriptMonkey's {purpose}!\n"
                f"!# {user_prompt}\n"
                "!# When you're done, press 'Ctrl+O' to save and 'Ctrl+X' to exit.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        elif "notepad" in editor.lower():
            instructions = (
                f"!# 🐒 Welcome to ScriptMonkey's {purpose}!\n"
                f"!# {user_prompt}\n"
                "!# When you're done, save and close the Notepad window.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        elif "code" in editor.lower():
            instructions = (
                f"!# 🐒 Welcome to ScriptMonkey's {purpose}!\n"
                f"!# {user_prompt}\n"
                "!# When you're done, save the file and close the editor window.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )
        else:
            instructions = (
                f"!# 🐒 Welcome to ScriptMonkey's {purpose}!\n"
                f"!# {user_prompt}\n"
                "!# Save and close the editor when you're done.\n"
                "!# (Lines starting with '!#' will be ignored.)\n\n"
            )

        # Write the instructions to the temporary file
        temp_file.write(instructions.encode("utf-8"))
        temp_file.flush()

        # Open the temporary file in the detected editor
        subprocess.call([editor, temp_file.name])

        # Read the user's input, ignoring lines starting with '!#'
        temp_file.seek(0)
        user_input = temp_file.read().decode("utf-8")
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
        instructions=instructions, content=description, response_format=ProjectStructureResponse
    )

    return project_structure


def create_project_structure(
    project_structure_response: dict, project_description: str, base_directory: str = "./generated_project"
):
    """Creates the directories and files for the project and generates code content for all file types."""
    # Extract the list of project files for context
    project_files = project_structure_response["files"]

    # Iterate through each file in the project structure
    for project_file in project_files:
        file_path = os.path.join(base_directory, project_file["path"].lstrip("/"))

        # Check if it's a directory or file (directories end with '/')
        if file_path.endswith("/"):
            os.makedirs(file_path, exist_ok=True)
            print(f"🐒 ScriptMonkey created directory: {file_path}")
        else:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Generate content for all files, including Python, HTML, JSON, CSS, etc.
            generated_content = generate_code_for_file(project_file, project_description, project_files)

            # Write the generated content to the file if it doesn't already exist
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(generated_content)
                print(f"🐒 ScriptMonkey created file with generated content at: '{file_path}'.")
            else:
                print(f"File already exists, skipping: {file_path}")


def gather_project_context(project_description: str, project_files: list) -> str:
    """
    Gathers a summary of the project goal and all existing files with their key functions or classes.

    Args:
        project_description (str): A high-level description of the project's purpose and goals.
        project_files (list): List of project file descriptions.

    Returns:
        str: A summary of the project goal and existing modules, classes, and functions.
    """
    context = f"Project Goal: {project_description}\n\n"
    context += "Project Context:\n"
    for file in project_files:
        if file["functions"]:
            context += f"- In '{file['path']}', the following functions are defined:\n"
            for function in file["functions"]:
                context += f"  - {function['function_name']}: {function['description']} (Inputs: {function['inputs']}, Outputs: {function['outputs']})\n"
        else:
            context += f"- '{file['path']}' is defined with no specific functions listed.\n"
    return context


def generate_code_for_file(file_description: dict, project_description: str, project_files: list) -> str:
    """
    Generates content for a given file based on its description using the chatgpt() function.

    Args:
        file_description (dict): The description of the file for which content is being generated.
        project_description (str): A high-level description of the project's purpose and goals.
        project_files (list): List of all project files for context.

    Returns:
        str: The generated content for the file.
    """
    # Gather context about the project goal and other files
    context = gather_project_context(project_description, project_files)

    # Extract the file extension to inform the content type
    file_extension = os.path.splitext(file_description["path"])[1].lower().strip(".")

    # Dynamically adjust the content type description based on the file extension
    if file_extension:
        content_type_description = f"{file_extension.upper()} file content"
    else:
        content_type_description = "text content"

    # Prepare instructions for OpenAI to generate content based on the file description and type
    instructions = (
        f"Write the complete content for a {content_type_description} that fulfills the following requirements. "
        "Consider the context of the entire project when generating the content and make use of imports where available and appropriate."
        "Use relevant imports, references, and appropriate formatting or structure where necessary. Do not add extra commentary or explanation. "
        "Make sure to return the content directly, without wrapping it in any code fences like triple quotes or backticks."
        f"\n\nFile Description: {file_description['description']}"
        f"\n\n{context}\n"
    )

    # Include functions for code files (if provided)
    if file_description.get("functions"):
        instructions += "\n\nFunctions:\n"
        for function in file_description["functions"]:
            instructions += (
                f"- {function['function_name']}: {function['description']} "
                f"(Inputs: {function['inputs']}, Outputs: {function['outputs']})\n"
            )

    # Call the chatgpt function to generate the content
    generated_content = chatgpt(prompt=instructions)

    # Clean up any unintended code blocks
    if f"```{file_extension}" in generated_content:
        generated_content = generated_content.split(f"```{file_extension}")[1].split("```")[0].strip()

    return generated_content


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


def generate_directory_tree(start_path, prefix="", max_depth=None, current_depth=0, max_files_per_type=5):
    """
    Generates a directory tree as a string with options to limit files of the same type,
    ignore directories, and handle critical code files.
    """
    # If max_depth is defined and the current depth exceeds it, stop recursion
    if max_depth is not None and current_depth > max_depth:
        return ""

    tree = ""
    files = sorted(os.listdir(start_path))

    # Group files by their extensions
    files_by_extension = defaultdict(list)
    for name in files:
        if os.path.isdir(os.path.join(start_path, name)):
            files_by_extension["<dir>"].append(name)
        else:
            _, ext = os.path.splitext(name)
            files_by_extension[ext].append(name)

    # Build a list of files to display
    display_files = []

    # Add directories first
    display_files.extend(sorted(files_by_extension["<dir>"]))

    # Add files, limiting non-important file types
    for ext, ext_files in files_by_extension.items():
        if ext == "<dir>":
            continue
        if ext in important_extensions:
            # Include all files of important types
            display_files.extend(sorted(ext_files))
        else:
            # Limit the number of files to `max_files_per_type` for non-important types
            display_files.extend(sorted(ext_files)[:max_files_per_type])
            if len(ext_files) > max_files_per_type:
                display_files.append(f"... ({len(ext_files) - max_files_per_type} more {ext} files omitted)")

    # Iterate over the files and directories to build the tree
    for index, name in enumerate(display_files):
        path = os.path.join(start_path, name)

        # Skip ignored directories
        if os.path.isdir(path) and name in ignored_dirs:
            continue

        connector = "└── " if index == len(display_files) - 1 else "├── "
        tree += prefix + connector + name + "\n"

        if os.path.isdir(path):
            new_prefix = prefix + ("    " if index == len(display_files) - 1 else "│   ")
            tree += generate_directory_tree(
                path,
                new_prefix,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                max_files_per_type=max_files_per_type,
            )

    return tree


def ask_gpt_with_files(question, file_paths, include_tree=False):
    """
    Constructs a detailed and flexible prompt for ChatGPT using a question and optionally including content from specified files.
    """
    prompt = (
        f"### Question:\n"
        f"{question}\n\n"
        "If I have included any files below, you can use them for additional context for this question. "
        "Please analyze the provided files below (if available) as needed and reference them when forming your answer. "
        "If the answer involves code, please format any code examples using Markdown with properly labeled language-specific code blocks. "
        "Your response should be in Markdown format to preserve readability.\n\n"
    )

    if file_paths:
        prompt += "### Files Provided:\n"
        for path in file_paths:
            try:
                content = read_file(path)
                prompt += (
                    f"## File: {path}\n"
                    f"The content of the file '{path}' is included below. Use this as context for answering the question:\n\n"
                    f"```\n{content}\n```\n\n"
                )
            except FileNotFoundError:
                console.print(f"[bold yellow]Warning: {path} not found. Skipping this file.[/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Error reading {path}: {e}[/bold red]")

    else:
        prompt += (
            "No specific files have been provided, so please base your response solely on the question above. "
            "If the response includes any code examples or technical explanations, please use Markdown formatting with language-specific code blocks for clarity.\n"
        )

    # Include the directory tree if the flag is set
    if include_tree:
        start_directory = os.getcwd()
        tree = generate_directory_tree(start_directory)
        prompt += "### Directory Tree:\n"
        prompt += f"The directory tree of the current working directory is included below (up to a depth of 6 levels):\n\n```\n{tree}\n```\n\n"
        console.print("- - Directory Tree - -")
        console.print(tree)

    # Output the constructed prompt to the console for transparency
    console.rule("🐒 ScriptMonkey is Thinking 🐒")
    console.rule()

    # Use the OpenAI API to get a response
    try:
        response = chatgpt(prompt=prompt)
        # Display the response using rich markdown and detect code blocks
        console.rule("🐒 ANSWER 🐒")
        render_response_with_syntax_highlighting(response)
        console.print("\n")
        console.rule()
    except Exception as e:
        console.print(f"[bold red]Error using OpenAI API: {e}[/bold red]")


def render_response_with_syntax_highlighting(response):
    """
    Render a ChatGPT response with syntax highlighting for detected code blocks.
    """
    # Regular expression to detect code blocks with a specified language (e.g., ```python)
    code_block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    last_pos = 0

    # Iterate over all detected code blocks
    for match in code_block_pattern.finditer(response):
        language = match.group(1) or "text"  # Default to 'text' if no language is specified
        code_content = match.group(2)

        # Print any text before the code block as markdown
        if match.start() > last_pos:
            pre_text = response[last_pos : match.start()]
            console.print(Markdown(pre_text))

        # Print the code block with syntax highlighting
        syntax = Syntax(f"\n{code_content}", language, theme="monokai", line_numbers=False)
        console.print("\n")
        console.print(syntax)
        console.print("\n")

        last_pos = match.end()

    # Print any remaining text after the last code block
    if last_pos < len(response):
        console.print(Markdown(response[last_pos:]))


def copy_files_to_clipboard(file_paths, include_tree=True):
    """
    Reads the content from the specified files and copies it to the clipboard in the specified format.
    Optionally includes a project directory tree.
    """
    formatted_output = "- - - - - - - - - -\nHere are some details about the project.\n\n"

    for path in file_paths:
        try:
            content = read_file(path)
            formatted_output += f"# {path}\n{content}\n\n- - - - - - - - - -\n"
        except FileNotFoundError:
            console.print(f"[bold yellow]Warning: {path} not found. Skipping this file.[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Error reading {path}: {e}[/bold red]")

    # Include the directory tree if requested
    if include_tree:
        start_directory = os.getcwd()
        tree = generate_directory_tree(start_directory)
        formatted_output += "- - - - - - - - - -\n\n# PROJECT TREE\n"
        formatted_output += f"{tree}\n\n"

    # Copy the formatted output to the clipboard
    pyperclip.copy(formatted_output)
    console.print("[green]🐒 Content has been copied to the clipboard.[/green]")


def handle_no_prompt():
    print(f"\nNo Prompt Provided (Tip: Did you save before closing the editor?).\n🐒 Quitting ScriptMonkey...\n")
    exit()


def main():
    parser = argparse.ArgumentParser(description="ScriptMonkey - Generate Python projects and fix code.")
    parser.add_argument("--ask", nargs="?", const=True, help="Ask a question to ChatGPT", type=str)
    parser.add_argument("--files", nargs="*", help="Paths to files to include in the prompt", type=str)
    parser.add_argument("--tree", help="Include a directory tree in the prompt", action="store_true")
    parser.add_argument("--set-api-key", help="Set the OpenAI API key", action="store_true")
    parser.add_argument(
        "--copy", help="Copy the content of the specified files to the clipboard", action="store_true"
    )  # New --copy flag
    args = parser.parse_args()

    print(f"\n- - 🐒 WELCOME TO SCRIPT MONKEY 🐒 - - -\n")

    if args.set_api_key:
        # Handle setting the API key
        update_api_key()
        return

    if args.copy:
        # Handle the --copy functionality
        file_paths = args.files if args.files else []
        if not file_paths:
            console.print("[bold red]❌ No files specified to copy. Use --files to specify file paths.[/bold red]")
            return
        include_tree = args.tree
        copy_files_to_clipboard(file_paths)
        return

    if args.ask is not None:
        # Handle the --ask functionality
        # Check if the --ask flag was used without a direct question (e.g., `--ask` alone)
        if args.ask is True:
            question = get_multiline_input_with_editor(mode="ASK")
            if not question:
                handle_no_prompt()
        else:
            question = args.ask

        file_paths = args.files if args.files else []
        include_tree = args.tree
        ask_gpt_with_files(question, file_paths, include_tree)
        return
    else:
        # Handle the build project functionality
        print(f"Opening prompt editor... ")
        time.sleep(2)

        # Step 1: Get multi-line project description from user
        project_description = get_multiline_input_with_editor(mode="BUILD")
        if not project_description:
            handle_no_prompt()

        print(f"Project Description: {project_description}")

        # Step 2: Generate the project structure using OpenAI API
        project_structure = generate_project_structure(project_description)
        print(f"\n🐒 ScriptMonkey created a project blueprint:")
        pprint(project_structure)

        # Step 3: Create the project structure (directories and files) on the filesystem
        print(f"\n🐒 ScriptMonkey is coding...")
        create_project_structure(project_structure_response=project_structure, project_description=project_description)
        print("\nProject structure creation complete.")

        # Step 4: Generate the README.md content based on the project description and structure
        readme_content = generate_readme(project_description, project_structure)
        readme_path = "./generated_project/README.md"
        with open(readme_path, "w") as readme_file:
            readme_file.write(readme_content)
        print(f"🐒 ScriptMonkey wrote a README.md file at: '{readme_path}'")
        return
