from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Charger le PDF
loader = PyPDFLoader("Projet_Ene.pdf")
pages = loader.load()

# Découper le texte en morceaux exploitables
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
documents = text_splitter.split_documents(pages)

# Ajouter au contexte dynamique de l'agent
context = "\n".join([doc.page_content for doc in documents[:3]])  # on prend les 3 premiers morceaux par ex.

#Interaction type à utiliser
#messages = [
    #SystemMessage(content=ene_system_prompt),
    #HumanMessage(content=f"Ene, voici un document que j’ai retrouvé sur toi :\n{context}\nTu veux bien m’en parler ?"),
#]

