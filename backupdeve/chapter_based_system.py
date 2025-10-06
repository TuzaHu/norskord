"""
Chapter-Based Learning System for Norwegian Words
Organized by chapters with progressive unlocking
"""

import os
import json
import shutil
from typing import Dict, List, Optional


class ChapterBasedWordManager:
    """
    Manages words organized by chapters with progressive unlocking
    """
    
    def __init__(self, base_directory: str = "chapters"):
        self.base_directory = base_directory
        self.chapters_data = {}
        self.chapter_progress_file = "chapter_progress.json"
        self.progress_data = self.load_chapter_progress()
        self.ensure_chapter_structure()
    
    def ensure_chapter_structure(self):
        """Ensure the chapter directory structure exists"""
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
        
        # Create example chapter structure
        self.create_chapter_structure()
    
    def create_chapter_structure(self):
        """Create the organized chapter structure"""
        chapters = [
            {
                "name": "Kapital En",
                "folder": "capital_one",
                "description": "Basic Norwegian words and phrases",
                "required_score": 0,  # First chapter is always unlocked
                "words": []  # Will be populated when you provide the data
            },
            {
                "name": "Kapital To", 
                "folder": "capital_two",
                "description": "Intermediate Norwegian vocabulary",
                "required_score": 70,  # Need 70% in previous chapter
                "words": []
            },
            {
                "name": "Kapital Tre",
                "folder": "capital_three", 
                "description": "Advanced Norwegian expressions",
                "required_score": 70,  # Need 70% in previous chapter
                "words": []
            }
        ]
        
        for chapter in chapters:
            chapter_path = os.path.join(self.base_directory, chapter["folder"])
            
            # Create chapter directory
            if not os.path.exists(chapter_path):
                os.makedirs(chapter_path)
            
            # Create subdirectories
            os.makedirs(os.path.join(chapter_path, "audio"), exist_ok=True)
            os.makedirs(os.path.join(chapter_path, "data"), exist_ok=True)
            
            # Create chapter metadata file
            metadata_file = os.path.join(chapter_path, "chapter_metadata.json")
            if not os.path.exists(metadata_file):
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "name": chapter["name"],
                        "folder": chapter["folder"],
                        "description": chapter["description"],
                        "required_score": chapter["required_score"],
                        "words_count": 0,
                        "created_date": "2024-01-01T00:00:00",
                        "last_updated": "2024-01-01T00:00:00"
                    }, f, indent=2, ensure_ascii=False)
            
            # Create words metadata file for this chapter
            words_file = os.path.join(chapter_path, "data", "words_metadata.json")
            if not os.path.exists(words_file):
                with open(words_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "words": {},
                        "last_updated": "2024-01-01T00:00:00"
                    }, f, indent=2, ensure_ascii=False)
    
    def load_chapter_progress(self) -> Dict:
        """Load chapter progress and unlocking status"""
        default_progress = {
            "chapters": {
                "capital_one": {
                    "unlocked": True,
                    "completed": False,
                    "best_score": 0,
                    "attempts": 0,
                    "last_attempt": None
                },
                "capital_two": {
                    "unlocked": False,
                    "completed": False,
                    "best_score": 0,
                    "attempts": 0,
                    "last_attempt": None
                },
                "capital_three": {
                    "unlocked": False,
                    "completed": False,
                    "best_score": 0,
                    "attempts": 0,
                    "last_attempt": None
                }
            },
            "current_chapter": "capital_one",
            "total_chapters": 3
        }
        
        if os.path.exists(self.chapter_progress_file):
            try:
                with open(self.chapter_progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    # Merge with defaults to handle new chapters
                    default_progress.update(progress)
            except Exception as e:
                print(f"Error loading progress: {e}")
        
        return default_progress
    
    def save_chapter_progress(self):
        """Save chapter progress"""
        try:
            with open(self.chapter_progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def get_available_chapters(self) -> List[Dict]:
        """Get list of available (unlocked) chapters"""
        available = []
        
        for chapter_folder in os.listdir(self.base_directory):
            chapter_path = os.path.join(self.base_directory, chapter_folder)
            if os.path.isdir(chapter_path):
                metadata_file = os.path.join(chapter_path, "chapter_metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        chapter_info = json.load(f)
                    
                    # Check if chapter is unlocked
                    chapter_key = chapter_info["folder"]
                    is_unlocked = self.progress_data["chapters"].get(chapter_key, {}).get("unlocked", False)
                    
                    chapter_info["unlocked"] = is_unlocked
                    chapter_info["progress"] = self.progress_data["chapters"].get(chapter_key, {})
                    available.append(chapter_info)
        
        # Sort by required score
        available.sort(key=lambda x: x.get("required_score", 0))
        return available
    
    def unlock_next_chapter(self, current_chapter: str, score: float):
        """Unlock next chapter if score is sufficient"""
        current_chapter_key = current_chapter
        
        # Update current chapter progress
        if current_chapter_key in self.progress_data["chapters"]:
            self.progress_data["chapters"][current_chapter_key]["best_score"] = max(
                self.progress_data["chapters"][current_chapter_key]["best_score"], 
                score
            )
            self.progress_data["chapters"][current_chapter_key]["attempts"] += 1
            
            if score >= 70:
                self.progress_data["chapters"][current_chapter_key]["completed"] = True
        
        # Check if next chapter should be unlocked
        available_chapters = self.get_available_chapters()
        for chapter in available_chapters:
            if chapter["required_score"] <= score and not chapter["unlocked"]:
                chapter_key = chapter["folder"]
                self.progress_data["chapters"][chapter_key]["unlocked"] = True
                print(f"🎉 Chapter '{chapter['name']}' unlocked!")
        
        self.save_chapter_progress()
    
    def get_chapter_words(self, chapter_folder: str) -> Dict:
        """Get words for a specific chapter"""
        chapter_path = os.path.join(self.base_directory, chapter_folder)
        words_file = os.path.join(chapter_path, "data", "words_metadata.json")
        
        if os.path.exists(words_file):
            with open(words_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("words", {})
        return {}
    
    def add_words_to_chapter(self, chapter_folder: str, words_data: Dict, audio_files: List[str]):
        """Add words and audio files to a specific chapter"""
        chapter_path = os.path.join(self.base_directory, chapter_folder)
        
        # Ensure chapter exists
        if not os.path.exists(chapter_path):
            print(f"Chapter '{chapter_folder}' does not exist!")
            return False
        
        # Update words metadata
        words_file = os.path.join(chapter_path, "data", "words_metadata.json")
        
        # Load existing words
        if os.path.exists(words_file):
            with open(words_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {"words": {}, "last_updated": "2024-01-01T00:00:00"}
        
        # Add new words
        for word, data in words_data.items():
            metadata["words"][word] = data
        
        # Save updated metadata
        with open(words_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Copy audio files to chapter's audio directory
        audio_dir = os.path.join(chapter_path, "audio")
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                destination = os.path.join(audio_dir, os.path.basename(audio_file))
                shutil.copy2(audio_file, destination)
                print(f"Copied audio: {os.path.basename(audio_file)}")
        
        # Update chapter metadata
        metadata_file = os.path.join(chapter_path, "chapter_metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                chapter_info = json.load(f)
            
            chapter_info["words_count"] = len(metadata["words"])
            chapter_info["last_updated"] = "2024-01-15T10:30:00"  # Current timestamp
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Added {len(words_data)} words to chapter '{chapter_folder}'")
        return True
    
    def migrate_existing_data(self):
        """Migrate existing words_metadata.json to chapter structure"""
        if not os.path.exists("words_metadata.json"):
            print("No existing words_metadata.json found!")
            return
        
        # Load existing data
        with open("words_metadata.json", 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Copy audio files
        audio_files = []
        if os.path.exists("audio"):
            for file in os.listdir("audio"):
                if file.endswith('.mp3'):
                    audio_files.append(os.path.join("audio", file))
        
        # Add to Capital One
        self.add_words_to_chapter("capital_one", existing_data["words"], audio_files)
        
        print("✅ Migrated existing data to chapter structure!")
    
    def get_chapter_statistics(self) -> Dict:
        """Get statistics for all chapters"""
        stats = {
            "total_chapters": 0,
            "unlocked_chapters": 0,
            "completed_chapters": 0,
            "total_words": 0,
            "chapters": {}
        }
        
        for chapter_folder in os.listdir(self.base_directory):
            chapter_path = os.path.join(self.base_directory, chapter_folder)
            if os.path.isdir(chapter_path):
                stats["total_chapters"] += 1
                
                # Get chapter info
                metadata_file = os.path.join(chapter_path, "chapter_metadata.json")
                words_file = os.path.join(chapter_path, "data", "words_metadata.json")
                
                chapter_info = {}
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        chapter_info = json.load(f)
                
                # Count words
                word_count = 0
                if os.path.exists(words_file):
                    with open(words_file, 'r', encoding='utf-8') as f:
                        words_data = json.load(f)
                        word_count = len(words_data.get("words", {}))
                
                # Check progress
                chapter_key = chapter_folder
                progress = self.progress_data["chapters"].get(chapter_key, {})
                
                chapter_stats = {
                    "name": chapter_info.get("name", chapter_folder),
                    "words_count": word_count,
                    "unlocked": progress.get("unlocked", False),
                    "completed": progress.get("completed", False),
                    "best_score": progress.get("best_score", 0),
                    "attempts": progress.get("attempts", 0)
                }
                
                stats["chapters"][chapter_folder] = chapter_stats
                
                if chapter_stats["unlocked"]:
                    stats["unlocked_chapters"] += 1
                if chapter_stats["completed"]:
                    stats["completed_chapters"] += 1
                
                stats["total_words"] += word_count
        
        return stats


def main():
    """Demo of the chapter-based system"""
    print("📚 Chapter-Based Learning System Demo")
    print("=" * 50)
    
    # Initialize chapter manager
    chapter_manager = ChapterBasedWordManager()
    
    # Show available chapters
    chapters = chapter_manager.get_available_chapters()
    print(f"\n📖 Available Chapters:")
    for chapter in chapters:
        status = "🔓 Unlocked" if chapter["unlocked"] else "🔒 Locked"
        print(f"  • {chapter['name']} - {status} ({chapter['words_count']} words)")
    
    # Show statistics
    stats = chapter_manager.get_chapter_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total chapters: {stats['total_chapters']}")
    print(f"  Unlocked: {stats['unlocked_chapters']}")
    print(f"  Completed: {stats['completed_chapters']}")
    print(f"  Total words: {stats['total_words']}")
    
    # Demo unlocking next chapter
    print(f"\n🎯 Demo: Completing Capital One with 75% score")
    chapter_manager.unlock_next_chapter("capital_one", 75.0)
    
    # Show updated status
    chapters = chapter_manager.get_available_chapters()
    print(f"\n📖 Updated Chapter Status:")
    for chapter in chapters:
        status = "🔓 Unlocked" if chapter["unlocked"] else "🔒 Locked"
        print(f"  • {chapter['name']} - {status}")


if __name__ == "__main__":
    main()
