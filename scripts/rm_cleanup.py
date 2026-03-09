#!/usr/bin/env python3
"""
Clean up processed PDFs and temporary images from the inbox.
Logs deletions to .cleanup-log for audit trail.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import yaml


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_directory_size(path: Path) -> int:
    """Calculate total size of directory in bytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except (OSError, PermissionError):
        pass
    return total


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def cleanup_directory(path: Path, pattern: str = "*", dry_run: bool = False) -> tuple[int, int]:
    """
    Clean up files or directories matching pattern.
    
    Returns:
        Tuple of (item_count, total_bytes_deleted)
    """
    if not path.exists():
        print(f"[SKIP] Directory does not exist: {path}")
        return 0, 0
    
    items = list(path.glob(pattern))
    if not items:
        print(f"[SKIP] No items to delete in: {path}")
        return 0, 0
    
    total_size = 0
    count = 0
    
    for item in items:
        if item.is_file():
            size = item.stat().st_size
        elif item.is_dir():
            size = get_directory_size(item)
        else:
            continue
        
        total_size += size
        count += 1
        
        if dry_run:
            print(f"[DRY-RUN] Would delete: {item.name} ({format_size(size)})")
        else:
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                print(f"[DELETED] {item.name} ({format_size(size)})")
            except (OSError, PermissionError) as e:
                print(f"[ERROR] Failed to delete {item.name}: {e}")
                count -= 1
                total_size -= size
    
    return count, total_size


def log_cleanup(processed_count: int, processed_size: int, 
                temp_count: int, temp_size: int, dry_run: bool = False):
    """Append cleanup summary to .cleanup-log."""
    if dry_run:
        return
    
    log_path = Path(__file__).parent.parent / ".cleanup-log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_path, "a") as f:
        if processed_count > 0:
            f.write(f"{timestamp} | Deleted {processed_count} PDFs from inbox/processed/ ({format_size(processed_size)})\n")
        if temp_count > 0:
            f.write(f"{timestamp} | Deleted {temp_count} image directories from temp/pdf_images/ ({format_size(temp_size)})\n")
        
        total_items = processed_count + temp_count
        total_size = processed_size + temp_size
        if total_items > 0:
            f.write(f"{timestamp} | Total: {total_items} items, {format_size(total_size)} freed\n")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up processed PDFs and temporary images from inbox"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    base_path = Path(__file__).parent.parent
    
    # Get paths
    processed_path = base_path / config.get("processed_path", "./inbox/processed")
    temp_images_path = base_path / "temp" / "pdf_images"
    
    print("=" * 60)
    if args.dry_run:
        print("DRY RUN MODE - No files will be deleted")
    else:
        print("CLEANUP MODE - Deleting files")
    print("=" * 60)
    print()
    
    # Clean up processed PDFs
    print(f"Cleaning up: {processed_path}")
    processed_count, processed_size = cleanup_directory(
        processed_path, 
        "*.pdf", 
        dry_run=args.dry_run
    )
    print()
    
    # Clean up temp images
    print(f"Cleaning up: {temp_images_path}")
    temp_count, temp_size = cleanup_directory(
        temp_images_path,
        "*",
        dry_run=args.dry_run
    )
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed PDFs: {processed_count} files, {format_size(processed_size)}")
    print(f"Temp images: {temp_count} directories, {format_size(temp_size)}")
    print(f"Total: {processed_count + temp_count} items, {format_size(processed_size + temp_size)} freed")
    
    if args.dry_run:
        print("\n[DRY-RUN] No files were actually deleted")
        print("Run without --dry-run to perform cleanup")
    else:
        # Log the cleanup
        log_cleanup(processed_count, processed_size, temp_count, temp_size)
        print(f"\n[LOGGED] Cleanup logged to .cleanup-log")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
