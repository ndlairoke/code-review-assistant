import requests
from file_work import *
from uuid import uuid4
from docx import Document
from docx2pdf import convert
import datetime as dt
import json

def make_prompt(code_text: str) -> str:
    """"This function makes prompt for analyzing code
        code_text: text of the code to analyze
    """

    return """"
        You are a professional code reviewer specializing in software quality analysis.
        You are given code to analyze based on the following criteria.
        The response must be strictly structured in JSON format, where for each criterion the following is specified:
        - Rating from 0 to 10 (10 is excellent, 0 is very bad)
        - Comments on what was good or bad
        - Examples of problem areas (if any)
        - Label `legacy_context`: true if the problem is due to legacy technologies
        - Label `forced_solution`: true if the bad solution was the only possible one within the constraints

        Criterias:
        1. Code Smells – repetitive code, long methods, redundant conditions, poor organization.
        2. Anti-Patterns – presence of architectural and design anti-patterns (e.g. God Object, Spaghetti Code, etc.)
        3. Legacy Compatibility – if the code is old, evaluate how adequate the solutions are in the context of their time and 
            environment constraints.

        Output must look like this:

        json
        {
            'Code Smells': {
                'score': 6,
                'comment': 'Repetetive code',
                'examples': ['line 40-45'],
                'legacy_context': false,
                'forced_solution': false
            },
            
            'Anti Patterns': {
                "score": 4,
                "comment": "Singleton applied in wrong place",
                "examples": ["line 70"],
                "legacy_context": true,
                "forced_solution": true
            },

            'Legacy Compatibility': {
                'score': 10,
                'comment': "The solutions are adequate for their time",
                'examples': [],
                'legacy_context': false,
                'forced_solution': false
            }
        }
        
        The code to analyze is:
        """ + code_text

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
        files: list of files with code to analyze
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

        # переводи строку в json формат и обязательно используем декодером для избежания ошибок в работе программы
        json_result = json.loads(result, cls=LazyDecoder)
        write_file(history_file, f"User: {prompt}\nAssistant: {result}\n")
        
        p = report.add_paragraph()
        p.add_run(f"Файл: {file}\n").bold = True
        write_json_to_docx_file(report, json_result)

    review_prompt = """
        You are an experienced team leader and code reviewer. Your job is to give the developer feedback on the quality of their code.
        Analyze the code for the following aspects:
        1. What good aspects did you notice in the code? (e.g. good structure, readability, attention to security, etc.)
        2. What improvements would you suggest? (optimization, style, architecture, security, etc.)
        3. Give 2-3 specific tips on what the developer should learn or improve to write even better
        4. If there are positive or negative aspects associated with the outdated stack, be sure to mention it.

        Return the answer in a strictly structured JSON format:

        json
        {
            'Overall Review': {
                "strengths": "The code is well structured, modules are logically separated. 
                                Explicit typing is used",
                "improvements": "In places the code style is not followed - indents and line lengths. 
                                    Repetitive code should be avoided, for example, in functions X and Y",
                "recommendations": "Learn SOLID principles and start applying them in the architecture.
                Try using linters (e.g. flake8, eslint) for automatic style control.
                Understand design patterns, especially in terms of separation of concerns"
            }
        }

        Do not include 'legacy_context' and 'forced_solution' into the final response's JSON!!!
        """
    history = read_file(history_file)

    # получаем анализ качества разработчика с учетом истории
    final_result = mistral_analyze(review_prompt, history)
    json_final_result = json.loads(final_result, cls=LazyDecoder)
    write_json_to_docx_file(report, json_final_result)

    report_name = f'report-{time}'
    report.save(report_name + '.docx')
    convert(report_name + '.docx', report_name + '.pdf')

    delete_file(history_file)
    delete_file(report_name + '.docx')

    return f'Отчет сгенерирован в файле {report_name + '.pdf'}'

