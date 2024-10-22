import os
import sys

CONFIG_FILE = os.path.expanduser("~/.scriptmonkey_config")


# - - - - - API KEY MANAGEMENT - - - - -


def save_api_key(api_key: str):
    """Save the OpenAI API key to the configuration file and environment variable."""
    with open(CONFIG_FILE, "w") as file:
        file.write(api_key)
    os.environ["OPENAI_API_KEY"] = api_key
    print(f"✅ OpenAI API key saved to {CONFIG_FILE}.")


def get_openai_api_key() -> str:
    """Retrieve the OpenAI API key from environment or configuration file."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # Check for API key in the configuration file
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                api_key = file.read().strip()

    # Prompt user for API key if not found
    if not api_key:
        print("🐒 ScriptMonkey requires an OpenAI API key to function.")
        api_key = input("Please enter your OpenAI API key: ")

        if api_key:
            save_api_key(api_key)

    if not api_key:
        print("❌ No API key provided. Exiting ScriptMonkey.")
        sys.exit(1)

    return api_key


def update_api_key():
    """Prompt the user to update the OpenAI API key."""
    api_key = input("Enter the new OpenAI API key: ")
    if api_key:
        save_api_key(api_key)
        print("✅ OpenAI API key updated successfully.")
    else:
        print("❌ No API key provided. The API key was not updated.")


# - - - - - NEW FEATURES - - - - -
