#!/usr/bin/env python3
"""Convert person files from static mentions to Dataview queries."""

import re
from pathlib import Path

VAULT_PATH = Path.home() / "Documents/Obsidian/brain.ai-vault"
PEOPLE_DIR = VAULT_PATH / "People"

DATAVIEW_QUERY = """
## Mentioned In

```dataview
LIST
FROM "Meetings" OR "Notes"
WHERE contains(file.outlinks, this.file.link)
SORT file.name ASC
```
"""

def convert_person_file(person_file: Path):
    """Replace static Mentioned In section with Dataview query."""
    content = person_file.read_text()
    
    # Remove existing "Mentioned In" section (both static and dataview)
    content = re.sub(r'\n## Mentioned In\n.*?(?=\n##|\Z)', '', content, flags=re.DOTALL)
    
    # Remove trailing whitespace
    content = content.rstrip()
    
    # Add Dataview query
    content += DATAVIEW_QUERY
    
    person_file.write_text(content)
    print(f"✓ Converted {person_file.stem}")

def main():
    print("Converting person files to use Dataview queries...\n")
    
    person_files = list(PEOPLE_DIR.glob("*.md"))
    
    for person_file in person_files:
        convert_person_file(person_file)
    
    print(f"\n✓ Converted {len(person_files)} person files")
    print("\nMake sure Dataview plugin is installed and enabled in Obsidian!")

if __name__ == "__main__":
    main()
