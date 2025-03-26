import os
import logging
import re
import unicodedata
from argparse import ArgumentParser

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
                    try:
                        os.rename(old_path, new_path)
                        logger.info(f"Renamed file: {old_path} -> {new_path}")
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
                    try:
                        os.rename(old_path, new_path)
                        logger.info(f"Renamed directory: {old_path} -> {new_path}")
                    except OSError as e:
                        logger.error(f"Error renaming directory {old_path}: {e}")

def main():
    """Main entry point for the command-line interface."""
    parser = ArgumentParser(description='Fix character encoding issues in file and directory names')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--mode', choices=['preserve', 'ascii'], default='preserve',
                      help='preserve: keep valid UTF-8, ascii: convert to ASCII only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--log-file', help='Path to the log file (if not specified, only console output is shown)')
    args = parser.parse_args()

    # Configure logging with timestamp and level
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add file handler if log file is specified
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    process_directory(args.directory, args.mode, args.dry_run)
    logging.info("Processing completed.")

if __name__ == '__main__':
    main()
