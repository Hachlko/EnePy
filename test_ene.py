import os, json, time
import openai

# 1) Renseigne ici ta clé
openai.api_key = os.getenv("OPENAI_API_KEY") 

# 2) On charge ta fiche de personnalité
with open("Projet Ene.pdf", "rb") as f:
    doc = f.read()  # ou extrait de texte

system_prompt = """
Tu incarnes Ene (Takane Enomoto), la super pretty cyber girl. 
Ta personnalité est très taquine, espiègle, affectueuse, 
avec un ton « Heh~ », des analogies informatiques, des taquineries sur “Maître”, 
mais aussi des moments de compassion ou d’anxiété quand l’utilisateur est triste.
"""

# 3) Fonction de génération
def generate_prompts(n=300):
    dataset = []
    seen = set()
    for i in range(n):
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role":"system", "content": system_prompt},
                {"role":"user", "content": (
                    "Génère une paire unique instruction/réponse dans le style d’Ene, "
                    "basée sur sa fiche de personnalité (évite les doublons). "
                    "Format JSON : {\"instruction\": \"…\", \"response\": \"…\"}." 
                )}
            ],
            temperature=1.0,
            max_tokens=100
        )
        text = resp.choices[0].message.content.strip()
        try:
            entry = json.loads(text)
            key = entry["instruction"] + entry["response"]
            if key in seen:
                i -= 1
                continue
            seen.add(key)
            dataset.append(entry)
        except:
            continue
        time.sleep(0.5)
    with open("ene_prompts_300.jsonl", "w", encoding="utf-8") as f:
        for e in dataset:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"✅ Généré {len(dataset)} prompts uniques → ene_prompts_300.jsonl")

if __name__ == "__main__":
    generate_prompts(300)
