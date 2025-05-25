import cv2
import numpy as np
from sklearn.cluster import KMeans
import os
import json
from collections import Counter

def extract_dominant_color(image_region, n_clusters=3):
    """Extract the dominant color from an image region using K-means clustering."""
    pixels = image_region.reshape(-1, 3)
    
    if len(pixels) < 10:
        return np.array([128, 128, 128])
    
    kmeans = KMeans(n_clusters=min(n_clusters, len(pixels)), random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    label_counts = Counter(labels)
    
    dominant_label = label_counts.most_common(1)[0][0]
    dominant_color = colors[dominant_label]
    
    return dominant_color.astype(int)

def rgb_to_hex(rgb):
    """Convert RGB values to hex color code."""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color_name(rgb):
    """Get a simple color name based on RGB values."""
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    
    if r > 200 and g > 200 and b > 200:
        return "Light/White"
    elif r < 50 and g < 50 and b < 50:
        return "Dark/Black"
    elif r > g and r > b:
        return "Red/Pink" if g > 100 else "Red"
    elif g > r and g > b:
        return "Green"
    elif b > r and b > g:
        return "Blue"
    elif r > 150 and g > 150:
        return "Yellow"
    elif abs(r - g) < 30 and abs(g - b) < 30:
        if r > 150:
            return "Light Gray"
        elif r > 80:
            return "Gray"
        else:
            return "Dark Gray"
    else:
        return "Mixed Color"

def is_white_empty(rgb, threshold=200):
    """Check if a color is white/empty (all RGB values above threshold)."""
    return all(value > threshold for value in rgb)

def create_leather_grid(image, rows=9, cols=10):
    """
    Create a grid for leather image with NO spacing between swatches.
    Samples from center of each cell to get clean colors.
    """
    height, width = image.shape[:2]
    
    # Calculate cell dimensions (no spacing, edge-to-edge)
    cell_width = width // cols
    cell_height = height // rows
    
    # Smaller border to ensure we sample from the swatch, not edges
    border_percent = 0.15  # 15% border to avoid any edge artifacts
    
    squares = []
    for row in range(rows):
        for col in range(cols):
            # Calculate exact cell boundaries
            x = col * cell_width
            y = row * cell_height
            w = cell_width if col < cols - 1 else width - x
            h = cell_height if row < rows - 1 else height - y
            
            # Apply small border for clean sampling
            border_x = int(w * border_percent)
            border_y = int(h * border_percent)
            
            sample_x = x + border_x
            sample_y = y + border_y
            sample_w = w - (2 * border_x)
            sample_h = h - (2 * border_y)
            
            # Ensure minimum sampling size
            if sample_w > 10 and sample_h > 10:
                squares.append((sample_x, sample_y, sample_w, sample_h, row, col))
            else:
                squares.append((x, y, w, h, row, col))
    
    return squares

def process_leather_image(image_path):
    """Process the leather image with special handling for row 4."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_file = os.path.basename(image_path)
    
    print(f"  Image dimensions: {image_rgb.shape[1]} x {image_rgb.shape[0]}")
    print(f"  Processing leather grid: 10 columns x 9 rows")
    print(f"  Special handling: Row 4 has only 5 colors (discarding white/empty ones)")
    
    # Create grid for leather
    squares = create_leather_grid(image_rgb)
    
    colors_data = []
    color_number = 1
    
    for i, (x, y, w, h, row, col) in enumerate(squares):
        square_region = image_rgb[y:y+h, x:x+w]
        
        if square_region.size > 0:
            dominant_color = extract_dominant_color(square_region, n_clusters=5)
            
            # Special handling for row 4 (index 3) - check if it's white/empty
            if row == 3 and col >= 5:  # Row 4, columns 6-10
                if is_white_empty(dominant_color, threshold=200):
                    print(f"    Skipping empty square at Row {row+1}, Col {col+1}")
                    continue
            
            hex_color = rgb_to_hex(dominant_color)
            color_name = get_color_name(dominant_color)
            
            colors_data.append({
                'color_number': f"{color_number:03d}",
                'position_in_grid': i + 1,
                'rgb': dominant_color.tolist(),
                'hex': hex_color,
                'name': color_name,
                'coordinates': (x, y, w, h),
                'grid_position': f"Row {row + 1}, Col {col + 1}"
            })
            
            color_number += 1
    
    print(f"  SUCCESS: Extracted {len(colors_data)} leather colors (skipped empty whites)")
    return colors_data

def generate_leather_html(colors_data, output_file='leather_colors.html'):
    """Generate HTML for leather colors with 10-column layout."""
    
    total_colors = len(colors_data)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leather Color Collection</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .leather-section {{
            background: white;
            margin: 40px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .leather-title {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 3px solid #e67e22;
            padding-bottom: 10px;
        }}
        .grid-info {{
            background: #fdf2e9;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
            color: #8b4513;
            border-left: 4px solid #e67e22;
        }}
        .color-grid {{
            display: grid;
            grid-template-columns: repeat(10, 80px);
            gap: 2px;
            margin: 20px 0;
            justify-content: start;
        }}
        .color-square {{
            width: 80px;
            height: 80px;
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .color-square:hover {{
            transform: scale(1.05);
            z-index: 10;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }}
        .color-number {{
            position: absolute;
            top: 2px;
            left: 2px;
            background: rgba(0,0,0,0.7);
            color: white;
            font-size: 10px;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 2px;
        }}
        .color-info {{
            position: absolute;
            bottom: -35px;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 5px 8px;
            border-radius: 4px;
            font-size: 11px;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.2s ease;
            z-index: 20;
            pointer-events: none;
        }}
        .color-square:hover .color-info {{
            opacity: 1;
        }}
        .summary {{
            background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .summary h1 {{
            margin: 0 0 10px 0;
            font-size: 32px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
        }}
        .copy-notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #e67e22;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            display: none;
            z-index: 1000;
        }}
        .leather-note {{
            background: #fff8dc;
            border: 1px solid #deb887;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            color: #8b4513;
        }}
        .empty-space {{
            width: 80px;
            height: 80px;
            border: 2px dashed #ccc;
            border-radius: 4px;
            background: #f9f9f9;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="copy-notification" id="copyNotification">Color copied to clipboard!</div>
    <div class="summary">
        <h1>Leather Color Collection</h1>
        <p>Professional leather swatches - Colors 001 to {total_colors:03d}</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">1</div>
                <div>Leather Sheet</div>
            </div>
            <div class="stat">
                <div class="stat-number">{total_colors}</div>
                <div>Total Colors</div>
            </div>
        </div>
    </div>
    
    <div class="leather-note">
        <strong>LEATHER PROCESSING:</strong> ✓ 10 columns × 9 rows layout ✓ Row 4 empty spaces discarded ✓ No spacing between swatches ✓ Sequential numbering 001-{total_colors:03d}
    </div>

    <div class="leather-section">
        <div class="leather-title">Leather Color Swatches</div>
        <div class="grid-info">
            ✓ PROCESSED: 10 columns layout - {total_colors} colors extracted (empty whites skipped)
            <br>Grid-based sampling with edge-to-edge swatches
        </div>
        <div class="color-grid">
"""

    # We need to reconstruct the 10-column layout including empty spaces
    grid_positions = {}
    for color_data in colors_data:
        grid_pos = color_data['grid_position']
        grid_positions[grid_pos] = color_data
    
    # Create the full 9x10 grid display
    for row in range(9):
        for col in range(10):
            grid_key = f"Row {row + 1}, Col {col + 1}"
            
            if grid_key in grid_positions:
                # Color swatch exists
                color_data = grid_positions[grid_key]
                hex_color = color_data['hex']
                rgb = color_data['rgb']
                color_number = color_data['color_number']
                
                html_content += f"""            <div class="color-square" style="background-color: {hex_color};" onclick="copyToClipboard('{hex_color}', '{color_number}')">
                <div class="color-number">{color_number}</div>
                <div class="color-info">{hex_color}<br>RGB({rgb[0]}, {rgb[1]}, {rgb[2]})</div>
            </div>
"""
            elif row == 3 and col >= 5:  # Row 4, columns 6-10 (empty spaces)
                html_content += """            <div class="empty-space">EMPTY</div>
"""
            # If it's not row 4 and not in our data, something's wrong - but we'll skip for now
    
    html_content += """        </div>
    </div>

    <script>
        function copyToClipboard(hex, colorNumber) {
            navigator.clipboard.writeText(hex).then(() => {
                const notification = document.getElementById('copyNotification');
                notification.textContent = `Color ${colorNumber} (${hex}) copied to clipboard!`;
                notification.style.display = 'block';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Leather HTML saved to: {output_file}")

def main():
    input_folder = os.path.dirname(os.path.abspath(__file__))
    print(f"Processing leather image in: {input_folder}")
    
    # Look for any image files in the folder
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(input_folder) 
                   if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print("No image files found in the Leather folder.")
        print("Please add your leather image file to this folder and run the script again!")
        return
    
    # Take the first image file found
    leather_file = image_files[0]
    print(f"Processing leather file: {leather_file}")
    
    image_path = os.path.join(input_folder, leather_file)
    colors_data = process_leather_image(image_path)
    
    if colors_data:
        # Generate HTML
        output_html = os.path.join(input_folder, 'leather_colors.html')
        generate_leather_html(colors_data, output_html)
        
        # Save JSON
        json_output = os.path.join(input_folder, 'leather_colors.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump({'leather_colors': colors_data}, f, indent=2, ensure_ascii=False)
        
        print(f"\nLEATHER PROCESSING COMPLETE!")
        print(f"HTML: {output_html}")
        print(f"JSON: {json_output}")
        print(f"Total leather colors: {len(colors_data)}")
        print("Fixed: 10-column layout with row 4 empty spaces handled")
    else:
        print("No leather colors extracted.")

if __name__ == "__main__":
    main()
