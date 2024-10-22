from pydantic import BaseModel
from typing import List, Optional


class FunctionDetails(BaseModel):
    function_name: str
    description: str
    inputs: Optional[List[str]]  # List of inputs with data types
    outputs: Optional[List[str]]  # List of outputs with data types


class ProjectFile(BaseModel):
    path: str  # The full path to the file or directory
    description: str  # High-level purpose of the directory or file
    functions: Optional[List[FunctionDetails]]  # List of functions/classes if it's a code file


class ProjectStructureResponse(BaseModel):
    files: List[ProjectFile]  # List of all files and directories in the project


class ScriptMonkeyResponse(BaseModel):
    problem: str  # A description of the error/problem
    solution: str  # The solution to the problem
    corrected_code: str  # The corrected version of the Python code
