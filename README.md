# UTF-8 Filename Fixer

A Python utility to fix character encoding issues in file and directory names.

## Features

- Fix invalid UTF-8 characters in filenames
- Option to convert to ASCII-only names
- Dry-run mode to preview changes
- Optional logging to file
- Recursive directory processing
- Safe handling of control characters
- Intelligent handling of diacritics and special characters
- Proper handling of umlaut characters (ä, ö, ü, ß)

## Installation

```bash
# Install from source
pip install .

# Install with test dependencies
pip install ".[test]"
```

## Usage

```bash
# Using pip-installed version
utf8fix directory [--mode {preserve,ascii}] [--dry-run] [--log-file LOG_FILE]

# Using the script directly
python -m utf8fix directory [--mode {preserve,ascii}] [--dry-run] [--log-file LOG_FILE]
```

### Arguments

- `directory`: Directory to process (required)
- `--mode`: Choose mode for handling special characters:
  - `preserve` (default): Keep valid UTF-8 characters, only fix invalid ones
  - `ascii`: Convert all non-ASCII characters to their ASCII equivalents
- `--dry-run`: Preview changes without making them
- `--log-file`: Optional log file path for detailed operation logging

### Examples

```bash
# Preview changes
utf8fix ./my_files --dry-run

# Fix names preserving valid UTF-8
utf8fix ./my_files

# Convert to ASCII-only with logging
utf8fix ./my_files --mode ascii --log-file changes.log
```

## Behavior

### Preserve Mode
- Keeps valid UTF-8 characters intact
- Replaces control characters with "withNull"
- Maintains original filename structure

Example transformations:
```
"tést.txt" → "tést.txt"
"münchen.doc" → "münchen.doc"
"file\x00with\x1fnull.txt" → "filewithNull.txt"
```

### ASCII Mode
- Converts accented characters to their ASCII equivalents
- Removes non-ASCII characters
- Maintains readability and original meaning

Common transformations:
```
# Basic accents
"tést.txt" → "test.txt"
"café.txt" → "cafe.txt"
"résumé.pdf" → "resume.pdf"

# Umlaut characters
"münchen.doc" → "muenchen.doc"
"über.txt" → "ueber.txt"
"Österreich.txt" → "Oesterreich.txt"

# Special characters
"ä" → "ae"
"ö" → "oe"
"ü" → "ue"
"ß" → "ss"
"Ä" → "Ae"
"Ö" → "Oe"
"Ü" → "Ue"
"ẞ" → "Ss"
```

### Safety Features
- Dry-run mode for previewing changes
- Bottom-up directory processing to avoid path issues
- Comprehensive error handling and logging
- File extension preservation
- Original file content remains unchanged
- Consistent handling of special characters

## Development

### Running Tests
```bash
# Install test dependencies
pip install ".[test]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=utf8fix
```

## Disclaimer

This is a utility script provided as-is without any warranties. Always use the `--dry-run` option first to preview changes, and ensure you have backups of important files before running the utility.

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
