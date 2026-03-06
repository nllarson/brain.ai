#!/usr/bin/env python3
"""
find_similar_people.py — Helper to find similar person names in Obsidian vault

Used during OCR workflow to detect potential duplicate person entries.
"""

import sys
from pathlib import Path
from difflib import SequenceMatcher


def similarity_ratio(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings (0.0 to 1.0)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_existing_people(vault_path: Path) -> list[str]:
    """Get list of all existing person names from vault."""
    people_dir = vault_path / "People"
    if not people_dir.exists():
        return []
    
    people = []
    for person_file in people_dir.glob("*.md"):
        # Remove .md extension to get person name
        people.append(person_file.stem)
    
    return sorted(people)


def find_similar(name: str, existing_people: list[str], threshold: float = 0.6) -> list[tuple[str, float]]:
    """
    Find similar names from existing people.
    
    Returns list of (name, similarity_score) tuples sorted by score descending.
    """
    similar = []
    
    for existing in existing_people:
        score = similarity_ratio(name, existing)
        if score >= threshold:
            similar.append((existing, score))
    
    # Sort by similarity score descending
    similar.sort(key=lambda x: x[1], reverse=True)
    
    return similar


def check_exact_match(name: str, existing_people: list[str]) -> str | None:
    """Check for exact match (case-insensitive). Returns matched name or None."""
    name_lower = name.lower()
    for existing in existing_people:
        if existing.lower() == name_lower:
            return existing
    return None


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 2:
        print("Usage: python3 find_similar_people.py <name>")
        print("Example: python3 find_similar_people.py 'Matt'")
        sys.exit(1)
    
    name = sys.argv[1]
    vault_path = Path.home() / "Documents" / "Obsidian" / "brain.ai-vault"
    
    existing_people = get_existing_people(vault_path)
    
    # Check for exact match
    exact = check_exact_match(name, existing_people)
    if exact:
        print(f"✓ Exact match found: {exact}")
        return
    
    # Find similar names
    similar = find_similar(name, existing_people, threshold=0.5)
    
    if similar:
        print(f"? '{name}' - Similar to:")
        for i, (similar_name, score) in enumerate(similar[:5], 1):
            print(f"  {i}. {similar_name} (similarity: {score:.2f})")
        print(f"  {len(similar[:5]) + 1}. Keep as '{name}' (new person)")
    else:
        print(f"? '{name}' - NEW person (no similar names found)")


if __name__ == "__main__":
    main()
