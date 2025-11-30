import os

def get_system_prompt(path: str="llm_config/llm_prompt.txt"):
    with open(path, "r") as file:
        return file.read()

def save_result_html(result: str, path: str="results/output.html"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        file.write(result)
        