import os
import json
import re
from unidiff import PatchSet
from pathlib import Path


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

class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)
    

def parse_diff_to_code_files(diff_path: str, output_dir: str) -> None:
    """This function parses diff to code files
        diff: diff to parse
        Returns: dict with file name and code
    """
    patch = PatchSet.from_filename(diff_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for patched_file in patch:
        new_file_path = Path(output_dir) / patched_file.path
        new_file_path.parent.mkdir(parents=True, exist_ok=True)

        new_lines = []
        for hunk in patched_file:
            for line in hunk:
                if line.is_added or line.is_context:
                    new_lines.append(line.value)

        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"Файл восстановлен: {new_file_path}")

def get_files_in_dir(dir: str) -> list[str]:
    path = Path(dir)
    return [str(file) for file in path.rglob("*") if file.is_file()]
    