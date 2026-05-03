import pyttsx3

print("Mencoba ngomong...")
engine = pyttsx3.init()

# Cek daftar suara yang ada di laptop lu
voices = engine.getProperty('voices')
for voice in voices:
    print(f"Suara terdeteksi: {voice.name}")

# Set suara ke index 0 (biasanya default Windows)
engine.setProperty('voice', voices[0].id) 
engine.setProperty('rate', 150)

engine.say("Halo Bro, ini tes suara satu dua tiga.")
engine.runAndWait()
print("Selesai.")