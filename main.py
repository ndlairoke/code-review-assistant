from analyze import *
from uuid import uuid4
# from file_work import write_file, read_file, delete_file
from docx import Document
from docx2pdf import convert

# путь к файлу который нужно проанализировать (поменяй чтоб потестить)
file1 = 'E:/учеба/moroshka_bot/work_time/time_func.py'
file2 = 'E:/учеба/moroshka_bot/handlers/dinner_time.py'
files = [file1, file2]

analyze_code_files(files)
# print(analysis)

# filename = str(uuid4()) + '.docx'
# document = Document()
# document.add_heading('Отчет об оценке качества кода', 0)
# p = document.add_paragraph()
# p.add_run('Общая информация').bold = True
# p = document.add_paragraph()
# p.add_run('ФИО: ').bold = True
# p.add_run('Котейкин Мяу Мяус')
# document.add_heading('Метрики качества', level=1)
# document.add_paragraph(
#     'Профессионализм: 100%', style='List Bullet'
# )
# document.add_paragraph(
#     'Милота: 100%', style='List Bullet'
# )


# document.save(filename)
# convert(filename, filename.replace('.docx', '.pdf'))