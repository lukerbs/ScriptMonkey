from setuptools import setup, find_packages

setup(
    name="codemonkey",  # Package name (this will be the PyPI name)
    version="0.1.0",  # Initial release version
    description="A Python package that automatically fixes errors in your code using OpenAI's GPT API",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",  # If README.md is in markdown format
    url="https://github.com/yourusername/codemonkey",  # Replace with your repo URL
    author="Luke",  # Your name
    author_email="youremail@example.com",  # Your email
    license="MIT",  # License type (or whatever you choose)
    packages=find_packages(),  # Automatically find package directories
    install_requires=[
        "openai",  # Dependencies required by your package
        "pydantic",
    ],
    python_requires=">=3.6",  # Minimum Python version
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
