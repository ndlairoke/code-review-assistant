import requests
from file_work import *
from uuid import uuid4

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
    # генерация уникального файла для сохранения истории диалога
    history_file = str(uuid4()) + '.txt'

    # проходимся по каждому файлу и анализируем его, сохраняя историю диалога в файл
    for file in files:
        code = read_file(file)
        prompt = make_prompt(code)
        result = mistral_analyze(prompt)
        write_file(history_file, f"User: {prompt}\nAssistant: {result}\n")

    review_prompt = """According to the code and found anti-patterns give your subjective opinion on the developer and describe the next point:
    1. How good are their skills?
    2. How professional they are?
    3. What would you rate them as a developer on a scale of 1 to 10. """
    history = read_file(history_file)

    # получаем анализ качества разработчика с учетом истории
    final_result = mistral_analyze(review_prompt, history)

    # delete_file(history_file)

    return final_result

