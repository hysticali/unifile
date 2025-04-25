import os
import sys
import pytest
import logging
from pathlib import Path
from io import StringIO
from unifile import clean_filename, process_directory, main

@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files with various encodings
    files = {
        "normal.txt": "normal.txt",
        "tést.txt": "tést.txt",
        "málaga.doc": "málaga.doc",
        "münchen": "münchen",  # directory
    }
    
    base_dir = tmp_path / "test_files"
    base_dir.mkdir()
    (base_dir / "münchen").mkdir()
    
    for name in files:
        if not name == "münchen":
            (base_dir / name).write_text("test content")
            
    return base_dir

@pytest.fixture
def setup_logging():
    """Set up logging for tests."""
    # Create a string buffer to capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    
    # Get the root logger and add our handler
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    yield log_stream
    
    # Clean up
    root_logger.removeHandler(handler)
    log_stream.close()

def test_clean_filename_preserve():
    assert clean_filename("test.txt", mode='preserve') == "test.txt"
    assert clean_filename("tést.txt", mode='preserve') == "tést.txt"
    assert clean_filename("münchen.doc", mode='preserve') == "münchen.doc"
    assert clean_filename("file\x00with\x1fnull.txt", mode='preserve') == "filewithNull.txt"

def test_clean_filename_ascii():
    assert clean_filename("test.txt", mode='ascii') == "test.txt"
    assert clean_filename("tést.txt", mode='ascii') == "test.txt"
    assert clean_filename("münchen.doc", mode='ascii') == "muenchen.doc"
    assert clean_filename("über.txt", mode='ascii') == "ueber.txt"
    assert clean_filename("München.txt", mode='ascii') == "Muenchen.txt"
    assert clean_filename("Über.txt", mode='ascii') == "Ueber.txt"

def test_process_directory_preserve(temp_directory):
    process_directory(str(temp_directory), mode='preserve', dry_run=False)
    files = set(os.listdir(temp_directory))
    assert "tést.txt" in files
    assert "málaga.doc" in files
    assert "münchen" in files

def test_process_directory_ascii(temp_directory):
    process_directory(str(temp_directory), mode='ascii', dry_run=False)
    files = set(os.listdir(temp_directory))
    assert "test.txt" in files
    assert "malaga.doc" in files
    assert "muenchen" in files

def test_process_directory_dry_run(temp_directory):
    original_files = set(os.listdir(temp_directory))
    process_directory(str(temp_directory), mode='ascii', dry_run=True)
    after_files = set(os.listdir(temp_directory))
    assert original_files == after_files

def test_invalid_directory():
    with pytest.raises(ValueError):
        process_directory("non_existent_dir")
    with pytest.raises(ValueError):
        process_directory("")
    with pytest.raises(TypeError):
        process_directory(None)

def test_permission_error(temp_directory):
    # Skip on Windows as permissions work differently
    if os.name != 'nt':
        os.chmod(temp_directory, 0o000)
        with pytest.raises(PermissionError):
            process_directory(str(temp_directory))
        os.chmod(temp_directory, 0o755)

def test_error_handling():
    with pytest.raises(Exception):
        clean_filename(None)

def test_clean_filename_edge_cases():
    # Empty string
    assert clean_filename("", mode='preserve') == ""
    assert clean_filename("", mode='ascii') == ""
    
    # Very long filename
    long_name = "a" * 255
    assert len(clean_filename(long_name, mode='preserve')) <= 255
    
    # Special characters
    assert clean_filename("file with spaces.txt", mode='preserve') == "file with spaces.txt"
    assert clean_filename("file.with.dots.txt", mode='preserve') == "file.with.dots.txt"
    assert clean_filename("file-with-dashes.txt", mode='preserve') == "file-with-dashes.txt"
    
    # Unicode normalization edge cases
    # These characters should normalize to the same result
    assert clean_filename("café", mode='ascii') == clean_filename("café", mode='ascii')
    assert clean_filename("über", mode='ascii') == clean_filename("über", mode='ascii')
    
    # Mixed case and special characters
    assert clean_filename("File-Name_123.txt", mode='preserve') == "File-Name_123.txt"
    
    # Multiple control characters
    assert clean_filename("file\x00with\x1fmultiple\x1econtrols.txt", mode='preserve') == "filewithNull.txt"

def test_clean_filename_unicode_normalization():
    # Test various Unicode normalization cases
    test_cases = [
        ("café", "cafe"),  # Basic accent
        ("über", "ueber"),  # Umlaut
        ("naïve", "naive"),  # Multiple special characters
        ("résumé", "resume"),  # Multiple accents
        ("übermensch", "uebermensch"),  # Mixed case with special characters
        ("München", "Muenchen"),  # Capitalized umlaut
        ("Äpfel", "Aepfel"),  # Another umlaut case
        ("Österreich", "Oesterreich"),  # Another umlaut case
        ("ß", "ss"),  # Special case
        ("ẞ", "Ss"),  # Capitalized special case
    ]
    
    for original, expected in test_cases:
        assert clean_filename(original, mode='ascii') == expected

def test_clean_filename_invalid_inputs():
    # Test invalid inputs
    with pytest.raises(TypeError):
        clean_filename(None, mode='preserve')
    
    with pytest.raises(TypeError):
        clean_filename(123, mode='preserve')  # Non-string input
    
    with pytest.raises(ValueError):
        clean_filename("test.txt", mode='invalid_mode')  # Invalid mode

def test_main_cli(tmp_path, setup_logging):
    """Test the main CLI functionality."""
    # Create a test file
    test_dir = tmp_path / "test_cli"
    test_dir.mkdir()
    test_file = test_dir / "tést.txt"
    test_file.write_text("test content")
    
    # Test with ASCII mode
    old_argv = sys.argv
    try:
        sys.argv = ["unifile", str(test_dir), "--mode", "ascii"]
        main()
        log_output = setup_logging.getvalue()
        assert "Processing completed" in log_output
        assert not test_file.exists()  # Original file should be renamed
        assert (test_dir / "test.txt").exists()  # New file should exist
    finally:
        sys.argv = old_argv

def test_main_cli_with_options(tmp_path, setup_logging):
    """Test the main CLI with various options."""
    # Create a test file
    test_dir = tmp_path / "test_cli_options"
    test_dir.mkdir()
    test_file = test_dir / "tést.txt"
    test_file.write_text("test content")
    
    # Test with ASCII mode and dry-run
    log_file = tmp_path / "test.log"
    old_argv = sys.argv
    try:
        sys.argv = ["unifile", str(test_dir), "--mode", "ascii", "--dry-run", "--log-file", str(log_file)]
        main()
        # Check that the file wasn't actually renamed (dry-run)
        assert test_file.exists()
        assert not (test_dir / "test.txt").exists()
        # Check log output
        log_output = setup_logging.getvalue()
        assert "Would rename file" in log_output
    finally:
        sys.argv = old_argv

def test_logging_configuration(tmp_path, setup_logging):
    """Test logging configuration."""
    log_file = tmp_path / "unifile.log"
    
    # Create a test directory with a file to rename
    test_dir = tmp_path / "test_logging"
    test_dir.mkdir()
    test_file = test_dir / "tést.txt"
    test_file.write_text("test")
    
    old_argv = sys.argv
    try:
        sys.argv = ["unifile", str(test_dir), "--mode", "ascii", "--log-file", str(log_file)]
        main()
        
        # Check log output
        log_output = setup_logging.getvalue()
        assert "Processing completed" in log_output
        
        # Check that the file was renamed
        assert not test_file.exists()
        assert (test_dir / "test.txt").exists()
        
        # Check log file contents
        assert log_file.exists()
        log_content = log_file.read_text()
        assert "Processing completed" in log_content
    finally:
        sys.argv = old_argv