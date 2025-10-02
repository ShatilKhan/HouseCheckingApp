"""
File utilities for industrial inspection system.

This module provides file management functions including directory creation,
filename generation with non-overwrite logic, and file operations.
"""

import os
from typing import List


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path: Path to directory to create
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False


def get_next_filename(
    directory: str, 
    status: str, 
    order_number: str, 
    part_number: str, 
    counter: int, 
    cam_id: int
) -> str:
    """
    Generate a non‑overwriting filename as specified in requirements.
    
    Args:
        directory: Output directory path
        status: Status string ("OK" or "NOK")
        order_number: Production order number
        part_number: Part identification number
        counter: Counter value for this status
        cam_id: Camera ID
        
    Returns:
        Complete file path that doesn't exist yet
    """
    # Generate base filename according to specification
    base_name = f"{status}_{order_number}_{part_number}Count{counter}_CAM{cam_id}.jpg"
    full_path = os.path.join(directory, base_name)
    
    # If file doesn't exist, return it
    if not os.path.exists(full_path):
        return full_path
    
    # If file exists, add suffix to make it unique
    name_without_ext = os.path.splitext(base_name)[0]
    suffix = 1
    
    while True:
        new_name = f"{name_without_ext}_{suffix}.jpg"
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(new_path):
            return new_path
        
        suffix += 1


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, -1 if file doesn't exist or error occurred
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return -1


def delete_file(file_path: str) -> bool:
    """
    Safely delete a file.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if file was deleted successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def list_files_by_extension(directory: str, extension: str) -> list:
    """
    List all files with specific extension in directory.
    
    Args:
        directory: Directory to search in
        extension: File extension (e.g., '.jpg', '.csv')
        
    Returns:
        List of file paths with the specified extension
    """
    try:
        if not os.path.exists(directory):
            return []
        
        files = []
        for filename in os.listdir(directory):
            if filename.lower().endswith(extension.lower()):
                files.append(os.path.join(directory, filename))
        
        return sorted(files)
    except OSError as e:
        print(f"Error listing files in {directory}: {e}")
        return []


def clean_old_files(directory: str, max_files: int = 1000) -> int:
    """
    Clean old image files if directory contains too many files.
    
    Args:
        directory: Directory to clean
        max_files: Maximum number of files to keep
        
    Returns:
        Number of files deleted
    """
    try:
        # Get all image files sorted by modification time
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        all_files = []
        
        for ext in image_extensions:
            files = list_files_by_extension(directory, ext)
            all_files.extend(files)
        
        # Sort by modification time (oldest first)
        all_files.sort(key=lambda x: os.path.getmtime(x))
        
        # Delete oldest files if we exceed the limit
        deleted_count = 0
        while len(all_files) > max_files:
            oldest_file = all_files.pop(0)
            if delete_file(oldest_file):
                deleted_count += 1
        
        return deleted_count
        
    except Exception as e:
        print(f"Error cleaning old files in {directory}: {e}")
        return 0


def backup_csv_file(csv_path: str) -> str:
    """
    Create a backup copy of CSV file with timestamp.
    
    Args:
        csv_path: Path to CSV file to backup
        
    Returns:
        Path to backup file, empty string if backup failed
    """
    try:
        if not os.path.exists(csv_path):
            return ""
        
        # Generate backup filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = os.path.dirname(csv_path)
        filename = os.path.basename(csv_path)
        name, ext = os.path.splitext(filename)
        
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(directory, backup_filename)
        
        # Copy file
        import shutil
        shutil.copy2(csv_path, backup_path)
        
        return backup_path
        
    except Exception as e:
        print(f"Error creating backup of {csv_path}: {e}")
        return ""