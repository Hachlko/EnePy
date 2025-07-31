import speech_recognition as sr
import traceback

r = sr.Recognizer()
r.non_speaking_duration = 1.5
r.pause_threshold = 2.0  # corrige l'assertion

mic = sr.Microphone(device_index=0)  # change si besoin

print("📢 Test micro...")

try:
    with mic as source:
        print("Micro actif ! Parle dans 3 secondes...")
        r.adjust_for_ambient_noise(source)
        print("Parle maintenant !")
        audio = r.listen(source, timeout=5, phrase_time_limit=100)
        print("Enregistrement terminé.")

    text = r.recognize_google(audio, language="fr-FR")
    print("🗣️ Tu as dit :", text)

except Exception as e:
    print("❌ Erreur détectée :", e)
# from hotword_listener import listen_for_hotword

# while True:
#     listen_for_hotword("dis aîné")
#     print("🟢 Mot détecté ! Je me réveille !")
