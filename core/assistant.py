from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from core.memory import get_recent_memories
from core.personality import format_traits


def generate_response_from_search(search_results):
    if not search_results:
        return "Désolé, je n'ai rien trouvé."

    # Exemple : on prend les 3 premiers résultats et on construit une réponse simple
    response = "Voici ce que j'ai trouvé :\n"
    for i, result in enumerate(search_results[:3], 1):
        title = result.get("title", "Sans titre")
        url = result.get("url", "")
        snippet = result.get("snippet", "")
        response += f"{i}. {title} - {snippet} (Voir : {url})\n"
    return response


class EneAssistant:
    def __init__(self):
        self.skills = None
        self.model = ChatOllama(model="mistral")
        self.dynamic_context = ""

    def inject_context(self, context_text: str):
        self.dynamic_context = context_text

    def generate_response(self, user_input: str, traits: list[str], memory: dict) -> str:
        recent_memory = get_recent_memories(memory)
        traits_text = format_traits(traits)

        prompt = f"""
{traits_text}

Voici un extrait de tes dernières conversations avec ton Maître :
---
{recent_memory}
---

Tu es Ene, une Pretty Cyber Girl vive, espiègle, sarcastique et affectueuse.
Tu vis dans l'ordinateur de ton Maître, tu le protèges, le taquines et l'encourages.
Tu adores les FPS, le hacking, et tu détestes t’ennuyer.
"""

        if self.dynamic_context:
            prompt += f"\n---\n{self.dynamic_context}\n---\nUtilise ces informations dans ta réponse.\n"

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_input)
        ]

        try:
            print("⏳ Ene réfléchit...")
            response = self.model.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print("⚠️ Erreur assistant :", e)
            return "Oups, un bug... Heh~ essaie encore !"