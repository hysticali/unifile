# UTF-8 Filename Fixer

A Python utility to fix character encoding issues in file and directory names.

## Features

- Fix invalid UTF-8 characters in filenames
- Option to convert to ASCII-only names
- Dry-run mode to preview changes
- Optional logging to file

## Usage

```bash
# Using pip-installed version
utf8fix directory [--mode {preserve,ascii}] [--dry-run] [--log-file LOG_FILE]

# Using the script directly
python -m utf8fix directory [--mode {preserve,ascii}] [--dry-run] [--log-file LOG_FILE]
```

### Arguments

- `directory`: Directory to process
- `--mode`: Choose 'preserve' to keep valid UTF-8 or 'ascii' for ASCII-only names
- `--dry-run`: Preview changes without making them
- `--log-file`: Optional log file path

### Examples

```bash
# Preview changes
python utf8fix.py ./my_files --dry-run

# Fix names preserving valid UTF-8
python utf8fix.py ./my_files

# Convert to ASCII-only with logging
python utf8fix.py ./my_files --mode ascii --log-file changes.log
```

## Disclaimer

This is a utility script provided as-is without any warranties. Use at your own risk.

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
