import speech_recognition as sr
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json

class MicrophoneHandler:
    def __init__(self, device_index=0):
        self.recognizer = sr.Recognizer()
        self.recognizer.non_speaking_duration = 1.5
        self.recognizer.pause_threshold = 2.0
        self.mic = sr.Microphone(device_index=device_index)

    def listen(self, timeout=5, phrase_time_limit=100, language="fr-FR"):
        """Écoute et retourne le texte reconnu."""
        with self.mic as source:
            print("🎙️ Ene: Je t’écoute, Maître~ (parle maintenant...)")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Enregistrement terminé.")
        try:
            text = self.recognizer.recognize_google(audio, language=language)
            print(f"🗣️ Tu as dit : {text}")
            return text
        except sr.WaitTimeoutError:
            print("⌛ Trop de silence.")
            return None
        except sr.UnknownValueError:
            print("🎧 Je n’ai rien compris.")
            return None
        except sr.RequestError as e:
            print(f"❌ Erreur API Google : {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur micro inattendue : {e}")
            return None

# -------------------------------------------------
# Fonction pour détection hotword Vosk

model_path = "models/fr"  # adapte selon l'emplacement de ton modèle Vosk
model = Model(model_path)

def listen_for_hotword(hotword: str, device=None, samplerate=16000, timeout=5):
    """
    Écoute en continu le micro et retourne quand le hotword est détecté.
    timeout : durée en secondes pour attendre des données audio avant de lever une exception.
    """
    q = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        q.put(bytes(indata))

    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(False)

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16',
                           channels=1, callback=audio_callback):
        print(f"🟢 En attente du hotword : '{hotword}' ...")

        while True:
            try:
                data = q.get(timeout=timeout)
            except queue.Empty:
                print("⌛ Timeout : pas de données audio reçues.")
                continue  # ou break si tu veux arrêter l’écoute ici

            if rec.AcceptWaveform(data):
                result = rec.Result()
                result_dict = json.loads(result)
                text = result_dict.get("text", "").lower()
                if hotword.lower() in text:
                    print(f"✅ Hotword détecté : '{hotword}'")
                    return
