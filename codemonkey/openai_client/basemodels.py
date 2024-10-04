from pydantic import BaseModel


class CodemonkeyResponse(BaseModel):
    problem: str  # A description of the error/problem
    solution: str  # The solution to the problem
    corrected_code: str  # The corrected version of the Python code
