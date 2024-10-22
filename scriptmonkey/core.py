import os
import sys
import time
import argparse
import platform
import traceback
from pprint import pprint

from rich.console import Console

from .utils.ui import Spinner, cli_text_editor
from .utils.key_manager import update_api_key
from .utils.file_handler import read_file, write_file, copy_files_to_clipboard
from .agents import (
    ask_gpt_with_files,
    generate_project_structure,
    build_project,
    generate_readme,
)

from .openai_client.basemodels import ScriptMonkeyResponse
from .openai_client import (
    chatgpt_json,
    default_prompts,
)

console = Console()
CONFIG_FILE = os.path.expanduser("~/.scriptmonkey_config")


def get_platform():
    os_name = platform.system()
    os_version = platform.release()
    return f"# Operating System: {os_name}, Version: {os_version}\n\n"


def scriptmonkey_exception_handler(exc_type, exc_value, exc_traceback):
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
    sys.excepthook = scriptmonkey_exception_handler


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
            question = cli_text_editor(mode="ASK")
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
        project_description = cli_text_editor(mode="BUILD")
        if not project_description:
            handle_no_prompt()

        print(f"Project Description: {project_description}")

        # Step 2: Generate the project structure using OpenAI API
        project_structure = generate_project_structure(project_description)
        print(f"\n🐒 ScriptMonkey created a project blueprint:")
        pprint(project_structure)

        # Step 3: Create the project structure (directories and files) on the filesystem
        print(f"\n🐒 ScriptMonkey is coding...")
        build_project(project_structure_response=project_structure, project_description=project_description)
        print("\nProject structure creation complete.")

        # Step 4: Generate the README.md content based on the project description and structure
        readme_content = generate_readme(project_description, project_structure)
        readme_path = "./generated_project/README.md"
        with open(readme_path, "w") as readme_file:
            readme_file.write(readme_content)
        print(f"🐒 ScriptMonkey wrote a README.md file at: '{readme_path}'")
        return
