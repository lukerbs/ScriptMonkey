import sys
import traceback
from .openai_client import chatgpt_json, CodemonkeyResponse, default_prompts
from .file_handler import read_file, write_file
import platform


def get_platform():
    os_name = platform.system()
    os_version = platform.release()
    return f"# Operating System: {os_name}, Version: {os_version}\n\n"


def codemonkey_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Pass through KeyboardInterrupt without handling it
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Get the error message
    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    print(error_message, "\n\n")
    print(f"🐒 CodeMonkey is fixing an error! One moment...")

    # Get the file responsible for the error (last frame)
    frame = traceback.extract_tb(exc_traceback)[-1]
    file_path = frame.filename

    # Read the code from the file
    original_code = read_file(file_path)
    content = f"{get_platform()}# Original Code:\n```\n{original_code}\n```\n\n# Error Message:\n{error_message}"

    # Returns response as structured dict
    solution = chatgpt_json(instructions=default_prompts.fix_error, content=content, response_format=CodemonkeyResponse)

    # Display the solution instead of the typical traceback
    print(f"\n[Codemonkey Solution]\nProblem:\n{solution['problem']}\n")
    print(f"Suggested Solution:\n{solution['solution']}\n")

    # Update the file with the corrected code
    write_file(file_path, solution["corrected_code"])
    print(f"Code has been automatically corrected at: '{file_path}'.")


# Replace the default sys.excepthook with our custom handler
def run():
    sys.excepthook = codemonkey_exception_handler
