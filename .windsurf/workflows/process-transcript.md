---
description: Process Microsoft Teams transcripts into Obsidian notes
---

# Process Teams Meeting Transcripts

This workflow processes Microsoft Teams meeting transcripts into structured Obsidian notes with AI-generated summaries, extracted action items, and verified people names.

## Prerequisites

- Teams meeting transcript (text format)
- Obsidian vault at `~/Documents/Obsidian/brain.ai-vault`
- Virtual environment activated (for script method)

## Input Methods

### Method 1: Direct Chat Paste (Fastest)

**Best for:** Quick processing, ad-hoc transcripts

1. Copy your Teams transcript to clipboard
2. In chat, say: "Process this Teams transcript" and paste the transcript
3. I will:
   - Generate custom AI summary with key points and context
   - Preserve Teams AI summary if present
   - Extract metadata (date, attendees, subject)
   - Verify people names against your vault
   - Structure into Markdown with action items
   - File to appropriate Meetings folder
   - Create person stubs for new attendees

**Pros:** Zero setup, immediate processing, interactive name verification

### Method 2: Text File Processing (Organized)

**Best for:** Batch processing, maintaining audit trail

1. Save your Teams transcript as a `.txt` file in `inbox/` folder
   - Example: `inbox/teams-meeting-2026-03-11.txt`

2. Run the processing script:
```bash
source .venv/bin/activate
python scripts/process_transcript.py inbox/teams-meeting-2026-03-11.txt
```

3. The script will:
   - Extract basic metadata
   - Display transcript info
   - Prompt for Claude Code processing

4. I will then:
   - Apply transcript structuring
   - Generate custom AI summary
   - Verify people names
   - File to Obsidian vault
   - Move source file to `inbox/processed/`

**Pros:** Organized workflow, trackable, consistent with PDF processing

## Teams Transcript Format

Teams transcripts typically include:

```
Meeting Title
Date: MM/DD/YYYY

Participants:
- John Smith
- Jane Doe

[Transcript]
John Smith: Let's discuss the project timeline.
Jane Doe: I think we should target Q2 for launch.
John Smith: That sounds reasonable.

[AI Summary]
The team discussed project timelines and agreed on a Q2 launch target.
```

## Output Structure

Processed notes will be saved as:
- **Location:** `~/Documents/Obsidian/brain.ai-vault/Meetings/YYYY/MM-MonthName/`
- **Filename:** `YYYY-MM-DD-Meeting-Subject.md`
- **Format:** Structured Markdown with frontmatter

Example output:

```markdown
---
title: "Project Timeline Discussion"
date: 2026-03-11
type: meeting
tags:
  - meeting
  - teams
  - project-planning
people:
  - "[[John Smith]]"
  - "[[Jane Doe]]"
projects:
  - "[[Project Alpha]]"
---

# Project Timeline Discussion

**Date:** 2026-03-11
**Attendees:** [[John Smith]], [[Jane Doe]]
**Platform:** Microsoft Teams

## Summary

**Key Points:**
- Discussed project timeline and launch targets
- Agreed on Q2 as realistic launch window
- Identified resource needs for Q1 preparation

**Context & Implications:**
- Q2 target aligns with market conditions
- Requires accelerated development in Q1
- Team capacity sufficient with current staffing

**Teams AI Summary:**
The team discussed project timelines and agreed on a Q2 launch target.

## Discussion

### Timeline Planning
- [[John Smith]]: Proposed discussing project timeline
- [[Jane Doe]]: Suggested Q2 launch target
- [[John Smith]]: Agreed with Q2 timeline

## Decisions

- Launch target set for Q2 2026

## Action Items

- [ ] Finalize Q1 development roadmap - [[John Smith]]
- [ ] Review resource allocation - [[Jane Doe]]
```

## Person Name Verification

Before filing the note, I will verify all people mentioned:

1. Check existing people in `~/Documents/Obsidian/brain.ai-vault/People/`
2. For new people, ask for confirmation:
   ```
   Found these people in the transcript:
   ✓ [[John Smith]] - matches existing person
   ? [[Jane Doe]] - NEW person, confirm name? (or provide full name)
   ```
3. Create person stubs for confirmed new people
4. Update all wikilinks consistently

## Tips

### Getting Teams Transcripts

1. In Teams, go to your meeting in Calendar
2. Click on the meeting → "Recap" tab
3. Click "Transcript" to view
4. Select all text and copy
5. Paste into chat or save as `.txt` file

### Improving Results

- **Include AI summary:** If Teams generated an AI summary, include it in the transcript
- **Add context:** Add a brief note at the top about the meeting purpose
- **Clean formatting:** Remove unnecessary headers or formatting artifacts
- **Date format:** Include the date clearly (MM/DD/YYYY or YYYY-MM-DD)

### Batch Processing

To process multiple transcripts:

1. Save all transcripts to `inbox/` with descriptive names
2. Process each one:
   ```bash
   for file in inbox/teams-*.txt; do
       python scripts/process_transcript.py "$file"
       # Then paste output to Claude Code for processing
   done
   ```

## Troubleshooting

**Issue:** Speaker names not recognized
- **Solution:** Ensure speaker labels follow "Name:" format. Edit transcript if needed.

**Issue:** Date not detected
- **Solution:** Add date clearly at top of transcript in MM/DD/YYYY format

**Issue:** No AI summary in output
- **Solution:** Custom AI summary is always generated. Teams summary only included if present in transcript.

**Issue:** Person names not matching
- **Solution:** During verification, provide the correct canonical name when prompted

## Example Workflow

**Quick processing:**
```
User: "Process this Teams transcript"
[pastes transcript]

Claude: [Generates structured note with summaries]
"Found 2 new people: Jane Doe, Bob Wilson. Confirm names?"

User: "Jane Doe is correct, Bob Wilson should be Robert Wilson"

Claude: [Updates note, creates person stubs, files to vault]
"✓ Filed to Meetings/2026/03-March/2026-03-11-Project-Discussion.md
✓ Created person stub for Jane Doe
✓ Created person stub for Robert Wilson"
```

## Related Workflows

- `/process-remarkable-notes` - Process handwritten notes from reMarkable
- `/meeting-briefing` - Generate pre-meeting briefings
- `/weekly-summary` - Generate weekly summaries from notes
