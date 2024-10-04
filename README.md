
# Codemonkey 🐒

Codemonkey is a Python package that automatically detects and fixes errors in your code using OpenAI's GPT API. It works with any IDE or code editor, analyzing your code at runtime, providing solutions to errors, and even updating the file with the corrected code.

## Features
- **Automatic error detection**: Captures errors during runtime.
- **AI-powered fixes**: Uses OpenAI's GPT API to understand and resolve errors.
- **Code auto-correction**: Automatically updates your Python files with the fixes.
- **Cross-IDE compatibility**: Works with any IDE or code editor.

## Installation

To install Codemonkey, simply run:

```bash
pip install codemonkey
```

## Usage

1. Import `codemonkey` in your Python script.
2. Call `codemonkey.run()` to activate the error handler.
3. Run your code, and let Codemonkey handle any errors that occur.

### Example

```python
import codemonkey

# Enable Codemonkey's error handler
codemonkey.run_codemonkey()

# Intentional error for testing
def add(a, b):
    return a + b  # This will fail if b is a string

print(add(2, "3"))  # Codemonkey will automatically fix this error and update the file
```

Once an error occurs, Codemonkey will:
1. Detect the error.
2. Send the error and code to OpenAI for analysis.
3. Provide a solution and automatically update the file with the correct code.

## How It Works

Codemonkey replaces Python's default exception handling with a custom handler. When an error is caught, it:
- Collects the traceback and the Python file that caused the error.
- Sends the error message and code to OpenAI.
- Receives the solution as structured JSON.
- Applies the fix directly to the source file.

## Requirements
- Python 3.6 or later
- OpenAI API key

## Setup

To use Codemonkey, you'll need an OpenAI API key. Set it up as follows:

```bash
export OPENAI_API_KEY='your-api-key'
```

Let Codemonkey take care of your Python errors so you can focus on building!
