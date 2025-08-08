import pyttsx3
import speech_recognition as sr
from core.mic import listen_for_hotword  # détection du hotword via Vosk

class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # Vitesse de la voix
        self.engine.setProperty('volume', 1.0)
        voices = self.engine.getProperty('voices')

        # Voix féminine si dispo
        for voice in voices:
            if "female" in voice.name.lower() or "femme" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def say(self, text: str):
        # print(f"Ene : {text}")
        self.engine.say(text)
        self.engine.runAndWait()

def listen_hotword_then_transcribe(voice_engine: VoiceEngine) -> str:
    recognizer = sr.Recognizer()

    # Étape 1 : détecter le hotword avec Vosk
    listen_for_hotword("dis aîné")

    # Étape 2 : écouter et transcrire
    with sr.Microphone() as source:
        print("🎤 Parle, je t’écoute...")
        voice_engine.say("Heh~ je t’écoute, vas-y.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        print("🗣️ Tu as dit :", text)
        return text
    except sr.UnknownValueError:
        voice_engine.say("J’ai rien capté. Tu peux répéter ?")
    except sr.RequestError:
        voice_engine.say("Je capte plus le serveur... Essaye encore.")
    return ""
