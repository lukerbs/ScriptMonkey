import os
from collections import defaultdict


def create_tree(start_path, prefix="", max_depth=None, current_depth=0, max_files_per_type=5):
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
            tree += create_tree(
                path,
                new_prefix,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                max_files_per_type=max_files_per_type,
            )

    return tree


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
