# 📱 PREPP-Lingo Mobile - Deployment Guide

## 🚀 Quick Start - Deploy to GitHub Pages

### Step 1: Push to GitHub

```bash
# Navigate to your project
cd /home/tuza/norskord

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Add PREPP-Lingo mobile web app"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/prepp-lingo.git

# Push to GitHub
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **main** branch
4. Select **/ (root)** or **/mobile** folder
5. Click **Save**
6. Your app will be live at: `https://YOUR_USERNAME.github.io/prepp-lingo/mobile/`

### Step 3: Access on Mobile

1. Open the URL on your mobile browser
2. **For iOS (Safari):**
   - Tap the Share button (📤)
   - Scroll down and tap "Add to Home Screen"
   - Tap "Add"

3. **For Android (Chrome):**
   - Tap the menu (⋮)
   - Tap "Add to Home screen"
   - Tap "Add"

Now you have PREPP-Lingo as a mobile app! 🎉

---

## 📂 Project Structure

```
mobile/
├── index.html          # Main HTML file
├── styles.css          # Mobile-optimized CSS
├── app.js              # JavaScript game logic
├── manifest.json       # PWA manifest
├── sw.js              # Service Worker for offline support
├── icon-192.png       # App icon (192x192)
├── icon-512.png       # App icon (512x512)
└── README.md          # This file
```

---

## ✨ Features

### Mobile-Optimized
- ✅ Responsive design for all screen sizes
- ✅ Touch-friendly buttons and inputs
- ✅ Text wrapping for long Norwegian phrases
- ✅ Smooth animations and transitions
- ✅ Works offline (PWA)

### Game Features
- 🎯 Practice & Action modes
- 💡 Hint system
- ❤️ Hearts system
- 🔥 Streak tracking
- 📊 Progress tracking
- 🔊 Text-to-Speech (Norwegian)
- 🌐 Works without backend

### Settings
- Difficulty levels (Easy, Medium, Hard)
- Word count selection (5, 10, 15, 20)
- Translation toggle
- Game mode selection

---

## 🔧 Customization

### Adding Your Own Words

Edit `app.js` and modify the `wordsDatabase` object:

```javascript
const wordsDatabase = {
    easy: [
        { word: "hei", translation: "hello", audio: null },
        // Add more easy words
    ],
    medium: [
        { word: "velkommen", translation: "welcome", audio: null },
        // Add more medium words
    ],
    hard: [
        { word: "Innsatsfaktorer", translation: "input factors", audio: null },
        // Add more hard words
    ]
};
```

### Loading Words from JSON

To load words from your chapter system, you can create a `words.json` file:

```json
{
    "easy": [
        {"word": "hei", "translation": "hello"}
    ],
    "medium": [
        {"word": "velkommen", "translation": "welcome"}
    ],
    "hard": [
        {"word": "Innsatsfaktorer", "translation": "input factors"}
    ]
}
```

Then modify `app.js` to fetch from this file.

---

## 🎨 Creating App Icons

### Quick Method (Online Tools)
1. Go to https://favicon.io/favicon-converter/
2. Upload an image (at least 512x512px)
3. Download the generated icons
4. Replace `icon-192.png` and `icon-512.png`

### Manual Method (Using ImageMagick)
```bash
# Create a simple icon with text
convert -size 512x512 xc:#2563eb \
  -gravity center \
  -pointsize 200 \
  -fill white \
  -annotate +0+0 "🎯" \
  icon-512.png

convert icon-512.png -resize 192x192 icon-192.png
```

---

## 🌐 Alternative Deployment Options

### Option 1: Netlify (Easiest)
1. Go to https://netlify.com
2. Drag and drop the `mobile` folder
3. Get instant URL
4. Free SSL and CDN

### Option 2: Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `cd mobile && vercel`
3. Follow prompts
4. Get instant deployment

### Option 3: GitHub Pages (Recommended)
- Free
- Easy to update
- Custom domain support
- Automatic HTTPS

---

## 📱 Testing Locally

### Simple HTTP Server (Python)
```bash
cd mobile
python3 -m http.server 8000
```
Then open: http://localhost:8000

### Or use Node.js
```bash
npx http-server mobile -p 8000
```

---

## 🔊 Audio Notes

The app uses the **Web Speech API** for Norwegian text-to-speech:
- Works on most modern browsers
- No audio files needed
- Adjustable speed and pitch
- Falls back gracefully if not supported

For better quality audio, you can:
1. Generate MP3 files using your `generate_chapter_audio.py` script
2. Upload them to GitHub
3. Modify `app.js` to load from URLs

---

## 🐛 Troubleshooting

### Audio Not Playing
- Ensure browser supports Web Speech API
- Check if Norwegian (no-NO) voice is installed
- Try on Chrome/Safari (best support)

### App Not Installing
- Ensure HTTPS is enabled (GitHub Pages has it by default)
- Check manifest.json is accessible
- Clear browser cache

### Offline Not Working
- Service Worker requires HTTPS
- Check browser console for errors
- Verify sw.js is in the same directory

---

## 📊 Browser Support

| Feature | Chrome | Safari | Firefox | Edge |
|---------|--------|--------|---------|------|
| Basic App | ✅ | ✅ | ✅ | ✅ |
| PWA Install | ✅ | ✅ | ⚠️ | ✅ |
| Text-to-Speech | ✅ | ✅ | ⚠️ | ✅ |
| Offline Mode | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Next Steps

1. ✅ Create app icons (icon-192.png, icon-512.png)
2. ✅ Test on your mobile device
3. ✅ Deploy to GitHub Pages
4. ✅ Add to home screen
5. ✅ Share with friends!

---

## 📞 Support

For issues or questions:
- Check browser console for errors
- Ensure all files are uploaded
- Test on different browsers
- Check GitHub Pages settings

---

## 🎉 You're All Set!

Your PREPP-Lingo mobile app is ready to deploy. Just follow the steps above and you'll have a fully functional Norwegian learning app on your phone!

**Live Demo URL (after deployment):**
`https://YOUR_USERNAME.github.io/prepp-lingo/mobile/`

Enjoy learning Norwegian! 🇳🇴