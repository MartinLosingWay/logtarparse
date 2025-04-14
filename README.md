# File Explorer with Tar.gz Support

A Python Qt application that allows you to:
- Browse and select directories
- View file structure in a tree view
- Read file contents into memory
- Handle tar.gz archives and read their contents

## Features
- Modern Qt6 interface
- Directory tree view with file sizes and types
- Memory usage tracking
- Support for regular files and tar.gz archives
- Error handling for permissions and file access

## Requirements
- Python 3.6 or higher
- PyQt6
- tarfile (included in Python standard library)

## Installation
1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the application:
```bash
python file_explorer.py
```
2. Click "Select Directory" to choose a directory to explore
3. Double-click on files to read their contents into memory
4. Double-click on tar.gz files to extract and read their contents
5. Monitor memory usage at the bottom of the window

## Notes
- The application keeps track of total memory usage
- File contents are stored in memory until the application is closed
- Large files may consume significant memory 