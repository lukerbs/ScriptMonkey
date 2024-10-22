import os

from rich.console import Console

from .utils.tree import create_tree
from .utils.file_handler import read_file
from .utils.ui import render_response_with_syntax_highlighting
from .utils.parsers import remove_code_block_lines
from .openai_client.client import chatgpt_json, chatgpt
from .openai_client.basemodels import ProjectStructureResponse

console = Console()


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


def build_project(
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
        tree = create_tree(start_directory)
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
