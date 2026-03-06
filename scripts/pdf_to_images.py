#!/usr/bin/env python3
"""Convert a PDF to PNG images for OCR processing."""

import sys
from pathlib import Path
from pdf2image import convert_from_path

def pdf_to_images(pdf_path: str, output_dir: str = None) -> list[str]:
    """
    Convert PDF to PNG images, one per page.
    
    Returns list of output image paths.
    """
    pdf_path = Path(pdf_path)
    
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = pdf_path.parent / "temp_images"
    
    output_dir.mkdir(exist_ok=True)
    
    # Convert PDF to images
    images = convert_from_path(str(pdf_path), dpi=200, fmt="png")
    
    output_paths = []
    base_name = pdf_path.stem
    
    for i, img in enumerate(images, 1):
        output_path = output_dir / f"{base_name}_page_{i}.png"
        img.save(output_path, "PNG")
        output_paths.append(str(output_path))
    
    return output_paths

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_images.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    images = pdf_to_images(pdf_file)
    
    print(f"Converted {len(images)} page(s):")
    for img in images:
        print(f"  {img}")
