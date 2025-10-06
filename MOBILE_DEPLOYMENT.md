# 📱 PREPP-Lingo Mobile - Complete Deployment Guide

## ✅ What I've Created For You

I've built a **complete mobile-optimized web version** of PREPP-Lingo that you can deploy to GitHub and access on your phone!

### 📂 Files Created

```
mobile/
├── index.html          ✅ Main app interface
├── styles.css          ✅ Mobile-optimized styling
├── app.js              ✅ Game logic with Norwegian TTS
├── manifest.json       ✅ PWA configuration
├── sw.js              ✅ Offline support
├── icon-192.png       ✅ App icon (small)
├── icon-512.png       ✅ App icon (large)
├── create_icons.py    ✅ Icon generator script
└── README.md          ✅ Detailed documentation
```

---

## 🚀 Deploy to GitHub Pages (3 Steps)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Name it: `prepp-lingo` (or any name you like)
3. Make it **Public**
4. Click "Create repository"

### Step 2: Push Your Code

```bash
# Navigate to your project
cd /home/tuza/norskord

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Add PREPP-Lingo mobile app"

# Add your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/prepp-lingo.git

# Push
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to your repo: `https://github.com/YOUR_USERNAME/prepp-lingo`
2. Click **Settings** (top right)
3. Click **Pages** (left sidebar)
4. Under "Source":
   - Branch: **main**
   - Folder: **/ (root)**
5. Click **Save**
6. Wait 1-2 minutes

**Your app will be live at:**
```
https://YOUR_USERNAME.github.io/prepp-lingo/mobile/
```

---

## 📱 Install on Your Phone

### For iPhone (iOS)

1. Open Safari
2. Go to: `https://YOUR_USERNAME.github.io/prepp-lingo/mobile/`
3. Tap the **Share** button (📤 at bottom)
4. Scroll down and tap **"Add to Home Screen"**
5. Tap **"Add"**
6. Done! App icon appears on your home screen 🎉

### For Android

1. Open Chrome
2. Go to: `https://YOUR_USERNAME.github.io/prepp-lingo/mobile/`
3. Tap the **menu** (⋮ top right)
4. Tap **"Add to Home screen"**
5. Tap **"Add"**
6. Done! App icon appears on your home screen 🎉

---

## ✨ Mobile App Features

### 🎯 Core Features
- ✅ **Responsive Design** - Works on all screen sizes
- ✅ **Touch Optimized** - Large, easy-to-tap buttons
- ✅ **Text Wrapping** - Long Norwegian phrases wrap nicely
- ✅ **Offline Support** - Works without internet (after first load)
- ✅ **Install as App** - Add to home screen like a native app

### 🎮 Game Features
- 🔊 **Norwegian Text-to-Speech** - Built-in audio (no files needed!)
- ❤️ **Hearts System** - 3 lives per session
- 💡 **Hint System** - Get letter-by-letter hints
- 🔥 **Streak Tracking** - Track your daily progress
- 📊 **Progress Stats** - See your accuracy and score
- ⚙️ **Settings** - Customize difficulty, word count, modes

### 🎨 UI Features
- Modern gradient background
- Smooth animations
- Professional color scheme
- Bottom sheet settings modal
- Toast notifications
- Loading screen

---

## 🧪 Test Locally First

Before deploying, test it on your computer:

```bash
# Start local server
cd /home/tuza/norskord/mobile
python3 -m http.server 8080
```

Then open in your browser:
```
http://localhost:8080
```

Or test on your phone (if on same WiFi):
```
http://YOUR_COMPUTER_IP:8080
```

---

## 🔧 Customization Options

### 1. Add Your Chapter Words

Edit `mobile/app.js` around line 20-40:

```javascript
const wordsDatabase = {
    easy: [
        { word: "hei", translation: "hello", audio: null },
        // Add your easy words from capital_one
    ],
    medium: [
        { word: "velkommen", translation: "welcome", audio: null },
        // Add your medium words
    ],
    hard: [
        { word: "Innsatsfaktorer", translation: "input factors", audio: null },
        // Add your hard words from capital_one
    ]
};
```

### 2. Load Words from JSON (Advanced)

Create `mobile/words.json` with your chapter data:

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

Then modify `app.js` to fetch it:

```javascript
// In app.js, replace wordsDatabase with:
let wordsDatabase = {};

fetch('words.json')
    .then(response => response.json())
    .then(data => {
        wordsDatabase = data;
    });
```

### 3. Change Colors

Edit `mobile/styles.css` around line 15:

```css
:root {
    --primary: #2563eb;        /* Main blue */
    --success: #10b981;        /* Green */
    --warning: #f59e0b;        /* Orange */
    --error: #ef4444;          /* Red */
}
```

### 4. Custom App Icons

Replace `icon-192.png` and `icon-512.png` with your own:

**Option A:** Use online tool
- Go to https://favicon.io/favicon-converter/
- Upload your image
- Download and replace

**Option B:** Recreate with Python
```bash
cd mobile
python3 create_icons.py
```

---

## 🌐 Alternative Deployment (Easier!)

### Netlify Drop (No Git Required!)

1. Go to https://app.netlify.com/drop
2. Drag the entire `mobile` folder
3. Get instant URL
4. Done! 🎉

**Pros:**
- No GitHub account needed
- Instant deployment
- Free SSL
- Custom domain support

---

## 📊 What Works Offline

After first load, these work without internet:
- ✅ Game interface
- ✅ All UI elements
- ✅ Settings
- ✅ Progress tracking
- ✅ Text-to-Speech (if voice is installed)

What needs internet:
- ❌ First-time load
- ❌ Downloading new voices (if not installed)

---

## 🎯 Desktop vs Mobile Comparison

| Feature | Desktop (Tkinter) | Mobile (Web) |
|---------|------------------|--------------|
| Platform | Windows/Mac/Linux | Any device with browser |
| Installation | Python + dependencies | Just visit URL |
| Offline | ✅ Always | ✅ After first load |
| Audio | MP3 files | Text-to-Speech API |
| Chapter System | ✅ Full system | ⚠️ Simplified (can be added) |
| Progress Sync | Local only | Can add cloud sync |
| Updates | Manual | Automatic |

---

## 🐛 Troubleshooting

### Problem: Audio not playing
**Solution:**
- Use Chrome or Safari (best support)
- Check if Norwegian voice is installed
- Try on different device

### Problem: Can't install as app
**Solution:**
- Must use HTTPS (GitHub Pages has it)
- Try different browser
- Clear cache and retry

### Problem: App not loading
**Solution:**
- Check GitHub Pages is enabled
- Wait 2-3 minutes after enabling
- Check URL is correct
- Try incognito/private mode

### Problem: Words not showing
**Solution:**
- Check browser console (F12)
- Verify `app.js` loaded correctly
- Check `wordsDatabase` has content

---

## 📈 Future Enhancements (Optional)

### Easy Additions:
1. **Load words from your chapters**
   - Export chapter JSON to mobile format
   - Fetch from GitHub raw URL

2. **Cloud sync**
   - Use Firebase or Supabase
   - Sync progress across devices

3. **Better audio**
   - Upload your MP3 files to GitHub
   - Load them instead of TTS

4. **More features**
   - Leaderboard
   - Achievements
   - Social sharing

### Medium Additions:
1. **Backend API**
   - Create Flask/FastAPI backend
   - Deploy to Heroku/Railway
   - Real-time progress sync

2. **User accounts**
   - Login system
   - Cloud storage
   - Multiple devices

---

## 📞 Quick Reference

### Your URLs (after deployment):
```
GitHub Repo:    https://github.com/YOUR_USERNAME/prepp-lingo
Live App:       https://YOUR_USERNAME.github.io/prepp-lingo/mobile/
Local Test:     http://localhost:8080
```

### Important Files:
```
mobile/index.html    - Main interface
mobile/app.js        - Game logic (edit words here)
mobile/styles.css    - Styling (edit colors here)
mobile/manifest.json - App config (edit name/colors)
```

### Quick Commands:
```bash
# Test locally
cd /home/tuza/norskord/mobile && python3 -m http.server 8080

# Deploy to GitHub
git add . && git commit -m "Update" && git push

# Create new icons
cd mobile && python3 create_icons.py
```

---

## ✅ Checklist

Before deploying:
- [ ] Test locally (`python3 -m http.server 8080`)
- [ ] Check all features work
- [ ] Test on mobile browser
- [ ] Customize words (optional)
- [ ] Create custom icons (optional)

After deploying:
- [ ] Verify GitHub Pages URL works
- [ ] Test on actual phone
- [ ] Install as home screen app
- [ ] Test offline functionality
- [ ] Share with friends! 🎉

---

## 🎉 You're Ready!

Everything is set up and ready to deploy. Just follow the **3 steps** at the top of this guide:

1. Create GitHub repo
2. Push your code
3. Enable GitHub Pages

Then access it on your phone and add to home screen!

**Questions?** Check the detailed `mobile/README.md` or test locally first.

**Enjoy learning Norwegian on the go! 🇳🇴📱**
