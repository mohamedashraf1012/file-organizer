import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

# File categories mapping
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Code": [
        ".py", ".js", ".ts", ".html", ".css",
        ".java", ".cpp", ".c", ".json", ".xml", ".yaml", ".yml",
    ],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Others": [],
}


def setup_logger(log_dir: str = "logs") -> logging.Logger:
    """Setup logger with file and console handlers."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "organizer.log")

    logger = logging.getLogger("FileOrganizer")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def get_category(file_extension: str) -> str:
    """Return the category name for a given file extension."""
    ext = file_extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def scan_folder(folder_path: str) -> list[dict]:
    """
    Scan a folder and return a list of file info dicts.
    Each dict has: name, extension, category, full_path, size_bytes
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    files = []
    for entry in os.scandir(folder_path):
        if entry.is_file():
            ext = Path(entry.name).suffix
            files.append({
                "name": entry.name,
                "extension": ext,
                "category": get_category(ext),
                "full_path": entry.path,
                "size_bytes": entry.stat().st_size,
            })

    return files


def organize_files(folder_path: str, dry_run: bool = False) -> dict:
    """
    Organize files in folder_path into category subfolders.
    If dry_run=True, only simulate without moving files.
    Returns a summary dict.
    """
    logger = setup_logger()
    files = scan_folder(folder_path)

    summary = {
        "total": len(files),
        "moved": 0,
        "skipped": 0,
        "errors": 0,
        "details": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    for file_info in files:
        category = file_info["category"]
        dest_dir = os.path.join(folder_path, category)
        dest_path = os.path.join(dest_dir, file_info["name"])

        try:
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
                if file_info["full_path"] != dest_path:
                    shutil.move(file_info["full_path"], dest_path)

            summary["moved"] += 1
            summary["details"].append({
                "file": file_info["name"],
                "category": category,
                "status": "moved" if not dry_run else "simulated",
            })
            prefix = "[DRY RUN] " if dry_run else ""
            logger.info(f"{prefix}Moved: {file_info['name']} → {category}/")

        except Exception as e:
            summary["errors"] += 1
            summary["details"].append({
                "file": file_info["name"],
                "category": category,
                "status": f"error: {str(e)}",
            })
            logger.error(f"Error moving {file_info['name']}: {e}")

    logger.info(
        f"Done! Total: {summary['total']} | "
        f"Moved: {summary['moved']} | Errors: {summary['errors']}"
    )
    return summary


def get_folder_stats(folder_path: str) -> dict:
    """Return stats about files in a folder before organizing."""
    files = scan_folder(folder_path)
    stats = {}
    for f in files:
        cat = f["category"]
        stats[cat] = stats.get(cat, 0) + 1
    return stats
