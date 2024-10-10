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


ignored_dirs = {
    "venv",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    "node_modules",
    ".next",
    "out",
    ".nuxt",
    "public",
    "jspm_packages",
    ".parcel-cache",
    ".vercel",
    "target",
    ".gradle",
    ".mvn",
    "bin",
    "obj",
    "coverage",
    "vendor",
    "storage",
    "cache",
    ".git",
    ".idea",
    ".vscode",
    ".DS_Store",
    "logs",
    "log",
    "tmp",
    "temp",
    ".angular",
    ".bundle",
    "vendor/bundle",
    "htmlcov",
    ".mypy_cache",
    ".pytest_cache",
}

# Define important file extensions
important_extensions = {
    # General programming and scripting languages
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rb",
    ".rs",
    ".php",
    ".sh",
    ".pl",
    ".swift",
    ".kt",
    ".kts",
    ".dart",
    ".scala",
    ".lua",
    ".r",
    ".jl",
    ".cs",
    ".csx",
    ".m",
    ".mm",
    ".bat",
    ".cmd",
}
