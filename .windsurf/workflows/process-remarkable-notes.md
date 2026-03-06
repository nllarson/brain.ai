---
description: Process reMarkable PDFs with Claude Code OCR
---

# Process reMarkable Notes with Claude Code

This workflow processes PDFs from the inbox folder using Claude Code's built-in vision capabilities, then files structured Markdown into your Obsidian vault.

## Prerequisites

- PDFs in `inbox/` folder (run `python3 scripts/rm_ingest.py` first)
- Obsidian vault at `~/Documents/Obsidian/brain.ai-vault`
- Obsidian MCP configured in Claude Code

## Steps

### 1. List PDFs in inbox

Check what's ready to process:

```bash
ls -lh inbox/*.pdf
```

### 2. Process each PDF

For each PDF in the inbox, do the following:

**a) Read the PDF as images**

Use the `read_file` tool or image reading capability to view each page of the PDF.

**b) OCR with the system prompt**

Apply the OCR prompt from `prompts/ocr_and_structure.md`:

- Transcribe handwriting accurately
- Infer metadata (date, title, type, people, projects)
- Generate YAML frontmatter
- Structure as Markdown with headers, lists, action items
- Add `[[wikilinks]]` for people and projects

**c) Verify person names**

Before filing the note, verify all `[[Person Name]]` wikilinks with the user:

1. Extract all person names from the `people:` frontmatter field and wikilinks in the note body
2. For each person, check if a matching file exists in `~/Documents/Obsidian/brain.ai-vault/People/`
3. Present the user with:
   - **New people** (no existing file): Ask to confirm the name or provide the correct canonical name
   - **Potential duplicates**: Show similar existing names (e.g., "John", "John Smith", "John S") and ask which to use
   - **Existing people**: Auto-match (no prompt needed)

**Example prompt to user:**
```
Found these people in the note:
✓ [[Kevin]] - matches existing person
? [[Steve Gillian]] - NEW person, confirm name or provide canonical name
? [[Matt]] - Similar to: [[Matt Cagle]], [[Matthew Johnson]]. Which should I use?
  1. Matt Cagle
  2. Matthew Johnson  
  3. Keep as "Matt" (new person)
```

4. Update the note with the confirmed canonical names
5. Update both the `people:` frontmatter and all wikilinks in the body consistently

**d) Classify and file the note**

Based on the note type in frontmatter:
- `meeting` → `~/Documents/Obsidian/brain.ai-vault/Meetings/YYYY/MM-MonthName/`
- `note`, `reference`, `project` → `~/Documents/Obsidian/brain.ai-vault/Notes/Projects/`
- Other → `~/Documents/Obsidian/brain.ai-vault/Notes/Projects/`

Filename format: `YYYY-MM-DD-Title.md`

**e) Create person stubs**

For any confirmed person names that don't have files yet, create stubs:

```markdown
---
title: "Person Name"
type: person
tags:
  - person
---

# Person Name

> Auto-created stub. Add details about this person here.

## Mentioned In

```dataview
LIST
FROM "Meetings" OR "Notes"
WHERE contains(file.outlinks, this.file.link)
SORT file.name ASC
```
```

**f) Move PDF to processed**

```bash
mv inbox/filename.pdf inbox/processed/
```

### 3. Repeat for all PDFs

Process each PDF in the inbox folder.

**Note:** Person files automatically show mentions via Dataview queries - no manual update needed!

## Example Interaction

User: "Process the PDFs in my inbox"

Claude Code should:
1. List PDFs in `inbox/`
2. For each PDF:
   - Read pages as images
   - Apply OCR prompt
   - Generate structured markdown
   - **Verify person names with user** (prompt for confirmation/matching)
   - Update note with confirmed canonical names
   - Write to vault with proper folder structure
   - Create person stubs for confirmed new people
   - Move PDF to `inbox/processed/`
3. Confirm completion with list of created notes

**Example person verification:**
```
Processing: inbox/Sales-Meeting-Notes.pdf

Found these people in the note:
✓ [[Kevin]] - matches existing person
✓ [[Erika]] - matches existing person
? [[Steve Gillian]] - NEW person, confirm name? (press Enter to keep, or type correct name)
? [[Matt]] - Similar to existing people:
  1. Matt Cagle
  2. Matthew Johnson
  Which should I use? (1-2, or 3 to keep as "Matt")
```

## Notes

- This workflow uses Claude Code's built-in vision — no Anthropic API key needed
- The Obsidian MCP gives Claude Code write access to your vault
- You can trigger this manually or set up automation via a custom MCP tool
