from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage

# Charger le modèle Mistral depuis Ollama
model = ChatOllama(model="mistral")

# Envoyer une question
response = model.invoke([
    HumanMessage(content="Peux-tu te présenter ?")
])

print(response.content)
