import json
import re

class LazyDecoder(json.JSONDecoder):
    """
    Декодер, который позволяет избежать ошибок при декодировании JSON, содержащего экранированные обратные косые черты
    """
    def decode(self, s, **kwargs):
        """
        Декодирование строки в JSON
        """
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)

def write_json_to_docx_file(file: str, json: dict) -> None:
    """
    Запись JSON в файл docx
    Args:
        file: файл для записи
        json: JSON
    
    Example:
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
            clean_text = str(small_json[k]).replace("\n", "   ")
            p.add_run(clean_text)

def write_to_docx_file(file: str, heading:str, text) -> None:
    """
    Запись в файл docx
    Args:
        file: файл для записи
        heading: заголовок
        text: текст
    """
    
    file.add_heading(heading, level=2)
    p = file.add_paragraph('')
    if text == []:
        p.add_run('Not found').bold = True
    else:
        p.add_run(text).bold = True
