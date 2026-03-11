#!/usr/bin/env python3
"""
Process Microsoft Teams meeting transcripts into structured Obsidian notes.

Usage:
    # From file
    python scripts/process_transcript.py inbox/teams-meeting.txt
    
    # From stdin (for piping)
    cat transcript.txt | python scripts/process_transcript.py
    
    # Interactive mode (paste and press Ctrl+D)
    python scripts/process_transcript.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import re

def read_input(file_path=None):
    """Read transcript from file or stdin."""
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), file_path
    else:
        # Read from stdin
        return sys.stdin.read(), None

def extract_metadata(transcript):
    """Extract basic metadata from transcript."""
    metadata = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'title': 'Meeting Notes',
        'attendees': []
    }
    
    # Try to extract date from common formats
    date_patterns = [
        r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        r'(\d{4}-\d{2}-\d{2})',       # YYYY-MM-DD
        r'(\w+ \d{1,2}, \d{4})'       # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, transcript[:500])
        if match:
            date_str = match.group(1)
            # Try to parse and convert to YYYY-MM-DD
            try:
                if '/' in date_str:
                    dt = datetime.strptime(date_str, '%m/%d/%Y')
                elif '-' in date_str:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    dt = datetime.strptime(date_str, '%B %d, %Y')
                metadata['date'] = dt.strftime('%Y-%m-%d')
                break
            except:
                pass
    
    # Extract speaker names (simple pattern matching)
    speaker_pattern = r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s+\([^)]+\))?):?'
    speakers = set()
    for line in transcript.split('\n'):
        match = re.match(speaker_pattern, line.strip())
        if match:
            name = match.group(1)
            # Remove (Guest) or similar annotations
            name = re.sub(r'\s*\([^)]+\)', '', name)
            speakers.add(name)
    
    metadata['attendees'] = sorted(list(speakers))
    
    # Try to extract title from first few lines
    lines = transcript.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) > 10 and len(line) < 100:
            # Likely a title if it's not a speaker line
            if not re.match(speaker_pattern, line) and ':' not in line:
                metadata['title'] = line
                break
    
    return metadata

def main():
    """Main processing function."""
    # Determine input source
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
    
    # Read transcript
    transcript, source_file = read_input(file_path)
    
    if not transcript.strip():
        print("Error: No transcript content provided", file=sys.stderr)
        sys.exit(1)
    
    # Extract basic metadata
    metadata = extract_metadata(transcript)
    
    # Output information for Claude Code to process
    print("=" * 80)
    print("TRANSCRIPT PROCESSING REQUEST")
    print("=" * 80)
    print(f"\nSource: {source_file if source_file else 'stdin'}")
    print(f"Detected Date: {metadata['date']}")
    print(f"Detected Title: {metadata['title']}")
    print(f"Detected Attendees: {', '.join(metadata['attendees']) if metadata['attendees'] else 'None'}")
    print(f"\nTranscript Length: {len(transcript)} characters")
    print(f"Lines: {len(transcript.split(chr(10)))}")
    print("\n" + "=" * 80)
    print("TRANSCRIPT CONTENT")
    print("=" * 80)
    print(transcript)
    print("\n" + "=" * 80)
    print("\nPlease process this transcript using the transcript_structure.md prompt.")
    print("Apply person name verification and file to the Obsidian vault.")
    
    if source_file:
        print(f"\nAfter processing, move source file to: inbox/processed/")

if __name__ == "__main__":
    main()
