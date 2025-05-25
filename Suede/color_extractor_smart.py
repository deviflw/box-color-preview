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

def determine_grid_size(image_file, image_shape):
    """
    Determine the appropriate grid size based on image name and dimensions.
    """
    height, width = image_shape[:2]
    
    # Based on your specification:
    # - First image (suede-1) has 30 colors
    # - Other images have around 50 colors
    
    if "suede-1.jpg" in image_file:
        # For 30 colors, try 6x5 or 5x6
        return 6, 5  # 30 squares
    else:
        # For ~50 colors, try different combinations
        if width > height:
            return 10, 5  # 50 squares (landscape)
        else:
            return 7, 7   # 49 squares (more square)

def create_precise_grid(image, rows, cols):
    """Create a precise grid with specified dimensions."""
    height, width = image.shape[:2]
    
    # Calculate cell dimensions
    cell_width = width // cols
    cell_height = height // rows
    
    squares = []
    for row in range(rows):
        for col in range(cols):
            x = col * cell_width
            y = row * cell_height
            # Adjust last column and row to fill the image completely
            w = cell_width if col < cols - 1 else width - x
            h = cell_height if row < rows - 1 else height - y
            squares.append((x, y, w, h))
    
    return squares

def process_image_smart(image_path):
    """Process image with smart grid detection."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_file = os.path.basename(image_path)
    
    # Determine grid size
    rows, cols = determine_grid_size(image_file, image_rgb.shape)
    total_squares = rows * cols
    
    print(f"  Image dimensions: {image_rgb.shape[1]} x {image_rgb.shape[0]}")
    print(f"  Using {rows}x{cols} grid ({total_squares} squares)")
    
    # Create grid
    squares = create_precise_grid(image_rgb, rows, cols)
    
    # Extract colors
    colors_data = []
    for i, (x, y, w, h) in enumerate(squares):
        square_region = image_rgb[y:y+h, x:x+w]
        
        if square_region.size > 0:
            dominant_color = extract_dominant_color(square_region)
            hex_color = rgb_to_hex(dominant_color)
            color_name = get_color_name(dominant_color)
            
            colors_data.append({
                'position': i + 1,
                'rgb': dominant_color.tolist(),
                'hex': hex_color,
                'name': color_name,
                'coordinates': (x, y, w, h),
                'grid_position': f"Row {i // cols + 1}, Col {i % cols + 1}"
            })
    
    return colors_data

def generate_html_grid(all_colors_data, output_file='extracted_colors_precise.html'):
    """Generate HTML with dynamic grid layouts."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Precise Color Extraction from Suede Images</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }
        .image-section {
            background: white;
            margin: 40px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .image-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .grid-info {
            background: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
            color: #34495e;
        }
        .color-square {
            width: 60px;
            height: 60px;
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            display: inline-block;
            margin: 2px;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            cursor: pointer;
        }
        .color-square:hover {
            transform: scale(1.1);
            z-index: 10;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .color-square:hover::after {
            content: attr(data-hex);
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            white-space: nowrap;
            z-index: 20;
        }
        .summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .summary h1 {
            margin: 0 0 10px 0;
            font-size: 32px;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
        }
        .stat {
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="summary">
        <h1>Precise Color Extraction from Suede Images</h1>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">""" + str(len(all_colors_data)) + """</div>
                <div>Images Processed</div>
            </div>
            <div class="stat">
                <div class="stat-number">""" + str(sum(len(colors) for colors in all_colors_data.values())) + """</div>
                <div>Total Colors</div>
            </div>
        </div>
    </div>
"""
    
    for image_name, colors in all_colors_data.items():
        # Determine grid layout for this image
        num_colors = len(colors)
        if num_colors == 30:
            grid_layout = "6x5 grid"
        elif num_colors in [49, 50]:
            grid_layout = f"Grid with {num_colors} colors"
        else:
            grid_layout = f"{num_colors} color squares"
            
        html_content += f"""
    <div class="image-section">
        <div class="image-title">{image_name}</div>
        <div class="grid-info">
            {grid_layout} - {num_colors} colors extracted
        </div>
        <div style="line-height: 0;">
"""
        
        for i, color_data in enumerate(colors):
            hex_color = color_data['hex']
            rgb = color_data['rgb']
            
            html_content += f"""<div class="color-square" style="background-color: {hex_color};" data-hex="{hex_color}" title="RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) - {color_data['name']}"></div>"""
            
            # Add line breaks for proper grid layout
            if num_colors == 30 and (i + 1) % 5 == 0:  # 6x5 grid
                html_content += "<br>"
            elif num_colors == 49 and (i + 1) % 7 == 0:  # 7x7 grid
                html_content += "<br>"
            elif num_colors == 50 and (i + 1) % 10 == 0:  # 10x5 grid
                html_content += "<br>"
        
        html_content += """
        </div>
    </div>
"""
    
    html_content += """
    <script>
        // Copy hex code to clipboard when clicked
        document.querySelectorAll('.color-square').forEach(square => {
            square.addEventListener('click', function() {
                const hex = this.getAttribute('data-hex');
                navigator.clipboard.writeText(hex).then(() => {
                    // Show brief confirmation
                    const original = this.style.transform;
                    this.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        this.style.transform = original;
                    }, 200);
                });
            });
        });
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML grid saved to: {output_file}")

def main():
    input_folder = os.path.dirname(os.path.abspath(__file__))
    print(f"Processing images in: {input_folder}")
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(input_folder) 
                   if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print("No image files found.")
        return
    
    print(f"Found {len(image_files)} images to process with smart grid detection...")
    
    all_colors_data = {}
    
    for image_file in sorted(image_files):
        image_path = os.path.join(input_folder, image_file)
        print(f"\nProcessing: {image_file}")
        
        colors_data = process_image_smart(image_path)
        
        if colors_data:
            all_colors_data[image_file] = colors_data
            print(f"  SUCCESS: Extracted {len(colors_data)} colors")
        else:
            print(f"  FAILED to process {image_file}")
    
    if all_colors_data:
        # Generate HTML
        output_html = os.path.join(input_folder, 'extracted_colors_precise.html')
        generate_html_grid(all_colors_data, output_html)
        
        # Save JSON
        json_output = os.path.join(input_folder, 'extracted_colors_precise.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(all_colors_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nCOMPLETE!")
        print(f"HTML: {output_html}")
        print(f"JSON: {json_output}")
        print("Click on any color square in the HTML to copy its hex code!")
    else:
        print("No colors extracted.")

if __name__ == "__main__":
    main()
