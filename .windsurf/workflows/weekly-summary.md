---
description: Generate a weekly summary from Obsidian notes
---

# Weekly Summary Workflow

This workflow generates a comprehensive weekly summary of your notes, meetings, and activities from your Obsidian vault.

## Step 1: Read the Weekly Summary Prompt

Read the system prompt that defines how to generate weekly summaries:

@/Users/nicklaslarson/code/brain.ai/prompts/weekly_summary.md

## Step 2: Search Obsidian Vault for This Week's Notes

Use the Obsidian MCP to search for notes from the current week. Look for:
- Meeting notes from this week
- Project updates
- Action items
- Key decisions
- People interactions

Search query: Look for notes with dates in the current week (use today's date to determine the week range).

## Step 3: Analyze and Categorize Content

Review all notes found and categorize them according to the prompt structure:
- **Key Meetings & Decisions**
- **Project Progress**
- **Action Items & Follow-ups**
- **People & Relationships**
- **Insights & Learnings**

## Step 4: Generate the Weekly Summary

Using the weekly summary prompt as your guide, generate a comprehensive summary that:
- Highlights the most important meetings and decisions
- Tracks progress on active projects
- Lists outstanding action items
- Notes key people interactions
- Captures insights and learnings

Format the output as a clean Markdown document with proper sections and bullet points.

## Step 5: Save the Summary

Save the generated summary to your Obsidian vault:
- Location: `Summaries/Weekly/YYYY-WW-Weekly-Summary.md`
- Include YAML frontmatter with date range and tags
- Add backlinks to referenced notes and people

## Step 6: Confirm Completion

Report to the user:
- Number of notes analyzed
- Key highlights from the week
- Location of the saved summary
- Any action items that need attention
