# Starfield Voice & Core Files Copier

A lightweight, standalone Python utility to easily copy localized voice files (`.ba2`) and core game files (`.esm`) for **Starfield**.

This tool is a Python/PySide6 reimplementation of the original Inno Setup script, designed to be faster, cross-platform, and highly portable.

## Features

- **GUI Interface**: Simple and intuitive interface built with PySide6 (Qt).
- **Multi-Language Support**: Supports English, German, French, Italian, Spanish, Polish, Portuguese, Japanese, Korean, and Chinese.
- **Smart Filtering**: Automatically detects and copies only the `.ba2` voice files matching the selected language and all `.esm` files.
- **Progress Tracking**: Real-time progress bar and log output.
- **Lightweight EXE**: Optimized PyInstaller build (under 50 MB).

## How to Use (End User)

1. Download the latest `StarfieldVoiceCopier.exe` from the **Releases** tab.
2. Run the `.exe` (no Python installation required).
3. Select your desired **Language** from the dropdown.
4. Choose the **Source Data Folder** (where your downloaded/localized voice files are located).
5. Choose the **Destination Data Folder** (usually your Starfield installation path, e.g., `...\Starfield\Data`).
6. Click **Copy** and wait for the progress bar to finish.

## How to Build from Source

### Prerequisites
- Python 3.10 (recommended)
- Anaconda or a Python virtual environment (`.venv`)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Sonic1SVK/Starfield-BA2-Manager-Compressor-Cross-Platform-.git
   cd Starfield-BA2-Manager-Compressor-Cross-Platform-
2.Install dependencies:
    pip install PySide6 pyinstaller
3.  Build the executable (using the optimized spec file):
   pyinstaller --noconfirm StarfieldVoiceCopier.spec
4. Find your executable in the dist/ folder.
UPX Compression (Optional)
To achieve the smallest possible file size (around 45 MB), ensure UPX is installed on your system and accessible in your system's PATH. The .spec file is already configured to use it.

Credits
Original Inno Setup logic by Sonic1SVK

Python/PySide6 implementation and optimization by [Sonic1SVK/GitHub Handle]
