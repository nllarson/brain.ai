#!/usr/bin/env python3
"""Convert a PDF to PNG images for OCR processing."""

import sys
from pathlib import Path
import fitz  # PyMuPDF

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
    
    # Open PDF
    doc = fitz.open(str(pdf_path))
    output_paths = []
    base_name = pdf_path.stem
    
    # Convert each page to image
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render page to image (200 DPI)
        mat = fitz.Matrix(200/72, 200/72)  # 200 DPI scaling
        pix = page.get_pixmap(matrix=mat)
        
        output_path = output_dir / f"{base_name}_page_{page_num + 1}.png"
        pix.save(str(output_path))
        output_paths.append(str(output_path))
    
    doc.close()
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
