from typing import List, Tuple
import os

def validate_file_type(filename: str, allowed_extensions: set) -> bool:
    """Validate file extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size"""
    return file_size <= max_size

def validate_batch_size(files: List, max_files: int) -> bool:
    """Validate number of files in batch"""
    return len(files) <= max_files

def validate_files(files: List, config) -> Tuple[bool, str]:
    """Validate all files against configuration"""
    if not files:
        return False, "No files uploaded"
        
    if not validate_batch_size(files, config.MAX_IMAGES):
        return False, f"Maximum {config.MAX_IMAGES} images allowed per batch"
        
    for file in files:
        if not validate_file_type(file.name, config.ALLOWED_EXTENSIONS):
            return False, f"Invalid file type: {file.name}"
            
        if not validate_file_size(file.size, config.MAX_FILE_SIZE):
            return False, f"File too large: {file.name}"
            
    return True, "" 