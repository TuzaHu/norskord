#!/usr/bin/env python3
"""
Test game engine initialization
"""

def test_game_init():
    print("🧪 Testing Game Engine Initialization")
    
    try:
        from game_engine import DuolingoStyleDictationGame
        
        print("Creating game instance...")
        game = DuolingoStyleDictationGame()
        
        print(f"✅ Game created successfully")
        print(f"📊 Words loaded: {len(game.words_data)}")
        print(f"📚 Chapter manager: {game.chapter_manager is not None}")
        
        if game.chapter_manager:
            chapters = game.chapter_manager.get_available_chapters()
            unlocked = [ch for ch in chapters if ch['unlocked']]
            print(f"🔓 Unlocked chapters: {len(unlocked)}")
            
            if unlocked:
                first_chapter = unlocked[0]
                words = game.chapter_manager.get_chapter_words(first_chapter['folder'])
                print(f"📝 Words in {first_chapter['name']}: {len(words)}")
        
        # Test audio path resolution
        if game.words_data:
            sample_word = list(game.words_data.keys())[0]
            audio_file = game.words_data[sample_word]['audio_file']
            audio_path = game.get_audio_file_path(audio_file)
            print(f"🎵 Sample audio path: {audio_path}")
            print(f"📁 Audio exists: {audio_path and os.path.exists(audio_path)}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import os
    test_game_init()

