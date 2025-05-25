import json
import os

# Read leather colors
with open('Leather/leather_colors.json', 'r') as f:
    leather_data = json.load(f)

# Read suede colors
with open('Suede/extracted_colors_FINAL.json', 'r') as f:
    suede_data = json.load(f)

# Extract leather colors
leather_colors = []
for color in leather_data['leather_colors']:
    leather_colors.append({
        'color_number': color['color_number'],
        'hex': color['hex']
    })

# Extract suede colors - flatten from all images
suede_colors = []
for image_name, colors in suede_data.items():
    for color in colors:
        suede_colors.append({
            'color_number': color['color_number'],
            'hex': color['hex']
        })

# Sort by color number
leather_colors.sort(key=lambda x: int(x['color_number']))
suede_colors.sort(key=lambda x: int(x['color_number']))

print(f"Extracted {len(leather_colors)} leather colors")
print(f"Extracted {len(suede_colors)} suede colors")

# Generate JavaScript file
js_content = f"""// Color data for AUBLIQ Color Preview System
// Complete dataset - {len(leather_colors)} leather + {len(suede_colors)} suede colors

window.colorData = {{
    leather: {json.dumps(leather_colors, indent=8)[:-1]}    ],
    
    suede: {json.dumps(suede_colors, indent=8)[:-1]}    ]
}};
"""

# Write to file
with open('color-data.js', 'w') as f:
    f.write(js_content)

print("Created complete color-data.js file!")
