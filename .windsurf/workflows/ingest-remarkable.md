---
description: Ingest documents from reMarkable tablet
---

# Ingest reMarkable Documents

This workflow downloads new/modified notebooks from your reMarkable tablet via USB to the inbox folder.

## Prerequisites

- reMarkable tablet connected via USB
- USB web interface enabled on reMarkable: Settings → Storage → USB web interface → ON
- reMarkable should show IP address `10.11.99.1`

## Steps

### 1. Run the ingestion script

// turbo
```bash
source .venv/bin/activate && python3 scripts/rm_ingest.py
```

This will:
- Connect to reMarkable at `http://10.11.99.1`
- Download new/modified notebooks as PDFs to `inbox/`
- Filter out excluded notebooks (2026 - Planner, Archive, Books, Personal)
- Track downloaded documents in `.state.json` to avoid re-downloading
- Move downloaded PDFs to the inbox folder

### 2. Review downloaded files

Check the output to see which files were downloaded and are ready for processing.

## Troubleshooting

If the connection fails:
1. Verify USB cable is connected
2. Check that USB web interface is ON in reMarkable settings
3. Confirm the IP address shown on reMarkable matches `10.11.99.1`
4. Try unplugging and reconnecting the USB cable

## Next Steps

After ingestion, you can process the PDFs using the `/process-remarkable-notes` workflow to convert them into structured Markdown notes in your Obsidian vault.
