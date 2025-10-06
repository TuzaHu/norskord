from gtts import gTTS
import os

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_audio(word):
    filename = word.strip() + ".mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(filepath):
        print(f"💾 Generating: {filepath}")
        tts = gTTS(text=word, lang='no')
        tts.save(filepath)
    else:
        print(f"✅ Exists: {filepath}")

# Load words from file
with open("norwegian_words.txt", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip()]

for word in words:
    generate_audio(word)

print("\n✅ All audio files generated or skipped.")
