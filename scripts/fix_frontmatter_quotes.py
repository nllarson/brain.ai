#!/usr/bin/env python3
"""Add quotes back to wikilinks in frontmatter."""

import re
from pathlib import Path

VAULT_PATH = Path.home() / "Documents/Obsidian/brain.ai-vault"
MEETINGS_DIR = VAULT_PATH / "Meetings"
NOTES_DIR = VAULT_PATH / "Notes"

def fix_frontmatter(file_path: Path):
    """Add quotes around wikilinks in frontmatter if missing."""
    content = file_path.read_text()
    
    # Match frontmatter section
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False
    
    frontmatter = frontmatter_match.group(1)
    original_frontmatter = frontmatter
    
    # Fix unquoted wikilinks in people and projects lists
    # Match lines like:  - [[Name]] and convert to  - "[[Name]]"
    frontmatter = re.sub(
        r'^(\s+- )(\[\[[^\]]+\]\])$',
        r'\1"\2"',
        frontmatter,
        flags=re.MULTILINE
    )
    
    if frontmatter != original_frontmatter:
        # Replace frontmatter in content
        new_content = content.replace(
            f'---\n{original_frontmatter}\n---',
            f'---\n{frontmatter}\n---',
            1
        )
        file_path.write_text(new_content)
        return True
    
    return False

def main():
    print("Adding quotes to wikilinks in frontmatter...\n")
    
    fixed_count = 0
    search_dirs = [MEETINGS_DIR, NOTES_DIR]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        for md_file in search_dir.rglob("*.md"):
            if fix_frontmatter(md_file):
                print(f"✓ Fixed {md_file.relative_to(VAULT_PATH)}")
                fixed_count += 1
    
    print(f"\n✓ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
