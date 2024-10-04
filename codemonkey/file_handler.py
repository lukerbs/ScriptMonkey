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
