#!/usr/bin/env python3
"""
rm_ingest.py — reMarkable USB Ingestion Script

Connects to the reMarkable tablet's USB web interface, discovers notebooks,
and downloads new/changed ones as PDFs into the inbox folder.
"""

import fnmatch
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def resolve_path(path_str: str) -> Path:
    """Resolve ~ and relative paths against the project root."""
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = Path(__file__).parent.parent / path
    return path


def load_state(state_path: Path) -> dict:
    """Load the download state file tracking previously ingested notebooks."""
    if state_path.exists():
        with open(state_path, "r") as f:
            return json.load(f)
    return {"notebooks": {}, "last_run": None}


def save_state(state_path: Path, state: dict):
    """Persist the download state."""
    state["last_run"] = datetime.now().isoformat()
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def matches_pattern(name: str, patterns: list[str]) -> bool:
    """Check if a name matches any of the given wildcard patterns (case-insensitive)."""
    if not patterns:
        return False
    name_lower = name.lower()
    for pattern in patterns:
        if fnmatch.fnmatch(name_lower, pattern.lower()):
            return True
    return False


def should_download_notebook(doc_name: str, folder_name: str, config: dict) -> bool:
    """
    Determine if a notebook should be downloaded based on include/exclude patterns.
    
    Patterns can match either:
    - Notebook name: "Meeting*"
    - Folder name: "Sales", "Sales/*" (folder and contents)
    - Full path: "Sales/Aruba"
    
    Logic:
    - If include_patterns is empty, download all (unless excluded)
    - If include_patterns is set, only download if name/folder matches at least one pattern
    - If exclude_patterns is set, skip if name/folder matches any exclude pattern
    """
    rm_config = config.get("remarkable", {})
    include_patterns = rm_config.get("include_patterns", [])
    exclude_patterns = rm_config.get("exclude_patterns", [])
    
    # Build possible match strings
    match_strings = [doc_name]  # Just the notebook name
    if folder_name:
        match_strings.append(folder_name)  # Just the folder name
        match_strings.append(f"{folder_name}/{doc_name}")  # Full path
    
    # Check exclude first (takes precedence)
    if exclude_patterns:
        for match_str in match_strings:
            if matches_pattern(match_str, exclude_patterns):
                return False
    
    # If no include patterns, download everything (that wasn't excluded)
    if not include_patterns:
        return True
    
    # Otherwise, must match at least one include pattern
    for match_str in match_strings:
        if matches_pattern(match_str, include_patterns):
            return True
    
    return False


def check_remarkable_connection(host: str) -> bool:
    """Check if the reMarkable is reachable via USB."""
    try:
        resp = requests.get(host, timeout=3)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def list_documents(host: str) -> tuple[list[dict], dict[str, str]]:
    """
    Fetch all documents from the reMarkable USB web interface, including nested folders.

    Returns:
        - List of all documents (notebooks only, not folders)
        - Folder map: {folder_id: folder_name}
    """
    url = f"{host}/documents/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        top_level = resp.json()
    except requests.exceptions.JSONDecodeError:
        print("[WARN] Could not parse JSON from /documents/, trying HTML fallback...")
        top_level = parse_document_list_html(host, resp.text)
    except requests.RequestException as e:
        print(f"[ERROR] Failed to list documents: {e}")
        return [], {}
    
    # Build folder map and recursively fetch folder contents
    folders = {}
    all_documents = []
    
    for item in top_level:
        if item["Type"] == "CollectionType":
            folder_id = item["ID"]
            folder_name = item.get("VisibleName", item.get("VissibleName", ""))
            folders[folder_id] = folder_name
            
            # Fetch documents inside this folder
            folder_url = f"{host}/documents/{folder_id}"
            try:
                folder_resp = requests.get(folder_url, timeout=10)
                folder_resp.raise_for_status()
                folder_contents = folder_resp.json()
                
                # Add documents from this folder
                for doc in folder_contents:
                    if doc["Type"] == "DocumentType":
                        all_documents.append(doc)
            except requests.RequestException as e:
                print(f"[WARN] Failed to fetch folder '{folder_name}': {e}")
        
        elif item["Type"] == "DocumentType":
            # Root-level document
            all_documents.append(item)
    
    return all_documents, folders


def parse_document_list_html(host: str, html: str) -> list[dict]:
    """
    Fallback parser for the reMarkable USB web interface HTML.

    The web UI at http://10.11.99.1 serves an HTML page with document entries.
    Each document has a download link and metadata.
    """
    documents = []
    # The reMarkable web UI renders documents as list items with data attributes
    # This is a simple parser — if the format changes, this may need updating
    import re

    # Look for document entries in the HTML
    # Pattern: links to download endpoints like /download/<id>/placeholder
    links = re.findall(r'href=["\'](/download/[^"\']+)["\']', html)
    names = re.findall(r'<div[^>]*class="name"[^>]*>([^<]+)</div>', html)

    for i, link in enumerate(links):
        doc_id = link.split("/")[2] if len(link.split("/")) > 2 else f"unknown_{i}"
        name = names[i].strip() if i < len(names) else f"Notebook_{i}"
        documents.append({
            "ID": doc_id,
            "VissibleName": name,  # reMarkable's actual spelling
            "ModifiedClient": "",
            "download_url": f"{host}{link}",
        })

    return documents


def download_document(host: str, doc: dict, inbox_path: Path) -> Path | None:
    """
    Download a document as PDF from the reMarkable USB web interface.

    Returns the path to the downloaded file, or None on failure.
    """
    doc_id = doc.get("ID", "unknown")
    doc_name = doc.get("VissibleName", doc.get("VisibleName", f"notebook_{doc_id}"))

    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in doc_name)
    safe_name = safe_name.strip()

    # Build download URL
    if "download_url" in doc:
        download_url = doc["download_url"]
    else:
        download_url = f"{host}/download/{doc_id}/placeholder"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.pdf"
    output_path = inbox_path / filename

    try:
        print(f"  Downloading: {doc_name} → {filename}")
        resp = requests.get(download_url, timeout=60, stream=True)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = output_path.stat().st_size
        print(f"  ✓ Saved ({file_size / 1024:.1f} KB)")
        return output_path

    except requests.RequestException as e:
        print(f"  ✗ Failed to download {doc_name}: {e}")
        if output_path.exists():
            output_path.unlink()
        return None


def ingest(config: dict) -> list[Path]:
    """
    Main ingestion routine.

    Returns a list of paths to newly downloaded PDFs.
    """
    rm_config = config["remarkable"]
    host = rm_config["host"]
    state_path = resolve_path(rm_config["state_file"])
    inbox_path = resolve_path(config["inbox_path"])

    # Ensure inbox exists
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Check connection
    print(f"Connecting to reMarkable at {host}...")
    if not check_remarkable_connection(host):
        print("✗ reMarkable not reachable. Is it connected via USB?")
        print("  Make sure USB is plugged in and the web interface is enabled:")
        print("  Settings → Storage → USB web interface → ON")
        return []

    print("✓ reMarkable connected")

    # Load state
    state = load_state(state_path)
    known_notebooks = state.get("notebooks", {})

    # List documents and build folder map
    documents, folders = list_documents(host)
    if not documents:
        print("No documents found on reMarkable.")
        return []

    print(f"Found {len(documents)} document(s) on reMarkable")

    # Find new or modified documents
    new_docs = []
    filtered_count = 0
    for doc in documents:
        doc_id = doc.get("ID", "")
        doc_name = doc.get("VissibleName", doc.get("VisibleName", ""))
        modified = doc.get("ModifiedClient", "")
        parent_id = doc.get("Parent", "")
        
        # Resolve folder name
        folder_name = folders.get(parent_id, "") if parent_id else ""
        
        # Check if this document should be downloaded based on patterns
        if not should_download_notebook(doc_name, folder_name, config):
            filtered_count += 1
            continue

        if doc_id not in known_notebooks:
            new_docs.append(doc)
        elif known_notebooks[doc_id].get("modified") != modified and modified:
            new_docs.append(doc)
    
    if filtered_count > 0:
        print(f"Filtered out {filtered_count} document(s) based on folder/name patterns")

    if not new_docs:
        print("No new or modified documents to download.")
        save_state(state_path, state)
        return []

    print(f"Downloading {len(new_docs)} new/modified document(s)...")

    # Download each new document
    downloaded = []
    for doc in new_docs:
        result = download_document(host, doc, inbox_path)
        if result:
            downloaded.append(result)
            # Update state
            doc_id = doc.get("ID", "")
            parent_id = doc.get("Parent", "")
            folder_name = folders.get(parent_id, "") if parent_id else ""
            
            known_notebooks[doc_id] = {
                "name": doc.get("VissibleName", doc.get("VisibleName", "")),
                "folder": folder_name,
                "modified": doc.get("ModifiedClient", ""),
                "downloaded_at": datetime.now().isoformat(),
                "local_path": str(result),
            }

    state["notebooks"] = known_notebooks
    save_state(state_path, state)

    print(f"\n✓ Done — {len(downloaded)} file(s) downloaded to {inbox_path}")
    return downloaded


def main():
    """Entry point."""
    config = load_config()

    print("=" * 50)
    print("brain.ai — reMarkable Ingestion")
    print("=" * 50)
    print()

    downloaded = ingest(config)

    if downloaded:
        print(f"\nNew files ready for processing:")
        for path in downloaded:
            print(f"  • {path.name}")

    return 0 if downloaded is not None else 1


if __name__ == "__main__":
    sys.exit(main())
