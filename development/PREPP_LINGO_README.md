# 🚀 PREPP-Lingo - Advanced Norwegian Language Learning Platform

## 🎯 Overview
PREPP-Lingo is a futuristic, modern Norwegian language learning application featuring a sleek dark theme interface with advanced dictation training capabilities.

## ✨ Features

### 🎨 Modern UI Design
- **Futuristic Dark Theme** with cyber-blue color scheme
- **Electric blue primary colors** (#00d4ff) with orange accents (#ff6b35)
- **Glass morphism effects** with dark slate backgrounds
- **Hexagonal futuristic logo** with animated glow effects
- **SF Pro Display typography** for professional appearance

### 🎮 Game Features
- **Audio Dictation Training** with Norwegian text-to-speech
- **Chapter-based Learning Progression** with 70% unlock threshold
- **Hearts & Hints System** for assistance
- **Dynamic Difficulty Levels** (Easy, Medium, Hard)
- **Progress Tracking** with streaks and XP
- **English Translations** via online API
- **Settings Configuration** with modern dark theme

### 🔧 Technical Features
- **Modular Architecture** with separate components
- **Chapter Audio Generator** for easy content creation
- **Translation Service** with fallback dictionaries
- **JSON-based Word Management** with rich metadata
- **Threaded Audio Playback** for smooth performance

## 🚀 Getting Started

### Prerequisites
```bash
pip install pygame pydub gtts requests
```

### Running the Application
```bash
cd /home/tuza/norskord/development
python3 main.py
```

### Creating New Chapters
1. Create a text file named `merged_chapter_X.txt` (where X is the chapter number)
2. Add one Norwegian word or phrase per line
3. Run the chapter generator:
```bash
python3 generate_chapter_audio.py
```

## 🎯 User Interface

### Main Interface
- **Header**: PREPP-Lingo logo, streak display, XP counter, settings button
- **Progress Section**: Hearts display, circular progress indicator, current settings
- **Lesson Card**: Word display, translation, input field
- **Controls**: Play audio, submit, hint, start session buttons

### Settings Window
- **Dark Theme Modal** with modern styling
- **Chapter Selection** with visual status indicators
- **Difficulty Configuration** with modern radio buttons
- **Translation Toggle** and other preferences
- **Scrollable Interface** for easy navigation

## 🎨 Color Scheme
- **Primary**: Electric Blue (#00d4ff)
- **Accent**: Orange (#ff6b35)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Error**: Red (#ef4444)
- **Dark**: Slate (#0f172a)
- **Dark Light**: Lighter Slate (#1e293b)

## 📁 File Structure
```
development/
├── main.py                    # Application entry point
├── game_engine.py            # Core game logic with modern UI
├── chapter_based_system.py   # Chapter management
├── translation_service.py    # Translation API integration
├── generate_chapter_audio.py # Audio generation script
├── chapters/                 # Chapter data
│   ├── capital_one/
│   ├── capital_two/
│   └── capital_three/
└── audio/                    # Audio files
```

## 🔧 Development

### Key Components
- **PREPPLingoGame**: Main game class with modern UI
- **ChapterManager**: Handles chapter progression and unlocking
- **TranslationService**: Provides English translations
- **ChapterAudioGenerator**: Creates audio and metadata from text files

### UI Components
- **Modern Button Styles**: PREPP.TButton, Secondary.TButton, Accent.TButton
- **Futuristic Logo**: Hexagonal design with glow effects
- **Status Animations**: Color transitions and flash effects
- **Glass Morphism**: Semi-transparent elements with blur effects

## 🎯 Future Enhancements
- [ ] Animated transitions between states
- [ ] Sound effects for interactions
- [ ] Advanced progress analytics
- [ ] Multi-language support
- [ ] Cloud synchronization
- [ ] Mobile-responsive design

---

**PREPP-Lingo** - Where Norwegian language learning meets the future! 🇳🇴✨
