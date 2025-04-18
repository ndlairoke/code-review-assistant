import os
import shutil
from pathlib import Path

def write_file(filename: str, text: str) -> None:
    """
    Запись в файл
    Args:
        filename: путь к файлу
        text: текст, который нужно записать в файл
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text)

def read_file(filename: str) -> str:
    """
    Чтение из файла
    Args:
        filename: путь к файлу
    Returns:
        text: текст из файла
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def delete_file(filename: str) -> None:
    """
    Удаление файла
    Args:
        filename: путь к файлу
    """
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

def delete_dir(dirname: str) -> None:
    """
    Удаление папки
    Args:
        dirname: путь к папке
    """
    try:
        shutil.rmtree(dirname)
    except FileNotFoundError:
        pass

def get_files_in_dir(dir: str) -> list[str]:
    """
    Получение списка файлов в папке
    Args:
        dir: путь к папке
    Returns:
        list: список файлов в папке
    """
    path = Path(dir)
    return [str(file) for file in path.rglob("*") if file.is_file()]