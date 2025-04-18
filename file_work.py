import os
import json
import re

class LazyDecoder(json.JSONDecoder):
    """
    This class is used to decode JSON files
    """
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)

def write_json_to_docx_file(file, json) -> None:
    """
    This function writes json to docx file
    file: docx file
    json: json to write

    JSON must be in this format:
    {
        "name": {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            "key4": "value4",
            
    """
    for key in json.keys():
        file.add_heading(key, level=2)
        small_json = json[key]

        for k in small_json.keys():
            p = file.add_paragraph('')
            p.add_run(f'{k}: ').bold = True
            p.add_run(str(small_json[k]))


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
