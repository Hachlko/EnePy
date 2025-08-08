import json
import os
import re
from urllib.parse import urlparse

SKILLS_FILE = "data/ene_skills.json"

def load_skills():
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_skills(skills):
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(skills, f, indent=2, ensure_ascii=False)

def detect_skill_learning(user_input: str):
    """
    Exemple : Ene retiens que 'ouvre twitch' = start https://twitch.tv
    """
    match = re.match(r"(?i)ene[, ]?\s*ret(iens|enir|iens que)?\s*[\"']?(.*?)['\"]?\s*=\s*(.*)", user_input)
    if match:
        skill = match.group(3).strip().lower()
        command = match.group(4).strip()
        return skill, command
    return None, None

def is_url(text: str) -> bool:
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def execute_skill(user_input: str, skills: dict) -> bool:
    """
    Si l'input contient un skill connu → exécute la commande liée.
    """
    for skill, command in skills.items():
        if skill in user_input.lower():
            print(f"🧠 Skill détecté : {skill} → {command}")
            if is_url(command):
                os.system(f'start {command}')
            else:
                os.system(command)
            return True
    return False
