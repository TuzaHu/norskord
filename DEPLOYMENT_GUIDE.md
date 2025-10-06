# 🚀 GitHub Pages Deployment Guide

## 📋 Quick Setup Checklist

### ✅ **Step 1: Create GitHub Repository**
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. **Repository name:** `norskord` (or `prepp-lingo`)
4. **Description:** `Norwegian Dictation Learning Game - PREPP-Lingo`
5. **Visibility:** Public ✅ (required for free GitHub Pages)
6. **DO NOT** check "Initialize with README" ❌
7. Click **"Create repository"**

### ✅ **Step 2: Connect and Push Code**
Run these commands in your terminal:

```bash
# Add GitHub repository as remote origin
git remote add origin https://github.com/YOURUSERNAME/norskord.git

# Push your code to GitHub
git push -u origin main
```

**Replace `YOURUSERNAME` with your actual GitHub username!**

### ✅ **Step 3: Enable GitHub Pages**
1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Scroll down to **"Pages"** in the left sidebar
4. **Source:** Select "Deploy from a branch"
5. **Branch:** Select "main" and "/ (root)"
6. Click **"Save"**

### ✅ **Step 4: Wait for Deployment**
- GitHub will build and deploy your site
- Usually takes 2-5 minutes
- You'll see a green checkmark when ready

### ✅ **Step 5: Access Your App**
Your app will be available at:
```
https://YOURUSERNAME.github.io/norskord/
```

## 🎯 **App Structure**

```
Your GitHub Pages Site:
├── https://YOURUSERNAME.github.io/norskord/          # Landing page
└── https://YOURUSERNAME.github.io/norskord/mobile/   # Mobile game app
```

## 📱 **Mobile App Features**

### **🎮 Game Modes:**
- **Øvelse (Practice):** 20-second timer, multiple retries
- **Aksjon (Action):** Time pressure, hearts system, unlocks chapters

### **📚 Chapter System:**
- **Chapter 1:** Grunnleggende (Basic) - Unlocked by default
- **Chapter 2:** Middels (Intermediate) - Unlock with 70% in Aksjon mode
- **Chapter 3:** Avansert (Advanced) - Unlock with 70% in Aksjon mode

### **🎵 Audio Features:**
- Real Norwegian MP3 files (no robotic voices!)
- Multiple difficulty levels: Easy, Medium, Hard
- Audio controls: Play, pause, repeat

### **📱 Mobile Optimization:**
- Responsive design for phones and tablets
- PWA support - install as native app
- Offline support with Service Worker
- Touch-friendly interface

## 🔧 **Updating Your App**

When you make changes to your code:

```bash
# Add your changes
git add .

# Commit with a message
git commit -m "Update game features"

# Push to GitHub
git push origin main
```

GitHub Pages will automatically redeploy your site!

## 🌐 **Sharing Your App**

### **Direct Links:**
- **Landing Page:** `https://YOURUSERNAME.github.io/norskord/`
- **Mobile Game:** `https://YOURUSERNAME.github.io/norskord/mobile/`

### **QR Code:**
Generate a QR code for easy mobile access:
1. Go to [qr-code-generator.com](https://www.qr-code-generator.com/)
2. Enter your mobile game URL
3. Download and share the QR code

## 📊 **Analytics (Optional)**

To track usage, add Google Analytics:

1. Get tracking code from [Google Analytics](https://analytics.google.com/)
2. Add to `mobile/index.html` before `</head>`
3. Commit and push changes

## 🔒 **Security & Privacy**

- Your app runs entirely in the browser
- No server-side data collection
- All progress saved locally on device
- No personal information transmitted

## 🆘 **Troubleshooting**

### **App Not Loading:**
- Check GitHub Pages is enabled in Settings
- Wait 5-10 minutes for deployment
- Clear browser cache and refresh

### **Audio Not Playing:**
- Ensure device volume is up
- Try different browser (Chrome recommended)
- Check if autoplay is blocked

### **Mobile Issues:**
- Use HTTPS (GitHub Pages provides this automatically)
- Try adding to home screen (PWA install)
- Clear browser data if needed

## 📞 **Support**

If you encounter issues:
1. Check the [GitHub Issues](https://github.com/YOURUSERNAME/norskord/issues) page
2. Create a new issue with:
   - Device/browser information
   - Steps to reproduce the problem
   - Screenshots if applicable

## 🎉 **Congratulations!**

Your PREPP-Lingo app is now live and accessible worldwide! 🇳🇴

---

**Happy Learning! 🎯**
