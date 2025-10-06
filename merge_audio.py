from pydub import AudioSegment
import os

# Settings
AUDIO_DIR = "audio"
OUTPUT_FILE = "all_words_merged.mp3"
MERGED_LOG = "merged_log.txt"
REPEAT_COUNT = 3
SILENCE_BETWEEN_REPEATS_MS = 3000  # 3 seconds

# Load or initialize the log of already-merged files
if os.path.exists(MERGED_LOG):
    with open(MERGED_LOG, "r", encoding="utf-8") as f:
        merged_files = set(line.strip() for line in f if line.strip())
else:
    merged_files = set()

# Silence segment between repeats
silence = AudioSegment.silent(duration=SILENCE_BETWEEN_REPEATS_MS)

# Start with existing merged audio if it exists, otherwise empty
if os.path.exists(OUTPUT_FILE):
    final_audio = AudioSegment.from_mp3(OUTPUT_FILE)
else:
    final_audio = AudioSegment.empty()

# Track new files added
new_files_processed = []

# Process audio files in the folder
for filename in sorted(os.listdir(AUDIO_DIR)):
    if not filename.endswith(".mp3"):
        continue

    filepath = os.path.join(AUDIO_DIR, filename)

    if filename in merged_files:
        print(f"✅ Already merged: {filename}")
        continue

    try:
        word_audio = AudioSegment.from_mp3(filepath)
        repeated_audio = AudioSegment.empty()

        for _ in range(REPEAT_COUNT):
            repeated_audio += word_audio + silence

        final_audio += repeated_audio
        new_files_processed.append(filename)
        print(f"🔄 Added: {filename}")

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

# Save the updated merged audio
if new_files_processed:
    final_audio.export(OUTPUT_FILE, format="mp3")
    print(f"\n🎉 Updated {OUTPUT_FILE} with {len(new_files_processed)} new file(s).")

    with open(MERGED_LOG, "a", encoding="utf-8") as log_file:
        for filename in new_files_processed:
            log_file.write(filename + "\n")
else:
    print("\nℹ️ No new audio files to merge.")
