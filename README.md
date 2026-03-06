# brain.ai — Second Brain Pipeline

**reMarkable Pro → Claude Code OCR → Obsidian Vault**

Automatically ingest handwritten notes from a reMarkable tablet, OCR them with Claude Code, and file structured Markdown into your Obsidian vault — complete with frontmatter, wikilinks, and action items.

## Architecture

```
reMarkable (USB) ←──────────────────────────────┐
       ↓                                         │
  rm_ingest.py (downloads new notebooks)         │
       ↓                                         │
  Claude Code (OCR + structuring)                │
       ↓                                         │
  Obsidian Vault (markdown with [[wikilinks]])   │
       ↓                                         │
  Claude Code + MCP (summaries, briefings)       │
       ↓                                         │
  rm_upload.py (sync PDFs back) ─────────────────┘
```

**Two-way sync**: Download handwritten notes from reMarkable, process them into Obsidian, then sync generated briefings and summaries back to reMarkable as PDFs.

## Prerequisites

- **Python 3.11+** (for rm_ingest.py only)
- **Claude Code** (Windsurf IDE with Claude integration)
- **reMarkable tablet** with USB web interface enabled
- **Obsidian** with vault at `~/Documents/Obsidian/brain.ai-vault`
- **Obsidian MCP** configured in Claude Code

## Setup

### 1. Install Python dependencies (for rm_ingest.py)

```bash
cd /path/to/brain.ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Obsidian MCP in Claude Code

Add the MCP server config to your Claude Code settings:

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian", "~/Documents/Obsidian/brain.ai-vault"],
      "env": {}
    }
  }
}
```

Or copy from `mcp/mcp_config.json`.

### 3. Configure paths and filtering

Edit `config.yaml` to match your paths and preferences:

```yaml
vault_path: ~/Documents/Obsidian/brain.ai-vault
inbox_path: ./inbox
remarkable:
  host: http://10.11.99.1
  # Optional: filter notebooks by name patterns
  include_patterns:
    - "Meeting*"
    - "Work*"
  exclude_patterns:
    - "*Draft*"
```

**Notebook Filtering** (optional):
- Leave `include_patterns` empty to download all notebooks
- Set `include_patterns` to only download notebooks matching those patterns
- Use `exclude_patterns` to skip specific notebooks (even if they match include)
- Supports wildcards: `*` (any characters), `?` (single character), `[abc]` (character set)
- Case-insensitive matching

**Folder-based filtering**:
- `"Sales"` → all notebooks in the Sales folder
- `"Sales/*"` → same as above (explicit wildcard)
- `"Sales/Aruba"` → specific notebook named "Aruba" in Sales folder
- `"Personal"` → all notebooks in Personal folder

**Name-based filtering**:
- `"Meeting*"` → notebooks with names starting with "Meeting"
- `"*1:1*"` → notebooks with "1:1" anywhere in the name
- `"Work*"` → notebooks starting with "Work"

**Combined example**:
```yaml
include_patterns:
  - "Sales"          # All notebooks in Sales folder
  - "Meeting*"       # Any notebook starting with "Meeting"
exclude_patterns:
  - "*Draft*"        # Skip drafts
  - "Archive"        # Skip Archive folder
```

### 4. Enable reMarkable USB web interface

On your reMarkable tablet:
1. Go to **Settings → Storage**
2. Enable **USB web interface**
3. Connect via USB cable

## Usage

### Step 1: Download notebooks from reMarkable

```bash
# Connect reMarkable via USB, then run:
python3 scripts/rm_ingest.py
```

This downloads new/changed notebooks as PDFs into `inbox/`.

### Step 2: Process with Claude Code

In Claude Code, use the workflow:

```
/process-remarkable-notes
```

Or simply ask:

> "Process the PDFs in my inbox folder and file them into my Obsidian vault"

Claude Code will:
1. Read each PDF in `inbox/`
2. OCR the handwriting using vision
3. Generate structured Markdown with frontmatter
4. File notes into your vault with proper folder structure
5. Create person stubs for `[[wikilinks]]`
6. Move processed PDFs to `inbox/processed/`

### Automated ingestion (optional)

You can automate the reMarkable download step with launchd:

```bash
# Edit the plist to only run rm_ingest.py (remove process_notes.py)
nano launchd/com.brain-ai.ingest.plist

# Create logs directory
mkdir -p logs

# Install the job
cp launchd/com.brain-ai.ingest.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.brain-ai.ingest.plist
```

Then process PDFs with Claude Code whenever convenient.

**Note**: The provided plist runs both ingestion and processing. Edit it to only run `rm_ingest.py` if using the Claude Code workflow.

## Using Claude Code with Your Vault

Once notes are in your vault, use Claude Code for:

### Processing new notes
- *"Process the PDFs in my inbox"* — triggers the OCR workflow

### Querying and summarizing
- *"Summarize everything from this week"*
- *"Find all notes about Project Atlas"*
- *"Generate a briefing for my meeting with Sarah"*

### Weekly summaries
Use the prompt in `prompts/weekly_summary.md` to generate weekly digests.

### Meeting briefings
Use the prompt in `prompts/briefing.md` before meetings to get context from past notes.

## Syncing Back to reMarkable

Generated briefings and summaries can be automatically synced back to your reMarkable as PDFs.

### Automatic Sync (via Workflows)

When using the `/meeting-briefing` or `/weekly-summary` workflows, PDFs are automatically uploaded to your reMarkable:

```bash
# Workflows automatically run:
python3 scripts/rm_upload.py briefings/2026-03-05-Medica-Connect-Briefing.md
```

The PDF will appear on your reMarkable with a friendly name like:
- **"Briefing - Medica Connect (Mar 5)"**
- **"Summary - Weekly (Mar 5)"**

Features:
- Wikilinks `[[Person Name]]` rendered as underlined text
- Clean e-ink-friendly formatting
- Proper spacing and readability
- Uploaded to root level (organize manually on device)

### Manual Sync

Upload any Markdown file to reMarkable:

```bash
source .venv/bin/activate
python3 scripts/rm_upload.py path/to/file.md
```

### Configuration

Control sync behavior in `config.yaml`:

```yaml
remarkable:
  upload:
    enabled: true      # Enable/disable upload
    auto_sync: true    # Auto-upload after generation
```

### Requirements

The upload script requires system libraries for PDF generation:

```bash
# macOS (via Homebrew)
brew install pango

# Already installed if you followed setup
pip install weasyprint markdown
```

## Vault Structure

Notes are automatically filed into:

```
brain.ai-vault/
├── Meetings/
│   └── 2026/
│       └── 03/
│           └── 2026-03-05-Sprint-Review.md
├── Notes/
│   └── Projects/
│       └── 2026-03-04-Atlas-Architecture.md
├── People/
│   ├── Sarah Chen.md
│   └── John Davis.md
└── Daily/
```

## Claude Prompts

Three prompts are included in `prompts/`:

| Prompt | Purpose |
|--------|---------|
| `ocr_and_structure.md` | System prompt for handwriting OCR + markdown generation |
| `weekly_summary.md` | Generates weekly summaries from vault notes |
| `briefing.md` | Pre-meeting briefings from past notes |

## Troubleshooting

**reMarkable not connecting:**
- Ensure USB cable is connected (not just charging)
- Enable USB web interface: Settings → Storage → USB web interface
- Test: open `http://10.11.99.1` in a browser

**Claude Code can't write to vault:**
- Verify Obsidian MCP is configured correctly in Claude Code settings
- Check vault path in `mcp/mcp_config.json` matches your actual vault location
- Test: ask Claude Code "List files in my Obsidian vault"

**OCR quality issues:**
- Ensure PDFs are high resolution (reMarkable exports at good quality by default)
- Try processing one page at a time for very dense notes
- Adjust the OCR prompt in `prompts/ocr_and_structure.md` if needed

**PDF upload fails:**
- Ensure reMarkable is connected via USB
- Check USB web interface is enabled: Settings → Storage → USB web interface
- Test connection: `curl http://10.11.99.1`
- Install system dependencies: `brew install pango` (macOS)
- Check upload is enabled in `config.yaml`

## File Structure

```
brain.ai/
├── config.yaml              # Central configuration
├── requirements.txt         # Python dependencies (minimal)
├── README.md                # This file
├── context/
│   └── project-overview.md  # Original project plan
├── scripts/
│   ├── rm_ingest.py         # reMarkable → inbox (PDF download)
│   ├── rm_upload.py         # Obsidian → reMarkable (PDF upload)
│   └── process_notes.py.standalone-reference  # Old standalone script (reference)
├── templates/
│   └── pdf_style.css        # PDF styling for reMarkable e-ink display
├── prompts/
│   ├── ocr_and_structure.md # OCR system prompt for Claude Code
│   ├── weekly_summary.md    # Weekly summary prompt
│   └── briefing.md          # Meeting briefing prompt
├── briefings/               # Generated meeting briefings
├── summaries/               # Generated weekly summaries
├── mcp/
│   └── mcp_config.json      # Obsidian MCP config for Claude Code
├── launchd/
│   └── com.brain-ai.ingest.plist  # macOS scheduled task (optional)
├── .windsurf/
│   └── workflows/
│       └── process-remarkable-notes.md  # Claude Code workflow
├── inbox/                   # Raw PDFs land here
│   └── processed/           # PDFs move here after processing
└── logs/                    # launchd output logs (if using automation)
```

## Standalone Mode (Alternative)

If you prefer to use the Anthropic API directly instead of Claude Code:

1. Set `processing_mode: standalone` in `config.yaml`
2. Rename `scripts/process_notes.py.standalone-reference` back to `process_notes.py`
3. Add `anthropic>=0.40.0`, `pdf2image>=1.17.0`, `Pillow>=10.0.0` to `requirements.txt`
4. Set `ANTHROPIC_API_KEY` environment variable
5. Run: `python3 scripts/process_notes.py`
