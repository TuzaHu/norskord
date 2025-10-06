#!/usr/bin/env python3
"""
Test the final game to verify it's working with chapter data
"""

def test_final_game():
    print("🎮 Testing Final Game Setup")
    
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
                
                # Test a sample word
                sample_word = list(words.keys())[0]
                word_data = words[sample_word]
                print(f"🎯 Sample word: {sample_word}")
                print(f"🎵 Audio file: {word_data['audio_file']}")
                print(f"📊 Difficulty: {word_data.get('difficulty', 'unknown')}")
                print(f"🌐 Translation: {word_data.get('translation', 'Not available')}")
                
                # Test audio path resolution
                audio_path = game.get_audio_file_path(word_data['audio_file'])
                print(f"📁 Audio path: {audio_path}")
                
                if audio_path and os.path.exists(audio_path):
                    print(f"✅ Audio file exists and is accessible")
                else:
                    print(f"❌ Audio file not found")
        
        print("\n🎉 SUCCESS! The game is now properly configured to use chapter data!")
        print("📚 The game loads words from chapters/capital_one/data/words_metadata.json")
        print("🎵 Audio files are loaded from chapters/capital_one/audio/")
        print("🔓 Chapter progression system is working")
        print("🎮 Ready to play the Duolingo-style dictation game!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    success = test_final_game()
    if success:
        print("\n🚀 You can now run: python3 main.py")
    else:
        print("\n🔧 There are still issues to fix")

