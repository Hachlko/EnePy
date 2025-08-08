def decision_engine(user_input: str, skills: dict, traits: list = None) -> dict:
    """
    Détecte si l'utilisateur
    – déclenche un skill appris
    — demande une recherche web
    — ou si l'on laisse la LLM répondre

    traits : liste de traits de personnalité (optionnel, non utilisé ici mais prêt à l'emploi)
    """
    input_lower = user_input.lower()

    # 🔧 Skill appris
    for skill in skills.keys():
        if skill in input_lower:
            return {
                "action": "execute_skill",
                "payload": skill
            }

    # 🌐 Recherche web ?
    search_keywords = ["cherche", "recherche", "trouve", "c’est quoi", "qui est", "qu’est-ce que"]
    if any(word in input_lower for word in search_keywords):
        return {
            "action": "search_web",
            "payload": user_input
        }

    # 💬 Sinon, réponse IA par défaut
    return {
        "action": "default",
        "payload": user_input
    }
