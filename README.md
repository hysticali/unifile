# Unifile

A command-line utility for normalizing filenames by converting special characters (like umlauts) to their ASCII equivalents while preserving the original meaning.

## Features

- Converts special characters to their ASCII equivalents (e.g., "tést.txt" → "test.txt")
- Preserves original filenames if no conversion is needed
- Recursive directory processing
- Dry-run mode for previewing changes
- Detailed logging of operations
- Command-line interface with configurable options

## Installation

```bash
pip install unifile
```

## Usage

Basic usage:
```bash
unifile /path/to/directory
```

With options:
```bash
unifile /path/to/directory --mode ascii --dry-run --log-file unifile.log
```

### Command-line Options

- `--mode`: Choose the conversion mode
  - `ascii`: Convert special characters to ASCII equivalents (default)
  - `preserve`: Keep original characters
- `--dry-run`: Preview changes without making them
- `--log-file`: Specify a custom log file path
- `--help`: Show help message

## Examples

```bash
# Convert all files in current directory
unifile .

# Preview changes without making them
unifile /path/to/dir --dry-run

# Use custom log file
unifile /path/to/dir --log-file mylog.log
```

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run tests:
   ```bash
   pytest
   ```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
