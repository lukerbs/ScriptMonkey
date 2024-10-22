import os

import pyperclip
from rich.console import Console

from .tree import create_tree


console = Console()


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
        tree = create_tree(start_directory)
        formatted_output += "- - - - - - - - - -\n\n# PROJECT TREE\n"
        formatted_output += f"{tree}\n\n"

    # Copy the formatted output to the clipboard
    pyperclip.copy(formatted_output)
    console.print("[green]🐒 Content has been copied to the clipboard.[/green]")


def read_file(path: str) -> str:
    """Loads a file and returns the content.

    Args:
        path (str): Path to the file

    Returns:
        str: The content of the file
    """
    with open(path, "r") as file:
        return file.read()


def write_file(path: str, content: str) -> None:
    """Writes string content to a file.

    Args:
        path (str): Path to the file.
        content (str): Content to write to file.
    """
    with open(path, "w") as file:
        file.write(content)
