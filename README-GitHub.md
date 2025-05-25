# AUBLIQ Color Preview System

## 🎯 Interactive Color Combination Tool
Professional leather and suede color preview system with real-time Photoshop-quality blending.

![Preview](preview-screenshot.png)

## ✨ Features
- 🎨 **85 Leather Colors** + **480 Suede Colors** 
- 🌗 **Light/Dark Base** toggle
- 🔢 **Sequential numbering** (001-085, 001-480)
- 💾 **Save combinations** as PNG
- 🎭 **Photoshop-quality blending** (CSS mix-blend-mode)
- 📱 **Responsive design**

## 🚀 Quick Start

### Prerequisites
- Python 3.x installed
- Modern web browser

### Run the App
```bash
# 1. Navigate to project folder
cd "C:\Users\mila\Desktop\Box Automation\Mockup\ColorPreview"

# 2. Start local server (required for loading color data)
python -m http.server 8000

# 3. Open browser
http://localhost:8000
```

## 🎨 How to Use
1. **Select Base**: Choose Light or Dark base
2. **Pick Leather**: Click any leather color (001-085)
3. **Choose Suede**: Click any suede color (001-480)  
4. **Preview**: See realistic combination in real-time
5. **Save**: Click "💾 Save Combination" to download PNG

## 📁 Project Structure
```
├── Mockup/ColorPreview/     # Main application
├── Suede/                   # Suede color extraction (480 colors)
├── Leather/                 # Leather color extraction (85 colors)
└── README.md               # This file
```

## 🔬 Technical Details
- **Color Extraction**: Python + OpenCV + K-means clustering
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Blending**: CSS `mix-blend-mode` for Photoshop-quality effects
- **Save Feature**: Canvas-based image generation

## 🌐 Hosting Options
- **Local**: `python -m http.server` (current)
- **GitHub Pages**: Deploy `Mockup/ColorPreview/` folder
- **Netlify**: Drag & drop deployment
- **Vercel**: GitHub integration

## 🏭 Production Use
Perfect for:
- Factory color specification
- Client presentations  
- Design mockups
- Color combination testing

## 👥 Contributors
- **Mila**: Project design, Photoshop expertise, color curation
- **Claude**: Technical implementation, color extraction algorithms

---
*AUBLIQ Color Preview System v1.0*
