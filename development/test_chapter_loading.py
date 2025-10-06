#!/usr/bin/env python3
"""
Test script to verify chapter-based word loading
"""

def test_chapter_loading():
    print("🧪 Testing Chapter-Based Word Loading")
    
    try:
        from chapter_based_system import ChapterBasedWordManager
        
        # Initialize chapter manager
        cm = ChapterBasedWordManager()
        print("✅ Chapter manager initialized")
        
        # Get available chapters
        chapters = cm.get_available_chapters()
        print(f"📚 Available chapters: {len(chapters)}")
        
        for chapter in chapters:
            print(f"  - {chapter['name']}: unlocked={chapter['unlocked']}, words={chapter.get('words_count', 0)}")
        
        # Test word loading from first unlocked chapter
        unlocked_chapters = [ch for ch in chapters if ch['unlocked']]
        if unlocked_chapters:
            first_chapter = unlocked_chapters[0]
            words = cm.get_chapter_words(first_chapter['folder'])
            print(f"✅ Loaded {len(words)} words from {first_chapter['name']}")
            
            # Show first few words
            word_list = list(words.keys())[:5]
            print(f"📝 Sample words: {word_list}")
            
            # Test audio file paths
            sample_word = word_list[0] if word_list else None
            if sample_word:
                word_data = words[sample_word]
                audio_file = word_data.get('audio_file')
                print(f"🎵 Sample audio file: {audio_file}")
                
                # Check if audio file exists
                import os
                audio_path = os.path.join("chapters", first_chapter['folder'], "audio", audio_file)
                exists = os.path.exists(audio_path)
                print(f"📁 Audio file exists: {exists}")
                if exists:
                    print(f"✅ Audio path: {audio_path}")
                else:
                    print(f"❌ Audio not found at: {audio_path}")
        else:
            print("❌ No unlocked chapters found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chapter_loading()

