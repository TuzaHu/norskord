# PREPP-Lingo 🎯

**Norwegian Dictation Learning Game** - A Duolingo-style language learning application for mastering Norwegian vocabulary through audio dictation.

## 🚀 Live Demo

**📱 Mobile Web App**: [Play Now](https://yourusername.github.io/norskord/)  
*Replace `yourusername` with your actual GitHub username*

## 🎮 Game Features

### 🎯 Two Game Modes
- **Øvelse (Practice)**: 20-second timer, multiple retries, perfect for learning
- **Aksjon (Action)**: Time pressure, hearts system, unlocks new chapters

### 📚 Chapter-Based Learning
- **Progressive Difficulty**: 3 chapters with increasing complexity
- **Unlock System**: Achieve 70% accuracy in Aksjon mode to unlock next chapter
- **Real Norwegian Audio**: Authentic pronunciation from your own recordings

### 🎵 Audio Features
- **Real MP3 Files**: No robotic voices - uses your actual Norwegian recordings
- **Multiple Difficulty Levels**: Easy, Medium, Hard word categorization
- **Audio Controls**: Play, pause, and repeat audio as needed

### 📱 Mobile Optimized
- **Responsive Design**: Works perfectly on phones and tablets
- **PWA Support**: Install as a native app on your device
- **Touch-Friendly**: Optimized for mobile interaction

## 🛠️ Technical Features

- **Modern Web Technologies**: HTML5, CSS3, JavaScript ES6+
- **Offline Support**: Service Worker for offline gameplay
- **Local Storage**: Saves your progress and settings
- **Cross-Platform**: Works on any device with a modern browser

## 📁 Project Structure

```
norskord/
├── mobile/                 # Mobile web application
│   ├── index.html         # Main app page
│   ├── styles.css         # Modern UI styling
│   ├── app.js            # Game logic and interactions
│   ├── manifest.json     # PWA configuration
│   ├── sw.js             # Service Worker for offline support
│   ├── audio/            # Norwegian MP3 audio files
│   ├── words_*.json      # Chapter word data
│   └── icons/            # App icons
├── development/           # Desktop Python application
│   ├── main.py           # Desktop app entry point
│   ├── game_engine.py    # Core game logic
│   ├── chapters/         # Chapter data and audio
│   └── translation_service.py
└── README.md             # This file
```

## 🚀 Quick Start

### For Mobile Web App (Recommended)
1. Visit: `https://yourusername.github.io/norskord/`
2. Open on your phone/tablet
3. Tap "Start Game" and begin learning!

### For Desktop Development
```bash
# Install dependencies
pip install pygame pydub gtts requests

# Run the desktop version
python3 development/main.py

# Export words for mobile app
python3 mobile/export_words.py
```

## 📱 Installation (PWA)

1. Open the app in your mobile browser
2. Look for "Add to Home Screen" option
3. Tap to install as a native app
4. Enjoy offline Norwegian learning!

## 🎯 How to Play

### Øvelse Mode (Practice)
- Listen to Norwegian audio
- Type what you hear
- 20 seconds per word
- Multiple attempts allowed
- No hearts lost on wrong answers

### Aksjon Mode (Action)
- Same gameplay as practice
- Limited hearts (lose one per wrong answer)
- Time carries over between words
- Must achieve 70% to unlock next chapter

## 📊 Progress Tracking

- **Best Scores**: Track your highest accuracy per chapter
- **Chapter Progress**: Visual indicators of completion status
- **Missed Words**: Review words you struggled with
- **Settings Persistence**: Your preferences are saved

## 🔧 Customization

### Adding New Words
1. Add audio files to `mobile/audio/`
2. Update chapter JSON files
3. Run `mobile/export_words.py` to sync data

### Modifying Game Settings
- Change timer durations in `app.js`
- Adjust difficulty thresholds
- Customize UI colors in `styles.css`

## 🌐 Browser Support

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/norskord/issues) page
2. Create a new issue with detailed description
3. Include browser/device information for mobile issues

## 🎉 Acknowledgments

- Norwegian language learning community
- Open source audio processing libraries
- Modern web standards for PWA support

---

**Happy Learning! 🇳🇴**