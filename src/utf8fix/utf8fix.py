import os
import logging
import re
import unicodedata
from argparse import ArgumentParser

def clean_filename(filename: str, mode: str = 'preserve') -> str:
    # Replace null and control characters (only once)
    filename = re.sub(r'[\x00-\x1f]+', 'withNull', filename, count=1)
    
    if mode == 'ascii':
        # Normalize and remove diacritics
        filename = unicodedata.normalize('NFKD', filename)
        # Remove combining characters and keep only ASCII
        filename = ''.join(c for c in filename if not unicodedata.combining(c) and ord(c) < 128)
    
    return filename

def process_directory(directory, mode='preserve', dry_run=False):
    logger = logging.getLogger(__name__)
    
    if directory is None:
        raise TypeError("Directory cannot be None")
    if not directory:
        raise ValueError("Directory path cannot be empty")
    if not isinstance(directory, (str, os.PathLike)):
        raise TypeError("Directory must be a string or path-like object")
    if not os.path.exists(directory):
        raise ValueError(f"Directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise ValueError(f"Path is not a directory: {directory}")

    # First pass: Process directories bottom-up
    for root, dirs, _ in os.walk(directory, topdown=False):
        for name in dirs:
            try:
                new_name = clean_filename(name, mode)
                if name != new_name:
                    old_path = os.path.join(root, name)
                    new_path = os.path.join(root, new_name)
                    if dry_run:
                        logger.info(f"Would rename directory: {old_path} -> {new_path}")
                    else:
                        os.rename(old_path, new_path)
                        logger.info(f"Renamed directory: {old_path} -> {new_path}")
            except Exception as e:
                logger.error(f"Error processing directory {name}: {e}")

    # Second pass: Process files
    for root, _, files in os.walk(directory):
        for name in files:
            try:
                new_name = clean_filename(name, mode)
                if name != new_name:
                    old_path = os.path.join(root, name)
                    new_path = os.path.join(root, new_name)
                    if dry_run:
                        logger.info(f"Would rename file: {old_path} -> {new_path}")
                    else:
                        os.rename(old_path, new_path)
                        logger.info(f"Renamed file: {old_path} -> {new_path}")
            except Exception as e:
                logger.error(f"Error processing {name}: {e}")

def main():
    parser = ArgumentParser(description='Fix character encoding in file and directory names')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--mode', choices=['preserve', 'ascii'], default='preserve',
                      help='preserve: keep valid UTF-8, ascii: convert to ASCII only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--log-file', help='Path to the log file (if not specified, only console output is shown)')
    args = parser.parse_args()

    # Set up logging handlers
    handlers = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    process_directory(args.directory, args.mode, args.dry_run)
    logging.info("Processing completed.")

if __name__ == '__main__':
    main()
