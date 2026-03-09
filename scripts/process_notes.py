#!/usr/bin/env python3
"""
Process reMarkable PDFs: Convert to images and prepare for OCR processing.
"""

import sys
from pathlib import Path
from pdf2image import convert_from_path

def pdf_to_images(pdf_path: Path, output_dir: Path) -> list[Path]:
    """Convert PDF to images, one per page."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert PDF to images
    images = convert_from_path(str(pdf_path), dpi=150)
    
    image_paths = []
    base_name = pdf_path.stem
    
    for i, image in enumerate(images, 1):
        image_path = output_dir / f"{base_name}_page_{i}.png"
        image.save(str(image_path), "PNG")
        image_paths.append(image_path)
    
    return image_paths

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 process_notes.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)
    
    # Create temp directory for images
    temp_dir = Path(__file__).parent.parent / "temp" / "pdf_images" / pdf_path.stem
    
    print(f"Converting {pdf_path.name} to images...")
    image_paths = pdf_to_images(pdf_path, temp_dir)
    
    print(f"✓ Created {len(image_paths)} images in {temp_dir}")
    for img in image_paths:
        print(f"  - {img.name}")
    
    return image_paths

if __name__ == "__main__":
    main()
