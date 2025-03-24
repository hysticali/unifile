import os
import pytest
from pathlib import Path
from utf8fix.utf8fix import clean_filename, process_directory

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

def test_clean_filename_preserve():
    assert clean_filename("test.txt", mode='preserve') == "test.txt"
    assert clean_filename("tést.txt", mode='preserve') == "tést.txt"
    assert clean_filename("münchen.doc", mode='preserve') == "münchen.doc"
    assert clean_filename("file\x00with\x1fnull.txt", mode='preserve') == "filewithNull.txt"

def test_clean_filename_ascii():
    assert clean_filename("test.txt", mode='ascii') == "test.txt"
    assert clean_filename("tést.txt", mode='ascii') == "tst.txt"
    assert clean_filename("münchen.doc", mode='ascii') == "mnchen.doc"

def test_process_directory_preserve(temp_directory):
    process_directory(str(temp_directory), mode='preserve', dry_run=False)
    files = set(os.listdir(temp_directory))
    assert "tést.txt" in files
    assert "málaga.doc" in files
    assert "münchen" in files

def test_process_directory_ascii(temp_directory):
    process_directory(str(temp_directory), mode='ascii', dry_run=False)
    files = set(os.listdir(temp_directory))
    assert "tst.txt" in files
    assert "malaga.doc" in files
    assert "munchen" in files

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