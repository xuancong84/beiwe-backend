
def read_file(file_path):
    """reads in a file, returns a string of the entire file."""
    with open(file_path, 'r') as f:
        return f.read()

