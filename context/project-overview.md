Perfect — that gives me everything I need. Here's a comprehensive plan tailored to your exact setup.

---

## The Big Picture

Since you don't have Connect, USB transfer becomes your ingestion point. The pipeline looks like this:

```
reMarkable (USB) → Raw PDFs/SVGs
       ↓
  Ingestion Script (watches a folder)
       ↓
  Claude API (OCR + structure + tags)
       ↓
  Obsidian Vault (markdown files, properly filed)
       ↓
  Claude Code / MCP (briefings, summaries, linking)
```

---

## Phase 1 — Getting Notes Off the reMarkable

Without Connect, the reMarkable mounts as a USB drive and exposes raw `.rm` files (a proprietary format) plus rendered PDFs if you export manually from the device. **The practical approach:**

- Use the **reMarkable USB web interface** — when plugged in, the tablet hosts a local web UI at `http://10.11.99.1` where you can download notebooks as PDFs, SVGs, or PNGs without any subscription.
- A small Python script (run on a schedule or triggered manually) can hit that API, pull new/changed notebooks, and drop them into a watched **Inbox folder** on your Mac.

**Tool:** `rmapi` (open source) or a simple `requests`-based script hitting the USB API.

---

## Phase 2 — OCR + Structuring with Claude

This is where Claude does the heavy lifting. Each ingested PDF/image goes through a Claude API call that:

1. **OCRs the handwriting** into clean text (Claude Vision is excellent at this)
2. **Infers metadata** — date, meeting name, attendees mentioned, topics
3. **Generates frontmatter** — YAML tags, links to related people/projects
4. **Formats as Markdown** — headers, bullet points, action items called out

The output is a `.md` file ready for Obsidian, filed into a folder structure like:
```
/Meetings/2026/03/
/Notes/Projects/
/People/
```

---

## Phase 3 — Obsidian Integration

The processed markdown files land directly in your Obsidian vault. A few things get wired up:

- **Dataview plugin** — lets you query your notes like a database (e.g., "show all notes mentioning John from last 30 days")
- **Templater plugin** — Claude-generated frontmatter plays nicely with this
- **Graph view** — once notes are properly linked with `[[wikilinks]]`, the graph becomes genuinely useful

Claude will embed `[[Person Name]]` and `[[Project Name]]` links directly in the markdown so Obsidian's graph and backlinks populate automatically.

---

## Phase 4 — The MCP Layer (where it gets powerful)

This is where Claude Code and MCPs come in. You'd build or configure two MCPs:

**1. Obsidian MCP** (community MCP already exists)
- Gives Claude Code read/write access to your vault
- Enables: "summarize everything from this week" or "find all notes where we discussed the Henderson account"

**2. Microsoft 365 MCP** (Microsoft has an official MCP for Graph API)
- Reads your Outlook calendar
- Every morning (or on-demand), Claude pulls your day's meetings, searches Obsidian for relevant past notes on those attendees/topics, and generates a **briefing note** dropped into your vault

So the morning workflow becomes: Claude wakes up, sees you have a 10am with Sarah about Project Atlas, finds your three previous meeting notes mentioning both, and writes a `2026-03-05-sarah-atlas-briefing.md` in your vault.

---

## Build Order (Recommended)

| Step | What | Time |
|------|------|------|
| 1 | USB ingestion script (Python, pulls PDFs from reMarkable) | 1-2 hrs |
| 2 | Claude OCR + markdown generator script | 2-3 hrs |
| 3 | Wire it to your Obsidian vault, test filing logic | 1-2 hrs |
| 4 | Set up launchd (macOS) to run ingestion on a schedule | 30 min |
| 5 | Install & configure Obsidian MCP in Claude Code | 1 hr |
| 6 | Microsoft Graph / Outlook MCP + briefing prompt | 2-3 hrs |
| 7 | Weekly summary prompt + Dataview dashboard | 1-2 hrs |

---

## What We'd Build with Claude Code

The core of this is **two Python scripts + one Claude Code MCP config:**

- `rm_ingest.py` — polls the reMarkable USB API, downloads new notebooks
- `process_notes.py` — sends to Claude API, writes structured markdown to vault
- `mcp_config.json` — wires Obsidian + M365 MCPs into Claude Code for the briefing/summary layer