
#!/usr/bin/env python3
"""
Chapter Audio Generator
Reads merged_chapter_x.txt files, generates audio with gTTS, and creates chapter structure
"""

import os
import json
import shutil
import re
import argparse
from pathlib import Path
from datetime import datetime
import requests
from gtts import gTTS

class ChapterAudioGenerator:
    def __init__(self):
        self.base_path = Path("/home/tuza/norskord/development")
        self.development_path = Path("/home/tuza/norskord/development")
        self.chapters_path = self.development_path / "chapters"
        
    def get_english_translation(self, norwegian_word):
        """Get English translation using online dictionary API"""
        try:
            # Try multiple translation services
            translation = self.try_my_memory_api(norwegian_word)
            if translation:
                return translation
                
            # Fallback to simple word mapping for common words
            return self.get_fallback_translation(norwegian_word)
            
        except Exception as e:
            print(f"Translation error for '{norwegian_word}': {e}")
            return f"Translation needed for {norwegian_word}"
    
    def try_my_memory_api(self, word):
        """Try MyMemory translation API"""
        try:
            url = f"https://api.mymemory.translated.net/get?q={word}&langpair=no|en"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('responseStatus') == 200:
                    translation = data['responseData']['translatedText']
                    if translation and translation != word:
                        return translation
        except:
            pass
        return None
    
    def get_fallback_translation(self, word):
        """Fallback translations for common Norwegian words"""
        translations = {
            "hei": "hello",
            "takk": "thanks",
            "ja": "yes", 
            "nei": "no",
            "god": "good",
            "morgen": "morning",
            "kveld": "evening",
            "dag": "day",
            "natt": "night",
            "bærekraftig": "sustainable",
            "forståelse": "understanding",
            "fortjeneste": "profit",
            "forurensning": "pollution",
            "færre": "fewer",
            "anlegg": "facility",
            "produkthåndtering": "product handling",
            "avvikshåndtering": "deviation handling",
            "betjening": "operation",
            "styresystemer": "control systems",
            "unngår": "avoids",
            "orden": "order"
        }
        return translations.get(word.lower(), f"Translation needed for {word}")
    
    def clean_word_name(self, filename):
        """Clean filename to get word name"""
        # Remove .mp3 extension
        word = filename.replace('.mp3', '').replace('.MP3', '')
        # Remove any extra spaces
        word = word.strip()
        return word
    
    def get_difficulty_level(self, word):
        """Determine difficulty based on word characteristics"""
        word = word.strip()
        word_length = len(word)
        word_count = len(word.split())
        
        # Special characters that increase difficulty
        special_chars = len(re.findall(r'[æøåÆØÅ]', word))
        
        # Difficulty criteria
        if word_count == 1:
            if word_length <= 4:
                return "easy"
            elif word_length <= 7:
                return "medium"
            else:
                return "hard"
        elif word_count == 2:
            if word_length <= 8:
                return "easy"
            elif word_length <= 12:
                return "medium"
            else:
                return "hard"
        else:  # 3+ words
            if word_length <= 12:
                return "medium"
            else:
                return "hard"
    
    def generate_audio_file(self, word, output_path):
        """Generate audio file using gTTS"""
        try:
            # Create gTTS object for Norwegian
            tts = gTTS(text=word, lang='no', slow=False)
            
            # Save to file
            audio_filename = f"{word}.mp3"
            audio_path = output_path / audio_filename
            
            tts.save(str(audio_path))
            print(f"🎵 Generated audio: {audio_filename}")
            return audio_filename
            
        except Exception as e:
            print(f"❌ Error generating audio for '{word}': {e}")
            return None
    
    def find_chapter_files(self):
        """Find all merged_chapter_x.txt files"""
        chapter_files = []
        
        for item in self.base_path.iterdir():
            if item.is_file() and item.name.startswith("merged_chapter_") and item.name.endswith(".txt"):
                chapter_files.append(item)
        
        return sorted(chapter_files)
    
    def get_existing_words(self):
        """Get all existing words from all chapters to avoid duplicates"""
        existing_words = set()
        
        if not self.chapters_path.exists():
            return existing_words
        
        for chapter_dir in self.chapters_path.iterdir():
            if chapter_dir.is_dir():
                metadata_file = chapter_dir / "data" / "words_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for word in data.get('words', {}):
                                existing_words.add(word.lower())
                    except Exception as e:
                        print(f"Error reading {metadata_file}: {e}")
        
        return existing_words
    
    def process_chapter_file(self, chapter_file):
        """Process a single merged_chapter_x.txt file"""
        print(f"\n📁 Processing: {chapter_file.name}")
        
        # Extract chapter number
        match = re.search(r'merged_chapter_(\d+)', chapter_file.name)
        if not match:
            print(f"❌ Invalid file name: {chapter_file.name}")
            return False
        
        chapter_num = match.group(1)
        chapter_folder_name = f"capital_{self.number_to_word(chapter_num)}"
        
        # Check if chapter already exists
        chapter_path = self.chapters_path / chapter_folder_name
        if chapter_path.exists():
            print(f"⚠️ Chapter {chapter_folder_name} already exists!")
            # Auto-update if running non-interactively (command-line mode)
            if hasattr(self, 'auto_update') and self.auto_update:
                print("📝 Auto-updating existing chapter...")
            else:
                try:
                    response = input("Do you want to update it? (y/n): ").lower()
                    if response != 'y':
                        return False
                except EOFError:
                    # Non-interactive mode, skip
                    print("⏭️ Skipping (non-interactive mode)")
                    return False
        
        # Get existing words to avoid duplicates
        existing_words = self.get_existing_words()
        
        # Read words from file
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Error reading {chapter_file}: {e}")
            return False
        
        # Load existing words metadata if updating
        words_metadata = {}
        words_metadata_file = chapter_path / "data" / "words_metadata.json"
        if words_metadata_file.exists():
            try:
                with open(words_metadata_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    words_metadata = existing_data.get('words', {})
                    print(f"📖 Loaded {len(words_metadata)} existing words from chapter")
            except Exception as e:
                print(f"⚠️ Could not load existing metadata: {e}")
        
        # Process words
        new_words = 0
        skipped_words = 0
        
        print(f"📝 Found {len(lines)} words in file")
        
        for line in lines:
            word = line.strip()
            if not word or word.startswith('#'):  # Skip empty lines and comments
                continue
            
            # Clean word name
            word_name = self.clean_word_name(word)
            
            # Check for duplicates
            if word_name.lower() in existing_words:
                print(f"⚠️ Skipping duplicate word: {word_name}")
                skipped_words += 1
                continue
            
            # Create chapter structure
            self.create_chapter_structure(chapter_path)
            
            # Generate audio file
            audio_filename = self.generate_audio_file(word_name, chapter_path / "audio")
            if not audio_filename:
                print(f"❌ Failed to generate audio for: {word_name}")
                continue
            
            # Get English translation
            print(f"🔍 Getting translation for: {word_name}")
            translation = self.get_english_translation(word_name)
            
            # Determine difficulty
            difficulty = self.get_difficulty_level(word_name)
            
            # Add to metadata
            words_metadata[word_name] = {
                "audio_file": audio_filename,
                "difficulty": difficulty,
                "category": "general",
                "chapter": chapter_num,
                "tags": [],
                "translation": translation,
                "last_updated": datetime.now().isoformat(),
                "auto_generated": True
            }
            
            existing_words.add(word_name.lower())
            new_words += 1
            print(f"✅ Added: {word_name} ({difficulty}) - {translation}")
        
        # Save words metadata
        words_metadata_file = chapter_path / "data" / "words_metadata.json"
        with open(words_metadata_file, 'w', encoding='utf-8') as f:
            json.dump({"words": words_metadata}, f, ensure_ascii=False, indent=2)
        
        # Get total word count (including existing words)
        total_words = len(words_metadata)
        
        # Load existing chapter metadata if updating
        chapter_metadata_file = chapter_path / "data" / "chapter_metadata.json"
        existing_metadata = {}
        if chapter_metadata_file.exists():
            try:
                with open(chapter_metadata_file, 'r', encoding='utf-8') as f:
                    existing_metadata = json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load existing chapter metadata: {e}")
        
        # Create/update chapter metadata (preserve existing values)
        chapter_metadata = {
            "name": f"Kapital {self.number_to_norwegian(chapter_num)}",
            "folder": chapter_folder_name,
            "description": f"Norwegian words and phrases - Chapter {chapter_num}",
            "unlocked": existing_metadata.get("unlocked", False),
            "required_score": existing_metadata.get("required_score", 70),
            "words_count": total_words,
            "best_score": existing_metadata.get("best_score", 0),
            "attempts": existing_metadata.get("attempts", 0),
            "created_date": existing_metadata.get("created_date", datetime.now().isoformat()),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(chapter_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(chapter_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Chapter {chapter_folder_name} created successfully!")
        print(f"📊 Added {new_words} new words, skipped {skipped_words} duplicates")
        print(f"🎵 Audio files generated in: {chapter_path / 'audio'}")
        print(f"📄 Metadata saved to: {chapter_path / 'data'}")
        
        return True
    
    def create_chapter_structure(self, chapter_path):
        """Create the folder structure for a chapter"""
        # Create directories
        (chapter_path / "audio").mkdir(parents=True, exist_ok=True)
        (chapter_path / "data").mkdir(parents=True, exist_ok=True)
    
    def number_to_word(self, num):
        """Convert number to word (1->one, 2->two, etc.)"""
        numbers = {
            "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
            "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"
        }
        return numbers.get(num, f"chapter_{num}")
    
    def number_to_norwegian(self, num):
        """Convert number to Norwegian word"""
        numbers = {
            "1": "En", "2": "To", "3": "Tre", "4": "Fire", "5": "Fem",
            "6": "Seks", "7": "Sju", "8": "Åtte", "9": "Ni", "10": "Ti"
        }
        return numbers.get(num, f"Kapittel {num}")
    
    def run(self, chapter_number=None, auto_update=False):
        """Main execution function"""
        self.auto_update = auto_update
        
        print("🚀 Chapter Audio Generator - Processing merged_chapter_x.txt files")
        print("=" * 70)
        
        # Check if gTTS is available
        try:
            from gtts import gTTS
            print("✅ gTTS (Google Text-to-Speech) is available")
        except ImportError:
            print("❌ gTTS not installed. Install with: pip install gtts")
            return
        
        # Find chapter files
        if chapter_number:
            # Process specific chapter
            chapter_file = self.base_path / f"merged_chapter_{chapter_number}.txt"
            if not chapter_file.exists():
                print(f"❌ File not found: {chapter_file.name}")
                return
            chapter_files = [chapter_file]
        else:
            # Find all chapter files
            chapter_files = self.find_chapter_files()
        
        if not chapter_files:
            print("❌ No merged_chapter_x.txt files found!")
            print("\nExpected file names:")
            print("  - merged_chapter_1.txt")
            print("  - merged_chapter_2.txt") 
            print("  - merged_chapter_3.txt")
            print("  - etc.")
            return
        
        print(f"📁 Found {len(chapter_files)} chapter files:")
        for file in chapter_files:
            print(f"  - {file.name}")
        
        # Process each file
        success_count = 0
        for chapter_file in chapter_files:
            if self.process_chapter_file(chapter_file):
                success_count += 1
        
        print("\n" + "=" * 70)
        print(f"🎉 Processing complete!")
        print(f"✅ Successfully created/updated {success_count} chapters")
        print(f"📚 Your chapters are ready to use in the app!")
        print(f"🎵 All audio files generated with Norwegian TTS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate audio files for Norwegian learning chapters')
    parser.add_argument('--chapter', type=int, help='Chapter number to process (e.g., 3 for merged_chapter_3.txt)')
    parser.add_argument('--auto-update', action='store_true', help='Automatically update existing chapters without prompting')
    args = parser.parse_args()
    
    generator = ChapterAudioGenerator()
    generator.run(chapter_number=args.chapter, auto_update=args.auto_update)
