#!/usr/bin/env python3
"""
Test script to verify game engine word loading
"""

def test_game_engine_loading():
    print("🧪 Testing Game Engine Word Loading")
    
    try:
        # Import and initialize chapter manager first
        from chapter_based_system import ChapterBasedWordManager
        cm = ChapterBasedWordManager()
        print("✅ Chapter manager initialized")
        
        # Test the same logic as in game engine
        words_data = {}
        
        # Try to load from chapter system first
        if cm:
            try:
                # Get available chapters
                chapters = cm.get_available_chapters()
                print(f"📚 Found {len(chapters)} chapters")
                
                for chapter in chapters:
                    if chapter['unlocked']:
                        print(f"🔓 Processing unlocked chapter: {chapter['name']}")
                        chapter_words = cm.get_chapter_words(chapter['folder'])
                        print(f"📝 Got {len(chapter_words)} words from {chapter['name']}")
                        
                        for word, data in chapter_words.items():
                            words_data[word] = {
                                'audio_file': data['audio_file'],
                                'length': len(word),
                                'word_count': len(word.split()),
                                'translation': data.get('translation'),
                                'difficulty': data.get('difficulty', 'medium'),
                                'chapter': data.get('chapter')
                            }
                
                if words_data:
                    print(f"✅ Loaded {len(words_data)} words from chapter system")
                    print(f"📝 Sample words: {list(words_data.keys())[:5]}")
                    return words_data
                    
            except Exception as e:
                print(f"⚠️ Error loading from chapter system: {e}")
                import traceback
                traceback.print_exc()
        
        print("⚠️ Fallback: No words loaded from chapter system")
        return {}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    words = test_game_engine_loading()
    print(f"🎯 Final result: {len(words)} words loaded")
