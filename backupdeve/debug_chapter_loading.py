#!/usr/bin/env python3
"""
Debug chapter loading issue
"""

def debug_chapter_loading():
    print("🐛 Debugging Chapter Loading")
    
    try:
        from chapter_based_system import ChapterBasedWordManager
        cm = ChapterBasedWordManager()
        
        print(f"Chapter manager exists: {cm is not None}")
        print(f"Has chapter_manager attr: {hasattr(cm, 'chapter_manager')}")
        print(f"Chapter manager type: {type(cm)}")
        
        # Test the exact condition from game engine
        condition_result = hasattr(cm, 'chapter_manager') and cm
        print(f"Condition result: {condition_result}")
        
        # Test with self.chapter_manager
        class MockSelf:
            def __init__(self):
                self.chapter_manager = cm
        
        mock_self = MockSelf()
        condition_result2 = hasattr(mock_self, 'chapter_manager') and mock_self.chapter_manager
        print(f"Condition with self: {condition_result2}")
        
        if condition_result2:
            chapters = mock_self.chapter_manager.get_available_chapters()
            print(f"✅ Got {len(chapters)} chapters")
            
            unlocked = [ch for ch in chapters if ch['unlocked']]
            print(f"🔓 Unlocked chapters: {len(unlocked)}")
            
            if unlocked:
                first_chapter = unlocked[0]
                words = mock_self.chapter_manager.get_chapter_words(first_chapter['folder'])
                print(f"📝 Words from {first_chapter['name']}: {len(words)}")
        else:
            print("❌ Condition failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chapter_loading()

