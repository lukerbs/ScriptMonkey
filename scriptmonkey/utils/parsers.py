def remove_code_block_lines(input_string):
    """Removes any lines from the input string that contain '```'."""
    lines = input_string.splitlines()
    filtered_lines = [line for line in lines if "```" not in line]
    return "\n".join(filtered_lines)
