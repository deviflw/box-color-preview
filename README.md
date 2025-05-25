# Color Preview System - Project Documentation

## 🎯 Project Overview
This project creates an interactive color preview system for leather and suede combinations on light/dark bases. Users can select material colors and see realistic previews in real-time.

## 📁 Project Structure
```
Box Automation/
├── Suede/                          # Suede color extraction
│   ├── suede-1.jpg to suede-10.jpg # Original suede images
│   ├── color_extractor_FINAL.py    # Final suede extraction script
│   ├── extracted_colors_FINAL.html # 480 suede colors (001-480)
│   └── extracted_colors_FINAL.json # Suede color data
├── Leather/                        # Leather color extraction  
│   ├── leather.jpg                 # Original leather image
│   ├── leather_extractor.py        # Leather extraction script
│   ├── leather_colors.html         # 85 leather colors (001-085)
│   └── leather_colors.json         # Leather color data
├── Mockup/                         # Preview system
│   ├── PNG/                        # Photoshop layer exports
│   └── ColorPreview/               # **MAIN COLOR PREVIEW APP** 🎨
└── README.md                       # This file
```

## 🎨 Color Extraction Results

### Suede Colors (480 total)
- **suede-1.jpg**: Colors 001-030 (6 rows × 5 columns)
- **suede-2.jpg**: Colors 031-080 (10 rows × 5 columns)
- **suede-3.jpg**: Colors 081-130 (10 rows × 5 columns)
- **suede-4.jpg**: Colors 131-180 (10 rows × 5 columns)
- **suede-5.jpg**: Colors 181-230 (10 rows × 5 columns)
- **suede-6.jpg**: Colors 231-280 (10 rows × 5 columns)
- **suede-7.jpg**: Colors 281-330 (10 rows × 5 columns)
- **suede-8.jpg**: Colors 331-380 (10 rows × 5 columns)
- **suede-9.jpg**: Colors 381-430 (10 rows × 5 columns)
- **suede-10.jpg**: Colors 431-480 (10 rows × 5 columns)

### Leather Colors (85 total)
- **Grid**: 10 columns × 9 rows
- **Special handling**: Row 4 has only 5 colors (columns 6-10 are empty/white)
- **Sequential numbering**: 001-085

## 🖼️ Photoshop Layer Structure

### Exported PNG Files:
1. **AUBLIQ.png** - Logo/text layer
2. **Texture - Overlay.png** - Base texture (overlay blend mode)
3. **Light Base Top - Overlay.png** - Light base version (overlay blend mode)
4. **Dark Base Top - Overlay.png** - Dark base version (overlay blend mode)
5. **Leather Mask - Overlay.png** - Leather area mask (overlay blend mode)
6. **Suede Mask - Overlay.png** - Suede area mask (overlay blend mode)
7. **Light Base Under - 20 opacity.png** - Light base bottom (20% opacity)
8. **Dark Base Under - 20 opacity.png** - Dark base bottom (20% opacity)

### Layer Stacking Order (bottom to top):
1. Base Under (20% opacity) - Light OR Dark
2. Suede Mask (overlay) - with selected suede color
3. Leather Mask (overlay) - with selected leather color  
4. Base Top (overlay) - Light OR Dark
5. Texture (overlay)
6. AUBLIQ logo

## 🔧 Technical Implementation

### CSS Blend Modes Used:
- `mix-blend-mode: overlay` - For most layers
- `opacity: 0.2` - For base under layers

### Color Application Method:
1. Load extracted color data from JSON files
2. Use PNG masks to define color areas
3. Apply selected colors with CSS background-color
4. Stack layers with proper blend modes
5. Show/hide light/dark base layers based on selection

### User Interface:
- **Base Selection**: Toggle between Light/Dark base
- **Leather Color Picker**: 85 leather colors with numbers 001-085
- **Suede Color Picker**: 480 suede colors with numbers 001-480
- **Live Preview**: Real-time color combination preview
- **Color Info**: Display selected color numbers and hex codes

## 🚀 How to Use

### 🌟 **MAIN APP - Start Here!**
```bash
# Navigate to the main color preview app
cd "C:\Users\mila\Desktop\Box Automation\Mockup\ColorPreview"

# Start the local server (required for loading color data)
python -m http.server 8000

# Open browser and go to:
http://localhost:8000
```

### Running Color Extraction:
```bash
# For suede colors (run in Suede folder)
python color_extractor_FINAL.py

# For leather colors (run in Leather folder)  
python leather_extractor.py
```

### Using Preview System:
1. Open `ColorPreview/index.html` in browser
2. Select base type (Light/Dark)
3. Click leather color from palette
4. Click suede color from palette
5. View realistic preview with proper blending
6. Copy color numbers for factory orders

## 📊 Total Combinations Possible:
- 85 leather × 480 suede × 2 bases = **81,600 combinations**
- Real-time generation vs pre-rendering saves massive storage

## 🎯 Key Features:
- ✅ Realistic Photoshop-quality blending in browser
- ✅ Sequential color numbering for factory communication
- ✅ Real-time preview (no pre-rendering needed)
- ✅ Professional UI with color palettes
- ✅ Copy color codes functionality
- ✅ Responsive design

## 🔄 Workflow Summary:
1. **Extract colors** from fabric images using Python scripts
2. **Export Photoshop layers** as PNG with blend mode notes
3. **Build HTML/CSS/JS preview** system with proper layer stacking
4. **Apply extracted colors** dynamically to masked areas
5. **Preview combinations** in real-time with realistic blending

## 🛠️ Technologies Used:
- **Python**: OpenCV, scikit-learn, KMeans clustering for color extraction
- **HTML/CSS**: Layer stacking, blend modes, responsive design
- **JavaScript**: Dynamic color application, user interaction
- **Photoshop**: Professional mockup creation and layer export

## 📝 Notes:
- Color extraction uses K-means clustering to handle fabric texture
- Center sampling avoids borders and white spaces
- CSS blend modes replicate Photoshop effects accurately
- Sequential numbering maintained for production workflow
- Empty/white areas automatically detected and skipped

## 🔮 Future Enhancements:
- Batch export functionality
- Color matching algorithms
- Print-ready output generation
- Integration with ordering systems

---
*Last updated: [Current Date]*
*Project by: Mila & Claude*
