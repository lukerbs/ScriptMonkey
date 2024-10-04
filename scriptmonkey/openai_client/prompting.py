import os


def load_prompt(path: str) -> str:
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path, "r") as file:
        return file.read()


class DefaultPrompts:
    def __init__(self):
        self.fix_error = load_prompt(path="./prompts/fix_error.txt")
