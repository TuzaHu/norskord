#!/usr/bin/env python3
"""
Simple script to create placeholder app icons for PREPP-Lingo
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple app icon"""
    # Create image with blue background
    img = Image.new('RGB', (size, size), color='#2563eb')
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    margin = size // 6
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill='#60a5fa', outline='white', width=size//40)
    
    # Try to add text
    try:
        # Use a large font size
        font_size = size // 3
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        text = "PL"
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        
        draw.text((x, y), text, fill='white', font=font)
    except Exception as e:
        print(f"Could not add text: {e}")
    
    # Save
    img.save(filename, 'PNG')
    print(f"✅ Created: {filename}")

if __name__ == "__main__":
    # Check if PIL is available
    try:
        create_icon(192, 'icon-192.png')
        create_icon(512, 'icon-512.png')
        print("\n🎉 Icons created successfully!")
        print("You can replace these with custom icons later.")
    except ImportError:
        print("❌ PIL/Pillow not installed. Creating simple placeholder...")
        print("Run: pip install Pillow")
        print("Or create icons manually at: https://favicon.io/")
