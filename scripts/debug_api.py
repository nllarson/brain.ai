#!/usr/bin/env python3
"""Debug script to inspect reMarkable USB API response."""

import json
import requests

host = "http://10.11.99.1"
url = f"{host}/documents/"

try:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    
    documents = resp.json()
    
    # Build folder map
    folders = {doc["ID"]: doc["VisibleName"] for doc in documents if doc["Type"] == "CollectionType"}
    
    print("=== Folders ===")
    for folder_id, folder_name in folders.items():
        print(f"  {folder_name} (ID: {folder_id})")
    
    print("\n=== Notebooks ===")
    for doc in documents:
        if doc["Type"] == "DocumentType":
            parent_id = doc.get("Parent", "")
            if parent_id:
                folder_name = folders.get(parent_id, f"Unknown ({parent_id})")
                print(f"  {doc['VisibleName']} → in folder: {folder_name}")
            else:
                print(f"  {doc['VisibleName']} → (root level)")
    
    print("\n=== Full Raw Response ===")
    print(json.dumps(documents, indent=2))
    
except requests.exceptions.JSONDecodeError:
    print("API returned HTML, not JSON")
    print("\n=== HTML Response (first 1000 chars) ===")
    print(resp.text[:1000])
    
except requests.RequestException as e:
    print(f"Error: {e}")
