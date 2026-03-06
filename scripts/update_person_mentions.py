#!/usr/bin/env python3
"""Update person files with a list of documents where they're mentioned."""

import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path.home() / "Documents/Obsidian/brain.ai-vault"
PEOPLE_DIR = VAULT_PATH / "People"
MEETINGS_DIR = VAULT_PATH / "Meetings"
NOTES_DIR = VAULT_PATH / "Notes"

def find_person_mentions():
    """Find all mentions of people across the vault."""
    mentions = defaultdict(list)
    
    # Search in Meetings and Notes directories
    search_dirs = [MEETINGS_DIR, NOTES_DIR]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for md_file in search_dir.rglob("*.md"):
            content = md_file.read_text()
            
            # Find all wikilinks in the file
            wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
            
            for link in wikilinks:
                # Check if this person exists
                person_file = PEOPLE_DIR / f"{link}.md"
                if person_file.exists():
                    # Get relative path from vault root
                    rel_path = md_file.relative_to(VAULT_PATH)
                    mentions[link].append(str(rel_path))
    
    return mentions

def update_person_file(person_name, mentioned_in):
    """Update a person's file with the list of documents they're mentioned in."""
    person_file = PEOPLE_DIR / f"{person_name}.md"
    
    if not person_file.exists():
        return
    
    content = person_file.read_text()
    
    # Remove existing "Mentioned In" section if present
    content = re.sub(r'\n## Mentioned In\n.*?(?=\n##|\Z)', '', content, flags=re.DOTALL)
    
    # Remove trailing whitespace
    content = content.rstrip()
    
    # Add new "Mentioned In" section
    mentioned_in_section = "\n\n## Mentioned In\n\n"
    for doc_path in sorted(set(mentioned_in)):
        # Convert path to wikilink format
        doc_name = Path(doc_path).stem
        mentioned_in_section += f"- [[{doc_name}]]\n"
    
    content += mentioned_in_section
    
    person_file.write_text(content)
    print(f"Updated {person_name}: {len(set(mentioned_in))} mentions")

def main():
    print("Finding person mentions across vault...")
    mentions = find_person_mentions()
    
    print(f"\nFound mentions for {len(mentions)} people")
    print("\nUpdating person files...")
    
    for person_name, mentioned_in in mentions.items():
        update_person_file(person_name, mentioned_in)
    
    print("\n✓ Done!")

if __name__ == "__main__":
    main()
