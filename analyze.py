import requests
from file_work import *
from uuid import uuid4
from docx import Document
from docx2pdf import convert
import datetime as dt
import json

WEIGHTS = {
    "Security": 3.0,
    "CodeStyle": 1.5,
    "CodeSmells": 2.0,
    "AntiPatterns": 2.5,
    "LegacyCompatibility": 1.0
}

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
            If there's no smells, rate it as 10. The more smells the lower the score.
        2. Anti-Patterns – presence of architectural and design anti-patterns (e.g. God Object, Spaghetti Code, etc.). 
            If there's no anti-patterns, rate it as 10. The more anti-patterns the lower the score.
        3. Legacy Compatibility – if the code is old, evaluate how adequate the solutions are in the context of their time and 
            environment constraints.
            If there's no legacy code, rate is as 10. The more legacy code the lower the score.

        Make sure to use double quotes in JSON!!!! You don't need to repeat the text in the example!
        Output must look like this:

        json
        {
            "CodeSmells": {
                "score": 6,
                "comment": "Repetetive code",
                "examples": "line 40-45, line 60-70",
                "legacy_context": false,
                "forced_solution": false
            },
            
            "AntiPatterns": {
                "score": 4,
                "comment": "Singleton applied in wrong place",
                "examples": "line 80",
                "legacy_context": true,
                "forced_solution": true
            },

            "LegacyCompatibility": {
                "score": 10,
                "comment": "The solutions are adequate for their time",
                "examples": "",
                "legacy_context": false,
                "forced_solution": false
            }
        }
        
        The code to analyze is:
        """ + code_text

def mistral_analyze(prompt: str, history: str = "") -> dict:
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

    try: 
        result = json.loads(response.json()['response'], cls=LazyDecoder)
    except Exception:
        result = response.json()['response']

    return result


def analyze_diff_and_write_in_docx(diff_path: str, docx: str, history_file: str):
    """This function analyzes diff file and gives feedback about it and how good the developer is
        diff_path: path to diff file
        docx: path to docx file
        history_file: path to history files
    """
    # сумма очков за каждый критерий * вес критерия
    score = 0

    # создаем отдельную папку для диффа, называем пока что по времени, чтобы при анализе других диффов не путаться
    time = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f'./restored/{time}'

    # парсим диффы в файлы с кодом с сохраннием структуры папок
    parse_diff_to_code_files(diff_path, output_dir)
    diff_files = get_files_in_dir(output_dir)

    # ЗДЕСЬ БУДЕТ ДОБАВЛЕНИЕ ОГЛАВЛЕНИЯ С НАЗВАНИЕМ MR ИЛИ ТИПА ТОГО

    for file in diff_files:
        code = read_file(file)
        prompt = make_prompt(code)
        ai_result = mistral_analyze(prompt)
        # ЗДЕСЬ БУДЕТ СТАТИЧЕСКИЙ АНАЛИЗ

        # записываем результат в файл истории
        write_file(history_file, f"User: {prompt}\nAssistant: {ai_result}\n")
        # ЗДЕСЬ БУДЕТ ЗАПИСЬ СТАТ АНАЛИЗА В ФАЙЛ ИСТОРИИ

        p = docx.add_paragraph()
        p.add_run(f"\nФАЙЛ: {file}").bold = True
        write_json_to_docx_file(docx, ai_result)

        for key in ai_result.keys():
            small_json = ai_result[key]
            score += small_json['score'] * WEIGHTS[key]

        # ЗДЕСЬ БУДЕТ ЗАПИСЬ СТАТ АНАЛИЗА В ФАЙЛ docx
        # ЗДЕСЬ БУДЕТ ДОБАВЛЕНИЕ ОЧКОВ ЗА СТАТ АНАЛИЗ В SCORE

    # возвращаем словарь {кол-во файлов: общая оценка} для формирования оценки разработчика
    return {len(diff_files): score}

def make_review_and_write_in_docx(docx: str, history_file: str) -> None:
    review_prompt = """
        You are an experienced team leader and code reviewer. Your job is to give the developer feedback on the quality of their code.
        Analyze the code for the following aspects:
        1. What good aspects did you notice in the code? (e.g. good structure, readability, attention to security, etc.)
        2. What improvements would you suggest? (optimization, style, architecture, security, etc.)
        3. Give 2-3 specific tips on what the developer should learn or improve to write even better
        4. If there are positive or negative aspects associated with the outdated stack, be sure to mention it.

        Make sure to use double quotes in JSON!!!! You don't need to repeat the text in the example!
        Return the answer in a strictly structured JSON format:

        json
        {
            "Overall Review": {
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
    result = mistral_analyze(review_prompt, history)
    
    write_json_to_docx_file(docx, result)




