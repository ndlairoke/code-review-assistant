import requests
import json
from utils.json_docx_work import *

def make_prompt(code_text: str) -> str:
    """"This function makes prompt for analyzing code
        code_text: text of the code to analyze
    """

    return """"
        You are a senior code reviewer and software quality expert. Your task is to analyze the given code strictly and precisely, based on the criteria below.

        You must respond **only in valid JSON format**, using **double quotes only** for all fields. Each criterion must contain:

        - `"score"`: Integer from 0 (very bad) to 10 (excellent)
        - `"comment"`: Short summary of issues or good points
        - `"examples"`: **Real problematic lines of code** (not descriptions!), extracted exactly as-is from the input. If no issues – leave as empty string.
        - `"suggestions"`: Clear, practical suggestion(s) on how to fix or improve the examples provided
        - `"solution"`: A corrected version of the problematic code from `"examples"`, applying the suggestions above
        - `"legacy_context"`: true if the issue is caused by legacy technology or outdated standards
        - `"forced_solution"`: true if the original code is bad, but there's no better option due to constraints

        Make sure that:
        - `"examples"` must contain **real code lines from the input** that illustrate the issue
        - `"solution"` must contain an **improved version of the actual example lines**
        - `"suggestions"` must be relevant to the specific problem in `"examples"`
        - If there are no issues, use empty strings for `"examples"`, `"suggestions"` and `"solution"` and give a `"score"` of 10

        Criteria:
        1. **Code Smells** – detect signs of poor quality like: duplicated logic, long functions, deeply nested code, unclear naming, dead code.
        2. **Anti-Patterns** – detect bad design or architecture practices like: God Object, Spaghetti Code, Magic Numbers, overuse of global state, etc.
        3. **Legacy Compatibility** – determine whether the code is old, and if the implementation was acceptable for its time and technical environment.

        Respond in the following JSON format:

        {
        "CodeSmells": {
            "score": 6,
            "comment": "Long method and repeated logic",
            "examples": [
            "for (int i = 0; i < list.size(); i++) { process(list.get(i)); }",
            "for (int i = 0; i < list.size(); i++) { process(list.get(i)); }"
            ],
            "suggestions": "Extract repeated loop logic into a helper method to improve readability and reduce duplication.",
            "solution": "void processList(List<Item> list) {\n  for (Item item : list) {\n    process(item);\n  }\n}",
            "legacy_context": false,
            "forced_solution": false
        },
        
        "AntiPatterns": {
            "score": 3,
            "comment": "God Object pattern detected in Manager class",
            "examples": [
            "public class Manager { private DB db; private Logger log; private EmailService email; /* ... */ }"
            ],
            "suggestions": "Break the Manager class into smaller single-responsibility classes using proper separation of concerns.",
            "solution": "public class EmailManager { private EmailService email; /* ... */ }\npublic class DBManager { private DB db; /* ... */ }",
            "legacy_context": false,
            "forced_solution": false
        },

        "LegacyCompatibility": {
            "score": 10,
            "comment": "The code reflects acceptable practices for the platform and era.",
            "examples": "",
            "suggestions": "",
            "solution": "",
            "legacy_context": true,
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

    return json.loads(response.json()['response'], cls=LazyDecoder)