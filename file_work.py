import os

def write_file(filename: str, text: str) -> None:
    """This function writes in file
        filename: path to the file to save history to
        text: text to save
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text)

def read_file(filename: str) -> str:
    """This function reads file
        filename: path to the file to read
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def delete_file(filename: str) -> None:
    """This function deletes file
        filename: path to the file to delete
    """
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

