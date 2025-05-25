import cv2
import numpy as np
from sklearn.cluster import KMeans
import os
import json
from collections import Counter

def extract_dominant_color(image_region, n_clusters=5):
    """
    Extract the dominant color from an image region using K-means clustering.
    """
    pixels = image_region.reshape(-1, 3)
    
    # Skip if too few pixels
    if len(pixels) < 10:
        return np.array([128, 128, 128])  # Default gray
    
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

def detect_grid_lines(image, min_line_length=100):
    """
    Detect horizontal and vertical grid lines in the image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 30, 100)
    
    # Detect lines using HoughLinesP
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                           minLineLength=min_line_length, maxLineGap=10)
    
    horizontal_lines = []
    vertical_lines = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate angle to determine if line is horizontal or vertical
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            
            if abs(angle) < 15 or abs(angle) > 165:  # Horizontal lines
                horizontal_lines.append(line[0])
            elif abs(abs(angle) - 90) < 15:  # Vertical lines
                vertical_lines.append(line[0])
    
    return horizontal_lines, vertical_lines

def create_grid_from_lines(horizontal_lines, vertical_lines, image_shape):
    """
    Create grid squares from detected lines.
    """
    height, width = image_shape[:2]
    
    # Extract y-coordinates from horizontal lines and x-coordinates from vertical lines
    h_coords = []
    for line in horizontal_lines:
        h_coords.append((line[1] + line[3]) // 2)  # Average y coordinate
    
    v_coords = []
    for line in vertical_lines:
        v_coords.append((line[0] + line[2]) // 2)  # Average x coordinate
    
    # Add image boundaries
    h_coords.extend([0, height])
    v_coords.extend([0, width])
    
    # Remove duplicates and sort
    h_coords = sorted(list(set(h_coords)))
    v_coords = sorted(list(set(v_coords)))
    
    # Create grid squares
    squares = []
    for i in range(len(h_coords) - 1):
        for j in range(len(v_coords) - 1):
            x = v_coords[j]
            y = h_coords[i]
            w = v_coords[j + 1] - x
            h = h_coords[i + 1] - y
            
            # Filter out very small squares
            if w > 20 and h > 20:
                squares.append((x, y, w, h))
    
    return squares

def analyze_image_grid(image_path):
    """
    Analyze an image to determine its grid structure.
    """
    image = cv2.imread(image_path)
    if image is None:
        return None, None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print(f"  Image dimensions: {image_rgb.shape[1]} x {image_rgb.shape[0]}")
    
    # Try to detect grid lines
    h_lines, v_lines = detect_grid_lines(image_rgb)
    
    print(f"  Detected {len(h_lines)} horizontal lines, {len(v_lines)} vertical lines")
    
    if len(h_lines) > 2 and len(v_lines) > 2:
        # Try grid from detected lines
        squares = create_grid_from_lines(h_lines, v_lines, image_rgb.shape)
        if len(squares) > 20:  # If we get a reasonable number of squares
            print(f"  Grid detection successful: {len(squares)} squares")
            return image_rgb, squares
    
    # Fallback: Ask user for grid dimensions
    print(f"  Grid detection failed. Please specify grid dimensions.")
    return image_rgb, None

def process_image_interactive(image_path):
    """
    Process image with user interaction for grid specification.
    """
    image_rgb, auto_squares = analyze_image_grid(image_path)
    
    if image_rgb is None:
        return None
    
    if auto_squares is not None:
        use_auto = input(f"    Use auto-detected {len(auto_squares)} squares? (y/n): ").lower().strip()
        if use_auto == 'y':
            squares = auto_squares
        else:
            squares = None
    else:
        squares = None
    
    if squares is None:
        # Ask user for manual grid specification
        print("    Please specify grid dimensions:")
        try:
            rows = int(input("    Number of rows: "))
            cols = int(input("    Number of columns: "))
            squares = create_manual_grid(image_rgb, rows, cols)
        except ValueError:
            print("    Invalid input. Using default 6x5 grid.")
            squares = create_manual_grid(image_rgb, 6, 5)
    
    return extract_colors_from_squares(image_rgb, squares)

def create_manual_grid(image, rows, cols):
    """Create a manual grid with specified dimensions."""
    height, width = image.shape[:2]
    cell_width = width // cols
    cell_height = height // rows
    
    squares = []
    for row in range(rows):
        for col in range(cols):
            x = col * cell_width
            y = row * cell_height
            squares.append((x, y, cell_width, cell_height))
    
    return squares

def extract_colors_from_squares(image_rgb, squares):
    """Extract colors from the detected squares."""
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
                'coordinates': (x, y, w, h)
            })
    
    return colors_data

def main():
    input_folder = os.path.dirname(os.path.abspath(__file__))
    print(f"Processing images in: {input_folder}")
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(input_folder) 
                   if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print("No image files found.")
        return
    
    print(f"Found {len(image_files)} images to process...")
    print("\nWe'll process each image individually to get the correct grid size.")
    
    all_colors_data = {}
    
    for image_file in sorted(image_files):
        image_path = os.path.join(input_folder, image_file)
        print(f"\n=== Processing: {image_file} ===")
        
        colors_data = process_image_interactive(image_path)
        
        if colors_data:
            all_colors_data[image_file] = colors_data
            print(f"  SUCCESS: Extracted {len(colors_data)} colors")
        else:
            print(f"  FAILED to process {image_file}")
    
    # Generate outputs
    if all_colors_data:
        # Save JSON
        json_output = os.path.join(input_folder, 'extracted_colors_precise.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(all_colors_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== COMPLETE ===")
        print(f"Color data saved as: {json_output}")
        print("Next step: We can generate the HTML grid with precise colors!")
    else:
        print("No colors extracted from any images.")

if __name__ == "__main__":
    main()
