import os

from dotenv import load_dotenv
from pydantic import BaseModel
import openai

# Load the OpenAI API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    # Initialize openai API client
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    raise ValueError("Missing OpenAI API Key. Please check your environment variables.")


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
