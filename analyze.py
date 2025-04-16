import requests
from file_work import *
from uuid import uuid4
from docx import Document
from docx2pdf import convert
import datetime as dt

def make_prompt(code_text: str) -> str:
    """"This function makes prompt for analyzing code
        code_text: text of the code to analyze
    """

    return f""""Analyze the following code:
        1.Point out any anti-patterns and code smells.
        2.Suggest improvements.
        3. If there's any legacy code you should point it out
        4. If you notice an anti-pattern but there's no other possible solution, point it out as a potential issue.

        Your answer should contain the following points:
        1. Anti-patterns, code smells.
        2. Suggestions for improvements.
        3. Potential issues if any
        4. Legacy code if any
        Do not input any code in your answer

        Answer in Russian only.
        The code to analyze is:
        {code_text}"""

def mistral_analyze(prompt: str, history: str = "") -> str:
    """This function analyzes code text on having anti patterns and code smells using mistral
        code: code to analyze
        history: history of previous responses
    """
    # Инициализируем историю диалога, если она есть
    talk_history = []

    if history:
        talk_history.append(history)
        talk_history.append("Assistant: Great, keep going")  # Имитация прошлой реакции

    talk_history.append({f"User: {prompt}"})
    full_prompt = "\n".join([str(item) for item in talk_history]) + "\nAssistant:"


    print("Mistral is working!")
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": full_prompt,
        "stream": False
    })
    return response.json()['response']

def analyze_code_files(files: list[str]) -> str:
    """This function analyzes files on having anti patterns and code smells using mistral
    and gives feedback about them and how good the developer is
        files: files with code to analyze
    """
    time = dt.datetime.now().strftime("%Y-%m-%d_%H-%M")

    history_file = f'history-{time}.txt'
    report = Document()
    report.add_heading('Отчет об оценке качества кода', 0)
    p = report.add_paragraph()
    p.add_run('Общая информация').bold = True
    p = report.add_paragraph()
    p.add_run('ФИО: ').bold = True
    p.add_run('Котейкин Мяу Мяус')

    report.add_heading('Выявленные проблемы', level=1)

    # проходимся по каждому файлу и анализируем его, сохраняя историю диалога в файл
    for file in files:
        code = read_file(file)
        prompt = make_prompt(code)
        result = mistral_analyze(prompt)
        write_file(history_file, f"User: {prompt}\nAssistant: {result}\n")
        
        p = report.add_paragraph()
        p.add_run(f"Файл: {file}\n").bold = True
        report.add_paragraph(f'{result}\n\n')

    review_prompt = """According to the code and found anti-patterns give your subjective opinion on the developer and describe the next point:
    1. How good are their skills?
    2. How professional they are?
    3. What would you rate them as a developer on a scale of 1 to 10. 
    Answer in Russian only"""
    history = read_file(history_file)

    # получаем анализ качества разработчика с учетом истории
    final_result = mistral_analyze(review_prompt, history)

    report.add_heading('Ревью', level=1)
    report.add_paragraph(f'{final_result}\n\n')

    report_name = f'report-{time}'
    report.save(report_name + '.docx')
    convert(report_name + '.docx', report_name + '.pdf')

    delete_file(history_file)
    delete_file(report_name + '.docx')

    return f'Отчет сгенерирован в файле {report_name + '.pdf'}'

