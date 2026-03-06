---
description: Generate a pre-meeting briefing from past Obsidian notes
---

# Meeting Briefing Workflow

This workflow generates a comprehensive briefing document before a meeting by analyzing past interactions, notes, and context from your Obsidian vault.

## Step 1: Get Meeting Details

Ask the user for:
- **Who** is the meeting with? (person or company name)
- **What** is the meeting about? (topic or purpose)
- **When** is the meeting? (date/time)

## Step 2: Read the Briefing Prompt

Read the system prompt that defines how to generate meeting briefings:

@/Users/nicklaslarson/code/brain.ai/prompts/briefing.md

## Step 3: Search Obsidian Vault for Relevant Context

Use the Obsidian MCP to search for:
- Past meeting notes with this person/company
- Project notes related to this person/company
- Action items involving this person/company
- Any mentions of the meeting topic

Search strategies:
- Search for the person's name: `[[Person Name]]`
- Search for the company/project: `[[Company Name]]`
- Search for related tags
- Look at recent notes (last 3-6 months most relevant)

## Step 4: Analyze Past Interactions

Review all found notes and extract:
- **Relationship history**: How long have you worked together? Past meetings?
- **Current projects**: What are you working on together?
- **Open action items**: What's pending from previous meetings?
- **Key decisions**: What was decided in past meetings?
- **Pain points**: What challenges have been discussed?
- **Opportunities**: What opportunities have been identified?

## Step 5: Generate the Briefing Document

Using the briefing prompt as your guide, create a comprehensive briefing that includes:

1. **Meeting Context**
   - Who, what, when
   - Purpose and objectives

2. **Relationship Summary**
   - History of interactions
   - Current status

3. **Recent Activity**
   - Last meeting summary
   - Recent developments

4. **Open Items**
   - Pending action items
   - Unresolved questions

5. **Discussion Topics**
   - Suggested agenda items
   - Key questions to ask

6. **Preparation Notes**
   - What to bring
   - What to review beforehand

## Step 6: Save the Briefing and Sync to reMarkable

Save the generated briefing to your Obsidian vault:
- Location: `Briefings/YYYY-MM-DD-[Person-Name]-Briefing.md`
- Include YAML frontmatter with meeting details
- Add backlinks to relevant notes and people

// turbo
Then immediately upload to reMarkable as a PDF:

```bash
python3 scripts/rm_upload.py briefings/YYYY-MM-DD-[Person-Name]-Briefing.md
```

This converts the Markdown briefing to a PDF with:
- Underlined wikilinks for easy reading
- Clean e-ink-friendly formatting
- Friendly filename: "Briefing - [Person Name] (Mon DD)"

The PDF will appear on your reMarkable tablet for reference during the meeting.

## Step 7: Present the Briefing

Show the user:
- The complete briefing document
- Number of past notes analyzed
- Key highlights they should know
- Suggested talking points
- Location where briefing was saved
- Confirmation that PDF was synced to reMarkable
