#!/usr/bin/env python3
"""
rm_upload.py — Upload PDFs to reMarkable via USB web interface

Converts Markdown briefings/summaries to PDF and uploads them to reMarkable.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

import markdown
import requests
import yaml
from weasyprint import HTML, CSS


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and return metadata + body."""
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    try:
        metadata = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return metadata or {}, body
    except yaml.YAMLError:
        return {}, content


def transform_wikilinks(text: str) -> str:
    """Transform [[Name]] wikilinks to underlined HTML."""
    # Replace [[Name]] with <span class="wikilink">Name</span>
    pattern = r'\[\[([^\]]+)\]\]'
    return re.sub(pattern, r'<span class="wikilink">\1</span>', text)


def generate_friendly_filename(metadata: dict, filepath: Path) -> str:
    """
    Generate friendly filename: "Briefing - Title (Mar 5)"
    
    Pattern: {Type} - {Title} ({Mon DD})
    """
    # Get type from metadata or filename
    doc_type = metadata.get("type", "Document")
    if doc_type == "reference" and "briefing" in metadata.get("tags", []):
        doc_type = "Briefing"
    elif doc_type == "reference":
        doc_type = "Summary"
    
    doc_type = doc_type.capitalize()
    
    # Get title from metadata or filename
    title = metadata.get("title", filepath.stem)
    # Clean up title - remove "Briefing —" prefix if present
    title = re.sub(r'^Briefing\s*[—-]\s*', '', title)
    title = re.sub(r'^Summary\s*[—-]\s*', '', title)
    
    # Get date
    date_value = metadata.get("date", datetime.now())
    try:
        # Handle both string and datetime.date objects
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
        else:
            # Already a date/datetime object
            date_obj = date_value if isinstance(date_value, datetime) else datetime.combine(date_value, datetime.min.time())
        date_formatted = date_obj.strftime("%b %d")  # "Mar 5"
    except (ValueError, AttributeError):
        date_formatted = datetime.now().strftime("%b %d")
    
    # Build filename
    filename = f"{doc_type} - {title} ({date_formatted}).pdf"
    
    # Sanitize
    filename = "".join(c if c.isalnum() or c in " -_()." else "_" for c in filename)
    
    return filename


def markdown_to_pdf(md_path: Path, output_path: Path) -> bool:
    """
    Convert Markdown file to PDF with styling.
    
    Returns True if successful, False otherwise.
    """
    try:
        # Read markdown file
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract frontmatter
        metadata, body = extract_frontmatter(content)
        
        # Transform wikilinks
        body = transform_wikilinks(body)
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'tables'])
        html_body = md.convert(body)
        
        # Build metadata section if present
        metadata_html = ""
        if metadata:
            meta_items = []
            # Only show tags if present (not date/people/projects since they're in body)
            if "tags" in metadata and metadata["tags"]:
                # Filter out 'briefing' tag and strip wikilink brackets
                tags = [tag.replace('[[', '').replace(']]', '') for tag in metadata["tags"] if tag != "briefing"]
                if tags:
                    meta_items.append(f"<strong>Tags:</strong> {', '.join(tags)}")
            
            if meta_items:
                metadata_html = f'<div class="metadata">{", ".join(meta_items)}</div>'
        
        # Build complete HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{metadata.get('title', 'Document')}</title>
</head>
<body>
    {metadata_html}
    {html_body}
</body>
</html>
"""
        
        # Load CSS
        css_path = Path(__file__).parent.parent / "templates" / "pdf_style.css"
        css = CSS(filename=str(css_path))
        
        # Generate PDF
        HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
        
        return True
        
    except Exception as e:
        print(f"Error converting Markdown to PDF: {e}")
        return False


def upload_to_remarkable(pdf_path: Path, host: str = "http://10.11.99.1") -> bool:
    """
    Upload PDF to reMarkable via USB web interface.
    
    Returns True if successful, False otherwise.
    """
    try:
        # Check connection
        try:
            resp = requests.get(f"{host}/", timeout=5)
            resp.raise_for_status()
        except requests.RequestException:
            print(f"✗ Cannot connect to reMarkable at {host}")
            print("  Make sure USB is connected and web interface is enabled:")
            print("  Settings → Storage → USB web interface → ON")
            return False
        
        # Upload file
        print(f"Uploading {pdf_path.name} to reMarkable...")
        
        with open(pdf_path, "rb") as f:
            files = {
                "file": (pdf_path.name, f, "application/pdf")
            }
            headers = {
                "Origin": host,
                "Referer": f"{host}/",
            }
            
            resp = requests.post(
                f"{host}/upload",
                files=files,
                headers=headers,
                timeout=30
            )
            resp.raise_for_status()
        
        print(f"✓ Successfully uploaded to reMarkable")
        return True
        
    except requests.RequestException as e:
        print(f"✗ Upload failed: {e}")
        return False


def upload_markdown_file(md_path: Path, config: dict) -> bool:
    """
    Main function: Convert Markdown to PDF and upload to reMarkable.
    
    Returns True if successful, False otherwise.
    """
    md_path = Path(md_path).resolve()
    
    if not md_path.exists():
        print(f"✗ File not found: {md_path}")
        return False
    
    # Read metadata for filename
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    metadata, _ = extract_frontmatter(content)
    
    # Generate friendly filename
    pdf_filename = generate_friendly_filename(metadata, md_path)
    
    # Create temp PDF
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    pdf_path = temp_dir / pdf_filename
    
    print(f"Converting {md_path.name} to PDF...")
    if not markdown_to_pdf(md_path, pdf_path):
        return False
    
    print(f"✓ PDF created: {pdf_filename}")
    
    # Upload to reMarkable
    rm_config = config.get("remarkable", {})
    host = rm_config.get("host", "http://10.11.99.1")
    
    upload_enabled = rm_config.get("upload", {}).get("enabled", True)
    if not upload_enabled:
        print("Upload disabled in config. PDF saved locally only.")
        return True
    
    success = upload_to_remarkable(pdf_path, host)
    
    # Clean up temp file
    if success:
        pdf_path.unlink()
    
    return success


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 rm_upload.py <markdown_file>")
        print("Example: python3 rm_upload.py briefings/2026-03-05-Medica-Connect-Briefing.md")
        sys.exit(1)
    
    md_file = sys.argv[1]
    config = load_config()
    
    success = upload_markdown_file(md_file, config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
