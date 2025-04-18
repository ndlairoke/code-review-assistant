import requests
import json
from utils.json_docx_work import *

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

    return json.loads(response.json()['response'], cls=LazyDecoder)