#!/usr/bin/env python3
"""
Export words from chapter system to mobile app format
Creates separate JSON files for each chapter
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'development'))

from translation_service import TranslationService

def load_chapter_words(chapter_path):
    """Load words from a chapter's metadata file"""
    metadata_file = os.path.join(chapter_path, 'data', 'words_metadata.json')
    
    if not os.path.exists(metadata_file):
        return {}
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('words', {})

def export_to_mobile_format():
    """Export words from each chapter to separate mobile-friendly JSON files"""
    
    # Initialize translation service
    translator = TranslationService()
    
    # Path to chapters
    chapters_dir = os.path.join(os.path.dirname(__file__), '..', 'development', 'chapters')
    mobile_dir = os.path.dirname(__file__)
    
    if not os.path.exists(chapters_dir):
        print("❌ Chapters directory not found!")
        return
    
    print("🚀 Exporting words from each chapter separately...")
    print("=" * 60)
    
    # Process each chapter separately
    for chapter_name in sorted(os.listdir(chapters_dir)):
        chapter_path = os.path.join(chapters_dir, chapter_name)
        if not os.path.isdir(chapter_path):
            continue
            
        print(f"\n📚 Processing chapter: {chapter_name}...")
        
        mobile_words = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        
        words = load_chapter_words(chapter_path)
        
        if not words:
            print(f"   ⚠️ No words found in {chapter_name}")
            continue
            
        for word, metadata in words.items():
            # Get translation
            translation = metadata.get('translation')
            if not translation:
                try:
                    translation = translator.get_translation(word)
                except Exception as e:
                    print(f"   ⚠️ Could not translate '{word}': {e}")
                    translation = word
            
            # Determine difficulty
            difficulty = metadata.get('difficulty', 'medium')
            
            # Add to mobile format with audio file path
            audio_file = metadata.get('audio_file', f"{word}.mp3")
            word_entry = {
                'word': word,
                'translation': translation or 'translation not available',
                'audio': f"audio/{audio_file}"  # Path to real MP3 file
            }
            
            mobile_words[difficulty].append(word_entry)
        
        # Write chapter-specific file
        output_file = os.path.join(mobile_dir, f'words_{chapter_name}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mobile_words, f, indent=2, ensure_ascii=False)
        
        total_words = sum(len(words) for words in mobile_words.values())
        print(f"   ✅ Exported {total_words} words to {output_file}")
        print(f"      - Easy: {len(mobile_words['easy'])} words")
        print(f"      - Medium: {len(mobile_words['medium'])} words") 
        print(f"      - Hard: {len(mobile_words['hard'])} words")
    
    print(f"\n🎉 All chapters exported successfully!")
    print(f"📱 Your mobile app now loads words from the selected chapter!")

if __name__ == "__main__":
    export_to_mobile_format()