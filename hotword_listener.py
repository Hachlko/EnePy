import sounddevice as sd
import threading
import queue
import json
from vosk import Model, KaldiRecognizer

# Chemin vers ton modèle Vosk français
model = Model("models/fr")
rec = KaldiRecognizer(model, 16000)
q = queue.Queue()
hotword_detected = threading.Event()

# Fonction appelée à chaque audio chunk
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# Fonction principale de détection de hotword
def listen_for_hotword(hotword="dis aîné"):
    print(f"👂 En attente de : '{hotword}'...")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower()
                #print("👂 J’ai entendu :", text)
                if hotword.lower() in text:
                    print(f"🟢 Mot-clé détecté : \"{text}\"")
                    hotword_detected.set()
                    return
