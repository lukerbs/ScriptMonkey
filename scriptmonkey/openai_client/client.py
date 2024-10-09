import os

from dotenv import load_dotenv
from pydantic import BaseModel
import openai

CONFIG_FILE = os.path.expanduser("~/.scriptmonkey_config")

# Load environment variables from the .env file if present
load_dotenv()


def get_openai_api_key():
    # Try to get the API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    # If not set, check the config file
    if not api_key and os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            api_key = f.read().strip()

    # If still not set, prompt the user for it
    if not api_key:
        print("It looks like your OpenAI API key isn't set.")
        api_key = input("🐒 Please paste your OpenAI API key here and press ENTER: ").strip()

        # Save the key to the config file for future use
        with open(CONFIG_FILE, "w") as f:
            f.write(api_key)
        print(f"Your API key has been saved to {CONFIG_FILE} for future use.")

    return api_key


# Get the OpenAI API key using the function
OPENAI_API_KEY = get_openai_api_key()

# Initialize the OpenAI client with the obtained API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def chatgpt_json(instructions: str, content: str, response_format: BaseModel) -> dict:
    """This function is used to return content from OpenAI Chat Completions API as a structured dictionary response.

    Args:
        instructions (str): Instructions for the LLM (how the LLM should process the input content).
        content (str): Information that the LLM is supposed to process.
        response_format (BaseModel): The output format defined by a Pydantic Basemodel.

    Returns:
        dict: The structured output response from the LLM.
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": content},
        ],
        response_format=response_format,
    )

    structured_response = completion.choices[0].message.parsed
    return structured_response.model_dump()


def chatgpt(prompt: str, model="gpt-4o", max_tokens=None):
    """Function for generating responses to text prompts with OpenAI's ChatGPT API

    Args:
        prompt (str): The instructions for ChatGPT to respond to
        model (str, optional): ChatGPT model to use. Defaults to "gpt-4o".
            - List of Available Models: https://platform.openai.com/docs/models/continuous-model-upgrades
        max_tokens (int, optional): Optional, the max tokens to be returned by response. Defaults to no limit (i.e. None).

    Returns:
        str: Returns the response to the prompt as a string value
    """
    completion = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    response = completion.choices[0].message.content
    return response
