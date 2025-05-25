import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import os
import json
from collections import Counter
import webcolors

def extract_dominant_color(image_region, n_clusters=3):
    """
    Extract the dominant color from an image region using K-means clustering.
    This helps to ignore texture and focus on the main color.
    """
    # Reshape the image to be a list of pixels
    pixels = image_region.reshape(-1, 3)
    
    # Apply K-means clustering to find dominant colors
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get the colors and their frequencies
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    # Count the frequency of each cluster
    label_counts = Counter(labels)
    
    # Get the most frequent color (dominant color)
    dominant_label = label_counts.most_common(1)[0][0]
    dominant_color = colors[dominant_label]
    
    return dominant_color.astype(int)

def rgb_to_hex(rgb):
    """Convert RGB values to hex color code."""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color_name(rgb):
    """Try to get a human-readable color name."""
    try:
        closest_name = webcolors.rgb_to_name((int(rgb[0]), int(rgb[1]), int(rgb[2])))
        return closest_name
    except ValueError:
        # If exact match not found, find closest color
        min_colors = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - rgb[0]) ** 2
            gd = (g_c - rgb[1]) ** 2
            bd = (b_c - rgb[2]) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

def detect_grid_squares(image):
    """
    Detect square regions in the image using edge detection and contour finding.
    Returns coordinates of detected squares.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    squares = []
    for contour in contours:
        # Approximate the contour to reduce number of points
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Check if the contour has 4 vertices (potential square/rectangle)
        if len(approx) == 4:
            # Calculate area to filter out very small regions
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                # Check if it's roughly square-shaped
                aspect_ratio = w / h
                if 0.8 <= aspect_ratio <= 1.2:  # Allow some tolerance
                    squares.append((x, y, w, h))
    
    return squares

def create_uniform_grid(image, rows=3, cols=3):
    """
    Create a uniform grid if automatic detection fails.
    Divides the image into equal squares.
    """
    height, width = image.shape[:2]
    
    # Calculate dimensions for each grid cell
    cell_width = width // cols
    cell_height = height // rows
    
    squares = []
    for row in range(rows):
        for col in range(cols):
            x = col * cell_width
            y = row * cell_height
            squares.append((x, y, cell_width, cell_height))
    
    return squares

def process_image(image_path, grid_rows=3, grid_cols=3):
    """
    Process a single image to extract colors from grid squares.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return None
    
    # Convert BGR to RGB (OpenCV uses BGR by default)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Try to detect squares automatically
    squares = detect_grid_squares(image)
    
    # If detection fails or finds too few squares, use uniform grid
    if len(squares) < grid_rows * grid_cols:
        print(f"Auto-detection found {len(squares)} squares, using uniform grid instead")
        squares = create_uniform_grid(image_rgb, grid_rows, grid_cols)
    
    colors_data = []
    
    for i, (x, y, w, h) in enumerate(squares):
        # Extract the square region
        square_region = image_rgb[y:y+h, x:x+w]
        
        if square_region.size > 0:
            # Extract dominant color
            dominant_color = extract_dominant_color(square_region)
            
            # Convert to hex
            hex_color = rgb_to_hex(dominant_color)
            
            # Get color name
            color_name = get_color_name(dominant_color)
            
            colors_data.append({
                'position': i + 1,
                'rgb': dominant_color.tolist(),
                'hex': hex_color,
                'name': color_name,
                'coordinates': (x, y, w, h)
            })
    
    return colors_data

def generate_html_grid(all_colors_data, output_file='color_grid.html'):
    """
    Generate an HTML file with color grids for all processed images.
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extracted Color Grids</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .image-section {
            background: white;
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .image-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        .color-grid {
            display: grid;
            grid-template-columns: repeat(3, 120px);
            gap: 10px;
            margin: 20px 0;
        }
        .color-square {
            width: 120px;
            height: 120px;
            border: 2px solid #ddd;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .color-info {
            background: rgba(255,255,255,0.9);
            padding: 5px;
            border-radius: 3px;
            text-align: center;
            font-size: 11px;
            font-weight: bold;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
        }
        .hex-code {
            font-family: monospace;
            font-size: 12px;
            margin-top: 2px;
        }
        .color-name {
            font-size: 10px;
            margin-top: 2px;
            text-transform: capitalize;
        }
    </style>
</head>
<body>
    <h1>Extracted Color Grids from Suede Images</h1>
"""
    
    for image_name, colors in all_colors_data.items():
        html_content += f"""
    <div class="image-section">
        <div class="image-title">{image_name}</div>
        <div class="color-grid">
"""
        
        for color_data in colors:
            rgb = color_data['rgb']
            hex_color = color_data['hex']
            color_name = color_data['name']
            
            html_content += f"""
            <div class="color-square" style="background-color: {hex_color};">
                <div class="color-info">
                    <div class="hex-code">{hex_color}</div>
                    <div class="color-name">{color_name}</div>
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML grid saved to: {output_file}")

def main():
    # Set the input folder path (current directory)
    input_folder = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Processing images in: {input_folder}")
    
    # Get all image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(input_folder) 
                   if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print("No image files found in the current folder.")
        return
    
    print(f"Found {len(image_files)} images to process...")
    
    all_colors_data = {}
    
    # Process each image
    for image_file in sorted(image_files):
        image_path = os.path.join(input_folder, image_file)
        print(f"Processing: {image_file}")
        
        colors_data = process_image(image_path)
        
        if colors_data:
            all_colors_data[image_file] = colors_data
            print(f"  Extracted {len(colors_data)} colors")
        else:
            print(f"  Failed to process {image_file}")
    
    # Generate HTML output
    if all_colors_data:
        output_html = os.path.join(input_folder, 'extracted_colors.html')
        generate_html_grid(all_colors_data, output_html)
        
        # Also save as JSON for further processing
        json_output = os.path.join(input_folder, 'extracted_colors.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(all_colors_data, f, indent=2, ensure_ascii=False)
        
        print(f"Color data also saved as JSON: {json_output}")
        print("Processing complete!")
        print(f"Open {output_html} in your browser to view the results!")
    else:
        print("No colors extracted from any images.")

if __name__ == "__main__":
    main()
