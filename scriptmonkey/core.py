import sys
import traceback
from .openai_client import chatgpt_json, ScriptMonkeyResponse, default_prompts
from .file_handler import read_file, write_file
import platform
import threading
import itertools
import time


def get_platform():
    os_name = platform.system()
    os_version = platform.release()
    return f"# Operating System: {os_name}, Version: {os_version}\n\n"


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


def codemonkey_exception_handler(exc_type, exc_value, exc_traceback):
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
    sys.excepthook = codemonkey_exception_handler
