import requests
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

def mistral_analyze(filename: str) -> str:
    """This function analyzes files on having anti patterns and code smells using mistral
        filename: path to the file containg the code to analyze
    """
    with open(filename, "r", encoding="utf-8") as f:
        code_text = f.read()

        prompt = make_prompt(code_text)
        print("Mistral is working!")
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })

    return response.json()['response']
        
def starcoder2_analyze(filename: str) -> str:
    """This function analyzes files on having anti patterns and code smells using starcoder2
        filename: path to the file containg the code to analyze
    """
    with open(filename, "r", encoding="utf-8") as f:
        code_text = f.read()

        prompt = make_prompt(code_text)
        print("Starcoder2 is working!")
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "starcoder2:15b",
            "prompt": "Tell me a joke about cats",
            "stream": False
        })

    return response.json()['response']


