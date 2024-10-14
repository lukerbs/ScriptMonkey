
# ScriptMonkey 🐒

ScriptMonkey is an AI-powered CLI tool and Python library that reimagines how projects are built. It doesn’t just generate simple scripts or templates like traditional LLMs—it creates entire, multi-file, multi-directory projects with fully custom code. Complex software projects can be generated in seconds based on your natural language descriptions, providing everything you need, from models and routes to templates and configuration files. With ScriptMonkey, you can instantly bootstrap new ideas or start complex projects without the tedious setup. The tool is perfect for developers looking to quickly prototype, experiment, or build production-ready applications without having to write boilerplate code manually.

Importantly, ScriptMonkey is versatile and can be used to build any type of software project in any programming language. Whether you’re working with Python, JavaScript, Java, C++, or any other language, ScriptMonkey can generate project structures and provide tailored code. Additionally, its context-aware Q&A feature allows you to ask technical questions about projects in any language, with or without providing files for context. You can even use your default editor for longer, multi-line prompts, ensuring that ScriptMonkey can adapt to your specific needs.

## Features
- **Custom Project Generation**: Create entire Python projects, not just boilerplate code. ScriptMonkey generates the specific files and directories you need based on your description.
- **Lightning-Fast Setup**: Complex Python projects can be generated in seconds, saving you time and effort.
- **Automatic Error Detection**: Captures errors during runtime.
- **AI-Powered Fixes**: Uses OpenAI's GPT API to understand and resolve errors.
- **Code Auto-Correction**: Automatically updates your Python files with the fixes.
- **Cross-IDE Compatibility**: Works with any IDE or code editor.
- **Context-Aware Q&A**: Ask questions directly to ChatGPT with or without providing files for context. Get detailed answers with code examples, explanations, and best practices tailored to your needs.

## 🚀 Watch the Demo

[![ScriptMonkey Demo](https://img.youtube.com/vi/2zoCDlf0Zf8/maxresdefault.jpg)](https://youtu.be/2zoCDlf0Zf8)

Click the image above or watch the video directly on [YouTube](https://youtu.be/2zoCDlf0Zf8).

## Installation

To install ScriptMonkey, simply run:

```bash
pip install scriptmonkey
```

## Usage

### Project Generation with `scriptmonkey` CLI Tool

ScriptMonkey can generate a complete, custom-coded project structure based on a description you provide. This feature helps you quickly set up new projects with the necessary files and folders.

#### How to Use

1. Run the following command in your terminal:

   ```bash
   scriptmonkey
   ```

2. A text editor will open (e.g., `nano`, `vim`, or `notepad` depending on your environment). Follow the on-screen instructions to provide a detailed description of your project.

3. Save and close the editor. ScriptMonkey will then:
   - Generate a complete project structure based on your description.
   - Create directories, code files, and templates.
   - Automatically generate a `README.md` with installation instructions and usage details.

#### Example Project Description Prompt

```
I need a Flask-based web application for managing a book library. The application should include:
- User authentication (login, registration, password reset).
- Models for Users, Books, and Authors using SQLAlchemy.
- A REST API with routes for adding, updating, and deleting books and authors.
- An admin dashboard for managing users and viewing statistics.
- HTML templates for user login, book list, and book detail views.
- The database should use PostgreSQL.
- Include environment-specific configurations for development and production.
```

ScriptMonkey will use this description to create a project structure and code files for you in a directory named `generated_project`.

### Context-Aware Q&A with `scriptmonkey --ask` CLI Tool

ScriptMonkey can help answer your technical questions, whether or not you provide code files for context. This feature allows you to leverage the power of ChatGPT to ask questions about files, clarify concepts, get code reviews, or understand best practices in various programming languages.

#### How to Use

- **Pass a question directly**:

  For quick, short prompts, you can directly pass your question using the `--ask` parameter:

  ```bash
  scriptmonkey --ask "What are the best practices for database indexing?"
  ```

- **Use your default editor for longer prompts**:

  If you need to provide a more detailed or multi-line prompt, simply use `--ask` without specifying a question. This will open up your default text editor (e.g., `vim`, `nano`, `notepad`) where you can write out your question or prompt:

  ```bash
  scriptmonkey --ask
  ```

  After you write your question in the editor and save and close it, ScriptMonkey will use the content as the question. This is especially useful for longer or more complex queries that require more explanation.

- **Ask a question about specific local files**:

  ```bash
  scriptmonkey --ask "Can you help me optimize this function?" --files ./path/to/file1.py ./path/to/file2.js
  ```

  The `--files` flag allows you to provide specific files as context for your question. ScriptMonkey will include the contents of these files in its analysis, allowing it to reference the actual code or data you are working with. This is particularly useful for getting detailed feedback on specific code snippets, debugging issues, or seeking advice on how to improve certain parts of your project.
  
  When you use `--files`, ScriptMonkey will read the contents of each provided file, include them in the prompt, and tailor its response based on the combined context of your question and the file contents. This feature ensures that you get precise, context-aware answers, helping you solve code challenges or understand complex concepts more effectively.

- **Ask a question with a directory tree**:

  ```bash
  scriptmonkey --ask "How do I organize this project better?" --tree
  ```

  The `--tree` flag will include a tree representation of the current working directory in the context for your question. This is particularly useful when you want to get feedback on the structure of your codebase or when your question relates to the project organization. It can be used in tandem with the `--files` flag to provide additional context about how those files fit within the larger context of the project.

  ScriptMonkey will analyze your question and any provided files or the directory tree to give a detailed, markdown-formatted response with explanations and code suggestions, if applicable. This feature is great for in-depth guidance on code optimization, architecture, or general programming questions.

### Copy Key Files and Project Details with `--copy`

ScriptMonkey's new `--copy` feature is designed to streamline the process of copying critical code files and project structure details into your clipboard, making it easier to ask questions to LLMs like ChatGPT or Claude. This feature formats the copied content in a neat way that includes file contents and the directory tree, making it simple to paste into a conversation for contextual help.

#### How to Use

- **Copy file contents directly**:

  You can use the --copy flag to quickly copy the contents of specified files into your clipboard, neatly formatted for easy sharing with an LLM. When combined with the --files flag, ScriptMonkey will copy the contents of the selected files along with a complete directory tree of your project. This provides additional context, helping LLMs better understand your project’s structure:

  ```bash
  scriptmonkey --copy --files path/to/file1.py path/to/file2.js
  ```

  Your files and project directory tree are automatically copied to your clipboard in the format:

  ```
  - - - - - - - - - -
  Here are some details about the project.

  # path/to/file1.py
  <content from file1.py>

  - - - - - - - - - -

  # path/to/file2.js
  <content from file2.js>

  - - - - - - - - - -

  # PROJECT TREE
  <directory structure>
  ```




### Error Handling with `scriptmonkey.run()`

ScriptMonkey doesn't just build projects; it also makes debugging a breeze.

1. Import `scriptmonkey` in your Python script.
2. Call `scriptmonkey.run()` to activate the error handler.
3. Run your code, and let ScriptMonkey handle any errors that occur.

#### Example

```python
import scriptmonkey

# Enable ScriptMonkey's error handler
scriptmonkey.run()

# Intentional error for testing
def add(a, b):
    return a + b  # This will fail if b is a string

print(add(2, "3"))  # ScriptMonkey will automatically fix this error and update the file.
```

Once an error occurs, ScriptMonkey will:
1. Detect the error.
2. Send the error and code to OpenAI for analysis.
3. Provide a solution and automatically update the file with the corrected code.

### Setting or Updating Your OpenAI API Key

If you haven't set your OpenAI API key yet or need to update it, you can do so with the following command:

```bash
python3 -m scriptmonkey --set-api-key your-api-key
```

This will store the API key in a config locally and use it for all future interactions with OpenAI.

## Requirements
- Python 3.6 or later
- An OpenAI API key (follow the steps below if you don't have one)

## Obtaining an OpenAI API Key

1. Go to the OpenAI website: [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account.
3. Navigate to the **API keys** section in your account dashboard.
4. Create a new API key and copy it.

## Configuring the API Key for ScriptMonkey

- **Option 1: Environment Variable**  
  You can set up your API key as an environment variable:

  ```bash
  export OPENAI_API_KEY='your-api-key'
  ```

- **Option 2: Entering the API Key When Prompted**  
  If ScriptMonkey does not find an API key in your environment variables, it will prompt you to enter your key. Once entered, it will save the key to a configuration file for future use.

- **Option 3: Using the `--set-api-key` Command**  
  Use the `--set-api-key` command as shown above to set or update your API key easily.

Let ScriptMonkey take care of your Python errors and project setup so you can focus on building!
