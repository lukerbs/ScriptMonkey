import re
import os
import sys
import time
import itertools
import platform
import threading
import subprocess

import tempfile
from rich.syntax import Syntax
from rich.console import Console
from rich.markdown import Markdown


console = Console()


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


def cli_text_editor(mode: str) -> str:
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
