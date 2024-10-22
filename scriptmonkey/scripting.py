import os

from .openai_client import chatgpt
from .utils.parsers import remove_code_block_lines


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
        "Make sure to return the content directly, without wrapping it in any code fences like triple quotes or backticks ."
        "i.e. DO NOT include any triple backtrick wrappers at all for any code, (e.g. ```python<content here>```) just return the code as plain text."
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
    generated_content = remove_code_block_lines(generated_content)

    return generated_content


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
