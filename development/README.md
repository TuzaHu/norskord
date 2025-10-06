# 🇳🇴 Norskord - Norwegian Language Learning Game

A professional Norwegian language learning application with progressive chapter-based system, audio pronunciation, and intelligent word management.

---

## 📁 Project Structure

```
development/
├── ma.py                           # 🎮 MAIN GAME - Run this to play
├── generate_chapter_audio.py       # 🎵 Chapter Audio Generator
├── chapter_based_system.py         # 📚 Chapter Management System
├── translation_service.py          # 🔤 Translation Service
├── chapters/                       # 📂 Chapter Data
│   ├── capital_one/               # Chapter 1 (Always Unlocked)
│   ├── capital_two/               # Chapter 2 (Unlocks at 70%)
│   └── capital_three/             # Chapter 3 (Unlocks at 70%)
├── audio/                          # 🎵 Main Audio Files
├── game_stats.json                 # 📊 Game Statistics
├── words_metadata.json             # 📝 Words Database
└── words_to_review.json            # 🔄 SRS Review System
```

---

## 🚀 Quick Start

### **1. Run the Game**
```bash
python3 ma.py
```

### **2. Game Features**
- ✅ Progressive chapter system
- ✅ 3 difficulty levels (Easy/Medium/Hard)
- ✅ Practice & Action modes
- ✅ Audio pronunciation
- ✅ Spaced repetition system (SRS)
- ✅ Statistics tracking
- ✅ Chapter unlocking (70% threshold)

---

## 📚 How to Add New Chapters

### **Step 1: Create Word List**
Create a file named `merged_chapter_X.txt` where X is the chapter number:

```bash
# Example: merged_chapter_2.txt
rekvisita
småstopp
prosesstyring
god morgen
tusen takk
```

**Format:** One Norwegian word/phrase per line (no .mp3 extension needed)

### **Step 2: Generate Chapter**
```bash
python3 generate_chapter_audio.py
```

### **What It Does:**
1. ✅ Reads words from `merged_chapter_X.txt`
2. ✅ Generates Norwegian audio using Google TTS
3. ✅ Fetches English translations from online API
4. ✅ Determines difficulty automatically:
   - **Easy**: Short words (1-4 chars, 1 word)
   - **Medium**: Medium length (5-7 chars or 2 words)
   - **Hard**: Long words (8+ chars or 3+ words)
5. ✅ Creates chapter structure in `chapters/capital_X/`
6. ✅ Avoids duplicate words across chapters
7. ✅ Updates chapter metadata

### **Step 3: Play!**
The new chapter will automatically appear in the game's chapter dropdown (locked until you achieve 70% in the previous chapter).

---

## 🎮 How to Play

### **Main Menu**
1. **Start Game** - Begin learning session
2. **Settings** ⚙️ - Configure game options
3. **Statistics** 📊 - View your progress
4. **Exit** - Close the game

### **Settings**
- **Chapter Selection**: Choose from unlocked chapters (✅ green = unlocked, 🔒 grey = locked)
- **Difficulty**: Easy, Medium, Hard
- **Words per Session**: 5-20 words
- **Translation**: Show/hide English translations
- **Game Mode**: Practice (learning) or Action (timed challenge)

### **Progressive Unlocking**
- **Capital One** - Always unlocked (your starter words)
- **Capital Two** - Unlocks after 70% score in Capital One
- **Capital Three** - Unlocks after 70% score in Capital Two
- **And so on...** - Add as many chapters as you want!

---

## 🛠️ Technical Details

### **Requirements**
```bash
# Python packages
pip install pygame tkinter gtts requests --break-system-packages
```

### **File Descriptions**

#### **ma.py** (Main Game)
- Complete game interface
- Chapter dropdown with visual indicators
- Scrollable settings window
- Audio playback system
- Statistics tracking
- Spaced repetition system

#### **generate_chapter_audio.py** (Chapter Creator)
- Reads `merged_chapter_X.txt` files
- Generates Norwegian TTS audio using gTTS
- Fetches translations via MyMemory API
- Auto-categorizes difficulty
- Creates JSON metadata
- Prevents word duplication

#### **chapter_based_system.py** (Chapter Manager)
- Manages chapter metadata
- Tracks unlock status
- Handles progression logic
- Stores best scores and attempts

#### **translation_service.py** (Translation)
- Online dictionary API integration
- Fallback translation support
- Caches translations

---

## 📝 Example: Adding Chapter 4

### **1. Create word list**
```bash
# File: merged_chapter_4.txt
avansert
komplisert
gjennomføring
implementering
strategisk planlegging
```

### **2. Run generator**
```bash
python3 generate_chapter_audio.py
```

### **3. Output**
```
✅ Chapter capital_four created successfully!
📊 Added 5 new words, skipped 0 duplicates
🎵 Audio files generated in: chapters/capital_four/audio
📄 Metadata saved to: chapters/capital_four/data
```

### **4. Play the game**
- Complete Capital Three with 70%+ score
- Capital Four automatically unlocks
- Select it from the chapter dropdown
- Start learning!

---

## 🎯 Difficulty Criteria

The system automatically determines difficulty:

| Category | Single Word | Multiple Words | Example |
|----------|-------------|----------------|---------|
| **Easy** | 1-4 characters | 2 words, ≤8 chars | "hei", "ja", "takk" |
| **Medium** | 5-7 characters | 2 words, 9-12 chars | "morgen", "god dag" |
| **Hard** | 8+ characters | 3+ words | "bærekraftig", "ha det bra" |

---

## 📊 Game Statistics

The game tracks:
- Total words learned
- Accuracy percentage
- Current streak
- Best streak
- Session history
- Per-chapter performance

View statistics by clicking the **Statistics** button in the main menu.

---

## 🔄 Spaced Repetition System (SRS)

Words you miss are automatically added to a review list with increasing intervals:
- First review: Next session
- Correct: Interval increases
- Incorrect: Interval resets

This helps you master difficult words over time.

---

## 🌐 Translation Sources

Translations are fetched from:
1. **MyMemory Translation API** (primary)
2. **Fallback dictionary** (backup for common words)

If translation fails, you can manually add it in the game or update the JSON metadata.

---

## 🎨 Visual Features

- **Modern UI** - Clean, professional design
- **Color Coding**:
  - 🟢 Green: Unlocked chapters, active elements
  - ⚫ Grey: Locked chapters, disabled elements
  - 🔵 Blue: Interactive elements
  - 🔴 Red: Errors, warnings
- **Icons**: ✅ (unlocked), 🔒 (locked), ⚙️ (settings), 📊 (stats)
- **Scrollable Settings** - Access all options easily

---

## 💡 Tips for Best Results

1. **Start with Capital One** - Master basics first
2. **Aim for 70%+** - Unlock new chapters
3. **Use Practice Mode** - When learning new words
4. **Try Action Mode** - For quick challenges
5. **Review Regularly** - Check SRS words
6. **Monitor Stats** - Track your progress
7. **Add Custom Chapters** - Tailor to your learning needs

---

## 🐛 Troubleshooting

### **No audio playing?**
- Check audio files exist in `chapters/capital_X/audio/`
- Verify pygame is installed: `pip install pygame`

### **Translation not working?**
- Check internet connection (uses online API)
- Fallback translations still work offline

### **Chapter not appearing?**
- Ensure `merged_chapter_X.txt` is in the development folder
- Run `python3 generate_chapter_audio.py`
- Check for errors in the output

### **Can't unlock next chapter?**
- Score 70%+ in current chapter
- Complete a full session (not just a few words)
- Check chapter metadata in `chapters/capital_X/data/chapter_metadata.json`

---

## 📜 License & Credits

**Developer**: Professional Norwegian Learning System  
**Version**: 2.0  
**Date**: September 2025  

**Technologies**:
- Python 3
- Tkinter (GUI)
- Pygame (Audio)
- gTTS (Text-to-Speech)
- MyMemory API (Translations)

---

## 🚀 Future Enhancements

Want to add features? Here are some ideas:
- [ ] More translation sources
- [ ] Offline TTS support
- [ ] Custom difficulty overrides
- [ ] Word categories/tags filtering
- [ ] Export/import chapters
- [ ] Multiplayer mode
- [ ] Leaderboards
- [ ] Mobile app version

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review the code comments
3. Test with the example chapter files
4. Verify all dependencies are installed

---

**Happy Learning! 🇳🇴📚**

**Lykke til med norsk!** (Good luck with Norwegian!)

