#!/usr/bin/env python3
"""
Create sample test images for demonstrating the Smart JPEG Renamer.
"""
from PIL import Image, ImageDraw, ImageFont
import random
import os
from datetime import datetime, timedelta

def create_test_image(width, height, colors, text, filename):
    """Create a test image with given colors and text."""
    
    # Create gradient background
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Draw gradient or solid background
    if len(colors) > 1:
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        draw.rectangle([0, 0, width, height], fill=colors[0])
    
    # Add some shapes
    num_shapes = random.randint(2, 5)
    for _ in range(num_shapes):
        shape_type = random.choice(['circle', 'rectangle'])
        x1 = random.randint(0, width - 100)
        y1 = random.randint(0, height - 100)
        x2 = x1 + random.randint(50, 150)
        y2 = y1 + random.randint(50, 150)
        
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        if shape_type == 'circle':
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=color)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=color)
    
    # Add text
    try:
        # Try to use a default font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Get text bounding box for centering
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Draw text with shadow
    draw.text((text_x + 2, text_y + 2), text, font=font, fill=(0, 0, 0))
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
    
    # Save image
    image.save(filename, 'JPEG', quality=95)
    print(f"✅ Created: {filename}")

def main():
    """Generate test images."""
    
    # Create test_images directory
    os.makedirs("test_images", exist_ok=True)
    
    print("=" * 60)
    print("Creating Test Images for Smart JPEG Renamer")
    print("=" * 60)
    print()
    
    test_configs = [
        {
            'filename': 'test_images/IMG_001.jpg',
            'width': 800,
            'height': 600,
            'colors': [(135, 206, 235), (0, 119, 190)],  # Sky blue
            'text': 'BEACH'
        },
        {
            'filename': 'test_images/IMG_002.jpg',
            'width': 800,
            'height': 600,
            'colors': [(255, 140, 0), (255, 69, 0)],  # Sunset orange
            'text': 'SUNSET'
        },
        {
            'filename': 'test_images/DSC_003.jpg',
            'width': 800,
            'height': 600,
            'colors': [(34, 139, 34), (0, 100, 0)],  # Forest green
            'text': 'FOREST'
        },
        {
            'filename': 'test_images/DSC_004.jpg',
            'width': 800,
            'height': 600,
            'colors': [(70, 130, 180), (25, 25, 112)],  # Mountain blue
            'text': 'MOUNTAIN'
        },
        {
            'filename': 'test_images/P1000005.jpg',
            'width': 800,
            'height': 600,
            'colors': [(220, 20, 60), (139, 0, 0)],  # Red
            'text': 'FLOWER'
        },
        {
            'filename': 'test_images/P1000006.jpg',
            'width': 800,
            'height': 600,
            'colors': [(192, 192, 192), (128, 128, 128)],  # Gray
            'text': 'BUILDING'
        },
        {
            'filename': 'test_images/photo_007.jpg',
            'width': 800,
            'height': 600,
            'colors': [(255, 215, 0), (255, 165, 0)],  # Golden
            'text': 'CAR'
        },
        {
            'filename': 'test_images/photo_008.jpg',
            'width': 800,
            'height': 600,
            'colors': [(75, 0, 130), (138, 43, 226)],  # Purple
            'text': 'NIGHT SKY'
        },
        {
            'filename': 'test_images/snapshot_009.jpg',
            'width': 800,
            'height': 600,
            'colors': [(255, 192, 203), (255, 105, 180)],  # Pink
            'text': 'CHERRY'
        },
        {
            'filename': 'test_images/snapshot_010.jpg',
            'width': 800,
            'height': 600,
            'colors': [(210, 180, 140), (160, 82, 45)],  # Brown
            'text': 'COFFEE'
        },
    ]
    
    for config in test_configs:
        create_test_image(
            config['width'],
            config['height'],
            config['colors'],
            config['text'],
            config['filename']
        )
    
    print()
    print("=" * 60)
    print(f"✅ Created {len(test_configs)} test images in test_images/")
    print()
    print("🚀 You can now test the app with these images:")
    print("   1. Run: streamlit run app.py")
    print("   2. Upload files from test_images/ directory")
    print("   3. Generate suggestions and see the AI at work!")
    print("=" * 60)

if __name__ == "__main__":
    main()

