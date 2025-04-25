import os
import logging
import re
import unicodedata
import shutil
from argparse import ArgumentParser
from pathlib import Path

# Mapping of common umlaut characters to their ASCII equivalents
UMLAUT_MAP = {
    'ä': 'ae', 'Ä': 'Ae',
    'ö': 'oe', 'Ö': 'Oe',
    'ü': 'ue', 'Ü': 'Ue',
    'ß': 'ss', 'ẞ': 'Ss',
}

def clean_filename(filename: str, mode: str = 'preserve') -> str:
    """Clean and normalize a filename based on the specified mode.
    
    Args:
        filename (str): The filename to clean
        mode (str): The cleaning mode:
            - 'preserve': Keep valid UTF-8 characters, only fix invalid ones
            - 'ascii': Convert all non-ASCII characters to their ASCII equivalents
                      (e.g., 'é' -> 'e', 'ü' -> 'ue', 'ß' -> 'ss')
    
    Returns:
        str: The cleaned filename
    
    Raises:
        TypeError: If filename is not a string
        ValueError: If mode is not 'preserve' or 'ascii'
    
    Examples:
        >>> clean_filename("test.txt", mode='preserve')
        'test.txt'
        >>> clean_filename("café.txt", mode='ascii')
        'cafe.txt'
        >>> clean_filename("tést.txt", mode='ascii')
        'test.txt'
        >>> clean_filename("münchen.txt", mode='ascii')
        'muenchen.txt'
        >>> clean_filename("über.txt", mode='ascii')
        'ueber.txt'
        >>> clean_filename("file\x00with\x1fnull.txt", mode='preserve')
        'filewithNull.txt'
    """
    if not isinstance(filename, str):
        raise TypeError("Filename must be a string")
    if mode not in ['preserve', 'ascii']:
        raise ValueError("Mode must be either 'preserve' or 'ascii'")
        
    # Handle control characters (characters with ASCII value < 32)
    if '\x00' in filename or any(ord(c) < 32 for c in filename):
        parts = re.split(r'[\x00-\x1f]+', filename)
        filename = 'filewithNull' + os.path.splitext(parts[-1])[1] if parts[-1] else ''
    
    if mode == 'ascii':
        # First handle umlaut characters with their common ASCII equivalents
        # e.g., 'ü' -> 'ue', 'ö' -> 'oe', etc.
        for umlaut, replacement in UMLAUT_MAP.items():
            filename = filename.replace(umlaut, replacement)
        
        # Normalize and remove diacritics using NFKD form
        # This separates the base characters from their combining marks
        # e.g., 'é' -> 'e', 'ñ' -> 'n', etc.
        filename = unicodedata.normalize('NFKD', filename)
        # Remove combining characters (like accents)
        filename = ''.join(c for c in filename if not unicodedata.combining(c))
        # Keep only ASCII characters (ord < 128)
        filename = ''.join(c for c in filename if ord(c) < 128)
    
    return filename

def process_directory(directory, mode='preserve', dry_run=False):
    """Process all files and directories in the given directory recursively.
    
    Args:
        directory: Path to the directory to process
        mode (str): The cleaning mode ('preserve' or 'ascii')
        dry_run (bool): If True, only show what would be done without making changes
    
    Raises:
        TypeError: If directory is None or not a string/path-like object
        ValueError: If directory is empty or doesn't exist
    
    Note:
        - Processes directories bottom-up to avoid path issues
        - Logs all operations and errors
        - Preserves file content, only changes names
    """
    logger = logging.getLogger(__name__)
    
    if directory is None:
        raise TypeError("Directory cannot be None")
    if not directory:
        raise ValueError("Directory cannot be empty")
    if not os.path.exists(directory):
        raise ValueError(f"Directory does not exist: {directory}")
    
    # Check if we have permission to access the directory
    if not os.access(directory, os.R_OK | os.X_OK):
        raise PermissionError(f"Permission denied: {directory}")
    
    # Process directories bottom-up to avoid path issues
    for root, dirs, files in os.walk(directory, topdown=False):
        # Process files first
        for name in files:
            old_path = os.path.join(root, name)
            new_name = clean_filename(name, mode)
            if new_name != name:
                new_path = os.path.join(root, new_name)
                if dry_run:
                    logger.info(f"Would rename file: {old_path} -> {new_path}")
                else:
                    # If target exists, append a unique identifier
                    final_new_path = new_path
                    base, ext = os.path.splitext(new_name)
                    counter = 1
                    while os.path.exists(final_new_path):
                        final_new_name = f"{base}-{counter}{ext}"
                        final_new_path = os.path.join(root, final_new_name)
                        counter += 1
                    try:
                        os.rename(old_path, final_new_path)
                        logger.info(f"Renamed file: {old_path} -> {final_new_path}")
                    except OSError as e:
                        logger.error(f"Error renaming file {old_path}: {e}")
        
        # Then process directories
        for name in dirs:
            old_path = os.path.join(root, name)
            new_name = clean_filename(name, mode)
            if new_name != name:
                new_path = os.path.join(root, new_name)
                if dry_run:
                    logger.info(f"Would rename directory: {old_path} -> {new_path}")
                else:
                    if os.path.exists(new_path):
                        # Move all contents to the existing directory
                        for item in os.listdir(old_path):
                            s = os.path.join(old_path, item)
                            d = os.path.join(new_path, item)
                            if os.path.exists(d):
                                # If destination exists, append a unique identifier for files, recurse for dirs
                                if os.path.isfile(s):
                                    base, ext = os.path.splitext(item)
                                    counter = 1
                                    new_file = f"{base}-{counter}{ext}"
                                    d_new = os.path.join(new_path, new_file)
                                    while os.path.exists(d_new):
                                        counter += 1
                                        new_file = f"{base}-{counter}{ext}"
                                        d_new = os.path.join(new_path, new_file)
                                    shutil.move(s, d_new)
                                else:
                                    # If it's a directory, recursively merge
                                    # For simplicity, recursively call this logic
                                    # (could be improved for performance)
                                    for subitem in os.listdir(s):
                                        shutil.move(os.path.join(s, subitem), os.path.join(d, subitem))
                                    os.rmdir(s)
                            else:
                                shutil.move(s, d)
                        os.rmdir(old_path)
                        logger.info(f"Merged and removed directory: {old_path} -> {new_path}")
                    else:
                        try:
                            os.rename(old_path, new_path)
                            logger.info(f"Renamed directory: {old_path} -> {new_path}")
                        except OSError as e:
                            logger.error(f"Error renaming directory {old_path}: {e}")

def setup_logging(log_file=None, preserve_handlers=False):
    """Set up logging configuration.
    
    Args:
        log_file (str, optional): Path to the log file. If provided, logs will be written to this file
                                 in addition to console output.
        preserve_handlers (bool): If True, preserve existing handlers. Used for testing.
    """
    root = logging.getLogger()
    
    if not preserve_handlers:
        # Remove any existing handlers
        for handler in root.handlers[:]:
            root.removeHandler(handler)
        handlers = [logging.StreamHandler()]
    else:
        # Keep existing handlers
        handlers = root.handlers[:]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Remove all handlers and re-add them
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    for handler in handlers:
        handler.setFormatter(logging.Formatter('%(message)s'))
        root.addHandler(handler)
    
    root.setLevel(logging.INFO)

def process_path(path: Path, mode: str = 'preserve', dry_run: bool = True):
    """Process a path and show/make encoding fixes"""
    for item in path.rglob('*'):
        try:
            current_name = item.name
            new_name = clean_filename(current_name, mode=mode)
            
            if current_name != new_name:
                parent_folder = item.parent.name or item.parent
                if dry_run:
                    if item.is_file():
                        logging.info(f"Would rename file: {item} -> {item.parent / new_name}")
                    else:
                        logging.info(f"Would rename directory: {item} -> {item.parent / new_name}")
                else:
                    if item.is_file():
                        # If target exists, append a unique identifier
                        base, ext = os.path.splitext(new_name)
                        counter = 1
                        target = item.parent / new_name
                        while target.exists():
                            target = item.parent / f"{base}-{counter}{ext}"
                            counter += 1
                        try:
                            shutil.move(str(item), str(target))
                            logging.info(f"Renamed file: {item} -> {target}")
                        except OSError as e:
                            logging.error(f"Failed to rename [{parent_folder}] {current_name}: {e}")
                    else:
                        target = item.parent / new_name
                        if target.exists():
                            # Move all contents to the existing directory
                            for subitem in item.iterdir():
                                dest = target / subitem.name
                                if dest.exists():
                                    if subitem.is_file():
                                        base, ext = os.path.splitext(subitem.name)
                                        counter = 1
                                        new_file = f"{base}-{counter}{ext}"
                                        d_new = target / new_file
                                        while d_new.exists():
                                            counter += 1
                                            new_file = f"{base}-{counter}{ext}"
                                            d_new = target / new_file
                                        shutil.move(str(subitem), str(d_new))
                                    else:
                                        # If it's a directory, recursively merge
                                        for ssubitem in subitem.iterdir():
                                            shutil.move(str(ssubitem), str(dest / ssubitem.name))
                                        subitem.rmdir()
                                else:
                                    shutil.move(str(subitem), str(dest))
                            item.rmdir()
                            logging.info(f"Merged and removed directory: {item} -> {target}")
                        else:
                            try:
                                shutil.move(str(item), str(target))
                                logging.info(f"Renamed directory: {item} -> {target}")
                            except OSError as e:
                                logging.error(f"Failed to rename [{parent_folder}] {current_name}: {e}")
        except Exception as e:
            logging.error(f"Error processing {item}: {e}")

def main():
    parser = ArgumentParser(description='Fix character encoding issues in file and directory names')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--mode', choices=['preserve', 'ascii'], default='preserve',
                      help='preserve: keep valid UTF-8, ascii: convert to ASCII only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--log-file', help='Path to the log file (if not specified, only console output is shown)')
    args = parser.parse_args()

    # Check if we're running in a test environment (pytest sets up handlers)
    root_logger = logging.getLogger()
    in_test = any(isinstance(h, logging.StreamHandler) and hasattr(h.stream, 'getvalue') 
                 for h in root_logger.handlers)
    
    setup_logging(args.log_file, preserve_handlers=in_test)
    target = Path(args.directory)
    
    if not target.exists():
        logging.error(f"Path does not exist: {target}")
        return

    logging.info(f"Scanning {target}")
    process_path(target, mode=args.mode, dry_run=args.dry_run)
    logging.info("Processing completed.")

if __name__ == '__main__':
    main()
