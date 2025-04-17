from analyze import *
from uuid import uuid4
# from file_work import write_file, read_file, delete_file
from docx import Document

# путь к файлу который нужно проанализировать (поменяй чтоб потестить)
file1 = 'E:/учеба/moroshka_bot/work_time/time_func.py'
file2 = 'E:/учеба/moroshka_bot/handlers/dinner_time.py'
files = [file1]

analyze_code_files(files)
