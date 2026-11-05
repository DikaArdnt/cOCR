[English](README.md) | [Bahasa Indonesia](README_ID.md)

---

# cOCR Workbench

Desktop and command-line (CLI) application to extract text from document images (exam papers, worksheets, scanned books, presentation slides, and quiz screenshots) into Microsoft Word (.docx), PDF (.pdf), or Markdown (.md).

All processing runs locally on your machine using ONNX Runtime. Images and extracted text are never sent to external servers or cloud services.

---

## Table of Contents

1. [Choose Your Path](#choose-your-path)
2. [Desktop App Guide (Non-Developer)](#desktop-app-guide-non-developer)
   - [Opening the Application](#1-opening-the-application)
   - [Document Extraction Steps](#2-document-extraction-steps)
   - [Layout Mode Guide](#3-layout-mode-guide)
   - [Finding Output Files](#4-finding-output-files)
3. [Developer Guide: Installation and Running from Source](#developer-guide-installation-and-running-from-source)
   - [System Requirements](#system-requirements)
   - [Standard Installation (pip)](#option-a-standard-installation-pip)
   - [Fast Installation (uv)](#option-b-fast-installation-uv)
   - [Optional GPU Acceleration (CUDA and DirectML)](#optional-gpu-acceleration)
   - [Running the Developer GUI](#running-the-developer-gui)
4. [Command-Line Interface (CLI) Guide](#command-line-interface-cli-guide)
   - [Syntax and Command Examples](#syntax-and-command-examples)
   - [CLI Parameter Reference](#cli-parameter-reference)
   - [Automation and Batch Scripts](#automation-and-batch-scripts)
5. [Standalone Executable Compilation (Build)](#standalone-executable-compilation-build)
   - [Build Architecture Options](#build-architecture-options)
   - [Building on Windows](#1-building-on-windows)
   - [Building on Linux](#2-building-on-linux)
   - [Building on macOS](#3-building-on-macos)
   - [Building Linux Binaries from Windows with Docker](#4-building-linux-binaries-from-windows-with-docker)
   - [GitHub Actions Automated Releases](#5-github-actions-automated-releases)
6. [Advanced Configuration and Customization](#advanced-configuration-and-customization)
   - [Watermark Filtering (watermarks.json)](#watermark-filtering-watermarksjson)
   - [Server and Security Configuration (.env)](#server-and-security-configuration-env)
7. [OCR Processing and Cleaning Pipeline](#ocr-processing-and-cleaning-pipeline)
8. [Troubleshooting](#troubleshooting)
9. [Project Structure](#project-structure)
10. [License](#license)

---

## Choose Your Path

Select the workflow that matches how you plan to use cOCR:

- **Desktop Users**: No Python setup, terminal commands, or programming knowledge required. Download the pre-built application package or launch the `.bat` shortcut, then work through the visual desktop interface. Go to the [Desktop App Guide](#desktop-app-guide-non-developer).
- **Developers and Technical Users**: Run from source, automate tasks through the CLI, configure GPU acceleration with CUDA or DirectML, or compile standalone binaries. Go to the [Developer Guide](#developer-guide-installation-and-running-from-source).

---

## Desktop App Guide (Non-Developer)

Follow this guide to extract text from documents using the visual interface.

### 1. Opening the Application

Choose the method that matches your setup:

#### Option 1: Using the Standalone Release Package
1. Download the release archive (for example, `cOCR_Workbench_Windows_x64.zip`) from the project releases page.
2. Extract the archive into a folder on your computer (such as `D:\cOCR`).
3. Open the extracted folder and double-click `cOCR.exe` on Windows, `cOCR Workbench.app` on macOS, or `cOCR` on Linux.
4. The cOCR Workbench desktop window opens.

> [!NOTE]
> The pre-built macOS package (`cOCR Workbench.app`) is not yet available for download. The macOS build is still in the testing stage and needs testers. In the meantime, macOS users can run cOCR from source (see the [Developer Guide](#developer-guide-installation-and-running-from-source)).

#### Option 2: Using the Local Repository on Windows
If you already have a copy of this repository on Windows:
1. Open the project folder.
2. Double-click `run_gui.bat`.
3. The script sets up the local environment and opens the desktop interface.

> [!NOTE]
> On the first launch, the application downloads the RapidOCR ONNX character recognition models. This download happens once. After that, cOCR operates entirely offline.

---

### 2. Document Extraction Steps

Once cOCR Workbench opens, complete the extraction in five steps:

```
[1. Select Images/Folder] -> [2. Choose Layout Mode] -> [3. Select Format] -> [4. Start Extraction] -> [5. Download Results]
```

1. **Select Document Source**:
   - **Select Folder**: Use this option when your document images are organized in a single folder. Click **Pilih Folder** (Select Folder) and choose the directory.
   - **File Upload / Drag and Drop**: Drag image files directly into the gray drop zone, or click the box to browse for individual files. Supported formats include `.jpg`, `.jpeg`, `.png`, `.webp`, and `.bmp`.
2. **Choose Output Formats**:
   - Check one or more formats:
     - **Word (.docx)**: Best for editing, formatting, or adding notes in Microsoft Word or Google Docs.
     - **PDF (.pdf)**: Best for printing or sharing clean document layouts.
     - **Markdown (.md)**: Lightweight formatted text for note tools (Obsidian, Notion) or documentation.
3. **Select Layout Mode**:
   - Match the physical structure of your source images (see the mode table below). If you are unsure, keep the default **Deteksi Otomatis** (Auto Detect).
4. **Choose Compute Device**:
   - Select **CPU** for standard processing on any computer.
   - Select **GPU** if your machine has a supported graphics card and you need faster processing on large batches.
5. **Run Extraction and Save Outputs**:
   - Click the blue **Mulai Ekstraksi Dokumen** (Start Extraction) button.
   - Monitor the progress bar and per-image status indicators.
   - Once the bar reaches 100%, review the text in the **Pratinjau Hasil** (Preview Results) or **Markdown Mentah** (Raw Markdown) tabs.
   - Click the download buttons to save your Word, PDF, or Markdown files.

---

### 3. Layout Mode Guide

Choosing the right layout mode helps cOCR organize text to match original document hierarchies:

| Document Mode | App Label | When to Use |
| :--- | :--- | :--- |
| **`auto`** | Deteksi Otomatis | **Recommended default.** Best when your image collection has mixed formats or unknown layouts. The engine analyzes image structure automatically. |
| **`document_mcq`** | Naskah Ujian & Pilihan Ganda | **For school exams, standardized tests, and question banks.** Preserves question numbering (1, 2, 3...) and separates multiple-choice options (A, B, C, D, E) so options do not blend into question text. |
| **`worksheet`** | Lembar Kerja Berseksi | **For student worksheets, lab modules, and structured study guides.** Detects section markers (Part A, Part B), exercise instructions, and fill-in questions. |
| **`quiz`** | Tangkapan Layar Kuis Ponsel | **For vertical smartphone screenshots from educational or trivia apps.** Separates the top question card from answer choices below. |
| **`full`** | Dokumen Bebas & Teks Penuh | **For book pages, articles, scanned papers, letters, or presentation slides.** Orders text lines sequentially from top to bottom without parsing exam questions. |

---

### 4. Finding Output Files

Beyond the download buttons in the interface, generated files are written directly to your disk:

- **Folder Selection Mode**: Files are saved to an `output/` subfolder inside the source directory you selected (for example: `D:\Scans\output\hasil_ekstraksi_dokumen.docx`).
- **File Upload / Drag and Drop Mode**: Files are saved inside the `outputs/` folder next to the `cOCR.exe` binary or project root.

---

## Developer Guide: Installation and Running from Source

This section covers running cOCR Workbench directly from source using a local Python environment.

### System Requirements

- **Python**: 3.9, 3.10, 3.11, or 3.12 (Python 3.10 or 3.11 recommended).
- **Operating System**: Windows 10/11 (x64), Linux (Ubuntu, Debian, Fedora, Arch), or macOS (Intel and Apple Silicon).
- **Memory (RAM)**: 4 GB minimum (8 GB or higher recommended for high-resolution images).
- **Disk Space**: Roughly 500 MB for Python libraries and ONNX model weights.

---

### Option A: Standard Installation (pip)

1. Navigate to the project root in your terminal:
   ```bash
   cd e:\py\cocr
   ```

2. Create and activate an isolated virtual environment:
   ```bash
   # On Windows (Command Prompt or PowerShell)
   python -m venv .venv
   .venv\Scripts\activate

   # On Linux or macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

### Option B: Fast Installation (uv)

If you use `uv`:

1. Create the virtual environment and install dependencies:
   ```bash
   uv venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate # Linux/macOS
   uv pip install -r requirements.txt
   ```

2. Run the application directly:
   ```bash
   uv run python main.py
   ```

---

### Optional GPU Acceleration

By default, cOCR runs OCR inference across CPU threads. To accelerate processing for large image batches, install an execution provider package matching your hardware:

#### 1. NVIDIA Graphics Cards (CUDA)
For Windows or Linux with an NVIDIA GPU and current CUDA drivers:
```bash
pip install onnxruntime-gpu
# or with uv:
uv pip install onnxruntime-gpu
```

#### 2. Universal Windows Acceleration via DirectML (AMD Radeon, Intel Arc / Iris Xe, and NVIDIA)
For Windows users with AMD, Intel, or NVIDIA graphics hardware:
```bash
pip install onnxruntime-directml
# or with uv:
uv pip install onnxruntime-directml
```

> [!TIP]
> No code changes are required. When `-d gpu` is specified, cOCR checks for available GPU providers automatically. If no GPU provider is found, the engine falls back to CPU execution without crashing.

---

### Running the Developer GUI

Launch the Python desktop interface through any of these modes:

1. **Native Desktop Window (Default)**:
   Opens a standalone desktop window using WebKit or Edge WebView2 through `pywebview`:
   ```bash
   python main.py
   # or
   python main.py --gui
   ```

2. **External Web Browser**:
   Opens the interface in your default browser (Google Chrome, Microsoft Edge, or Mozilla Firefox) at `http://127.0.0.1:8765`:
   ```bash
   python main.py --browser
   ```

3. **Headless Server Mode**:
   Runs the web server without opening a desktop window (useful for containerized or local server deployments):
   ```bash
   python main.py --headless --host 0.0.0.0 --port 8765
   ```

---

## Command-Line Interface (CLI) Guide

CLI mode processes document batches directly without loading the graphical interface. This works well for scheduled jobs, directory watches, and automated pipelines.

### Syntax and Command Examples

Basic command syntax:
```bash
python main.py --cli -i <IMAGE_FOLDER> [OPTIONS]
```

Practical examples:

#### Example 1: Extract a Folder to All Formats (Markdown, Word, PDF) Using Auto Detection
Scans images in `samples/` and exports files to `output/`:
```bash
python main.py --cli -i samples -o output -f all -m auto
```

#### Example 2: Extract an Exam Folder to Word (.docx) Using Multiple-Choice Mode
Processes numbered exam questions and writes a `.docx` file:
```bash
python main.py --cli -i "D:\Exams\Math_Test" -f docx -m document_mcq
```

#### Example 3: Extract Book Pages or Scanned Notes to Markdown (.md)
Converts long document scans into clean Markdown text:
```bash
python main.py --cli -i "D:\Scans\Book_Chapter1" -f md -m full
```

#### Example 4: Extract Mobile Quiz Screenshots with GPU Acceleration
Runs batch extraction on vertical quiz images using your graphics card:
```bash
python main.py --cli -i "D:\Quiz_Screenshots" -f all -d gpu -m quiz
```

#### Example 5: Run the CLI from a Compiled Binary (cOCR.exe)
Execute the CLI without a Python runtime:
```powershell
.\cOCR.exe --cli -i "C:\Users\Username\Documents\Scans" -f docx -m auto
```

---

### CLI Parameter Reference

| Parameter | Short Flag | Values | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--input-dir` | `-i` | Directory path | *(Required)* | Directory containing document images (`.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`). |
| `--output-dir` | `-o` | Directory path | `<input-dir>/output` | Destination directory for exported files. Created automatically if missing. |
| `--format` | `-f` | `md`, `docx`, `pdf`, `all` | `all` | Output file format. Use `all` to produce all three formats in one run. |
| `--device` | `-d` | `cpu`, `gpu` | `cpu` | Computation device used for OCR inference. |
| `--mode` | `-m` | `auto`, `quiz`, `document_mcq`, `worksheet`, `full` | `auto` | Document layout segmentation strategy. |
| `--cli` | | Flag | | Enforces terminal execution without launching a server or UI window. |
| `--gui` | | Flag | | Launches the desktop interface (used when `-i` is omitted). |
| `--browser` | | Flag | | Opens the web interface in the default external browser. |
| `--headless` | | Flag | | Runs the web server in the background without opening a window. |
| `--host` | | IP Address | `127.0.0.1` | Host address for the web server. |
| `--port` | | Port Number | `8765` | Network port for the web server. |

---

### Automation and Batch Scripts

When running via CLI, the terminal prints real-time extraction progress:

```text
cOCR Workbench
Device : CPU Multi-threading
Format : Markdown (.md), Word (.docx), PDF (.pdf)

Initializing OCR engine (CPU)...
Engine ready on device: CPU
Found 12 image files to process.
Segmentation Mode : auto
Output Directory  : D:\Documents\output

[========================] 100% | Processing complete.

Extraction finished in 8.45 seconds.
- Total files scanned : 12
- Unique files parsed : 12
- Duplicate files skip: 0

Generated output files:
  -> D:\Documents\output\hasil_ekstraksi_dokumen.md (14.2 KB)
  -> D:\Documents\output\hasil_ekstraksi_dokumen.docx (28.7 KB)
  -> D:\Documents\output\hasil_ekstraksi_dokumen.pdf (45.1 KB)

Done.
```

You can call this command inside a Windows batch script (`.bat`), PowerShell script (`.ps1`), or Linux bash script to automate recurring tasks.

---

## Standalone Executable Compilation (Build)

The repository includes PyInstaller build tooling to compile Python source code into standalone binaries that run on machines without Python installed.

### Build Architecture Options

The build script supports two distribution models:

1. **`--mode onedir` (Recommended)**:
   - Produces a single distribution directory named `cOCR_Workbench/` containing the executable and shared libraries.
   - Starts quickly because files do not need to be unpacked to a temporary folder on each run.
2. **`--mode onefile`**:
   - Produces a single executable binary (for example, `cOCR.exe`).
   - Unpacks dependencies to `%TEMP%` on each launch before opening the window.

---

### 1. Building on Windows

Install build dependencies:
```powershell
pip install pyinstaller pywebview
```

Run either build option:

- **Via batch file**: Double-click **`build.bat`** in the project root.
- **Via command line**:
  ```powershell
  python build_exe.py --mode onedir
  ```

Optional arguments:
- `--clean`: Removes previous `build/` and `dist/` folders before compilation.
- `--console`: Keeps the command console visible behind the application window (helpful when reading debug logs).

The compiled output is placed in **`dist/cOCR_Workbench/`** with the main executable **`cOCR.exe`**.

---

### 2. Building on Linux (Ubuntu / Debian / Linux Mint / Fedora)

On Linux, the embedded desktop window requires WebKitGTK system libraries.

1. Install WebKitGTK packages:
   ```bash
   # Debian, Ubuntu, or Linux Mint:
   sudo apt-get update
   sudo apt-get install -y libwebkit2gtk-4.1-dev gir1.2-webkit2-4.1

   # Fedora or Red Hat Enterprise Linux:
   sudo dnf install webkit2gtk4.1-devel
   ```

2. Run the build script:
   ```bash
   chmod +x build.sh
   ./build.sh --mode onedir
   ```

The compiled binary is written to **`dist/cOCR_Workbench/cOCR`**.

---

### 3. Building on macOS (Apple Silicon and Intel)

> [!WARNING]
> The macOS build is **not yet available** on the releases page because it is still in the testing stage. We are looking for macOS testers (Intel and Apple Silicon). If you can help, build from source using the steps below and report any issues you encounter.

macOS includes the Cocoa WebKit engine natively:

1. Run the build script:
   ```bash
   chmod +x build.sh
   ./build.sh --mode onedir
   ```

2. The output produces the application bundle **`dist/cOCR Workbench.app`**, which can be moved directly into `/Applications`.

---

### 4. Building Linux Binaries from Windows with Docker

If you work on Windows and need Linux binaries without setting up a virtual machine, use the included Docker configuration:

```powershell
docker build -t cocr-linux-builder -f build_tools/Dockerfile.build .
docker run --rm -v ${PWD}/dist_linux:/output cocr-linux-builder
```

Compiled Linux binaries are placed in `dist_linux/`.

---

### 5. GitHub Actions Automated Releases

Continuous delivery automation is configured in [`.github/workflows/build.yml`](.github/workflows/build.yml).

Pushing a version tag to GitHub triggers the build pipeline:
```bash
git tag v1.2.0
git push origin v1.2.0
```

GitHub Actions will:
1. Build binaries on Windows x64 and Linux x64. The macOS targets (ARM64/Apple Silicon and Intel) are temporarily disabled while the macOS build is in testing — see [Building on macOS](#3-building-on-macos).
2. Archive outputs into `.zip` and `.tar.gz` packages.
3. Attach binary release assets directly to GitHub Releases.

---

## Advanced Configuration and Customization

### Watermark Filtering (watermarks.json)

Scanned exams and worksheets often contain promotional headers, diagonal watermarks, website URLs, or contact numbers that clutter extracted text.

cOCR Workbench filters matching text using regular expressions defined in **`watermarks.json`**.

Setup steps:
1. Copy `watermarks.example.json` to `watermarks.json`:
   ```bash
   cp watermarks.example.json watermarks.json
   ```
2. Add keywords or regular expression patterns to match:
   ```json
   [
     "tutoring_center_xyz",
     "private_collection",
     "\\.com",
     "\\.id",
     "whatsapp",
     "all rights reserved",
     "^page\\s+\\d+"
   ]
   ```
3. Save the file. Lines matching these patterns are removed from the exported documents.

> [!NOTE]
> `watermarks.json` is listed in `.gitignore` so your local filtering patterns are not committed to public repositories.

---

### Server and Security Configuration (.env)

Configure runtime settings through `.env` (a template is available in `.env.example`). This is useful when hosting cOCR on a local network for schools, offices, or labs:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `COCR_HOST` | `127.0.0.1` | Server bind address. Set to `0.0.0.0` to permit connections from other local network machines. |
| `COCR_PORT` | `8765` | Network port for the web interface. |
| `COCR_ALLOWED_ORIGINS` | `http://localhost:8765,...` | Allowed CORS origins for API requests. |
| `COCR_CLOUD_MODE` | `0` | When set to `1` or `true`, enables server sandbox mode. Disables server-side directory picking so clients can only process files uploaded within their session. |
| `COCR_API_KEY` | *(Empty)* | Authentication key. When set, client requests must supply an `X-API-Key` or `Authorization: Bearer <key>` header. |

Active security controls:
- **Session Isolation**: Uploaded files and generated documents are separated into session sandboxes (`temp_uploads/<session_id>` and `outputs/<session_id>`).
- **Path Traversal Protection**: Rejects attempts to access sensitive system paths (such as `C:\Windows`, `/etc`, or `.ssh` keys).
- **Upload Constraints**: Enforces limits of 100 MB per batch, 8192x8192 pixel dimensions, and 25 megapixels per image to protect against memory exhaustion.
- **Security Headers**: Transmits standard HTTP headers including `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, and `X-Frame-Options: DENY`.

---

## OCR Processing and Cleaning Pipeline

cOCR Workbench processes extracted text through a sequential cleaning pipeline:

1. **Angled Watermark Filtering**: Ignores bounding boxes with contour angles exceeding 16 degrees, preventing diagonal stamps from inserting fragments into question text.
2. **Mobile Screen Element Removal**: Crops out phone status bars (battery, cellular signal, clock), bottom navigation bars, and mobile quiz pagination counters.
3. **Grouped Reading Order Sorting**: Sorts text blocks top to bottom and merges inline words horizontally using an adaptive character-height threshold.
4. **Automatic Page Number Detection**: Detects page markers (such as `Page 12 of 40` or `12/40`) to maintain document order even when image filenames are unordered.
5. **Checksum Deduplication**: Generates MD5 hashes to detect and skip duplicate images within an upload batch.
6. **Document Format Sanitization**: Escapes XML and HTML reserved characters (`<`, `>`, `&`) to avoid parsing errors during ReportLab PDF and DOCX generation.

---

## Troubleshooting

### 1. Windows SmartScreen displays a warning when opening `cOCR.exe`
- **Cause**: The binary was compiled locally and does not carry a commercial code signing certificate.
- **Solution**: Click **More info** on the Windows SmartScreen dialog, then click **Run anyway**. The binary runs locally without external network dependencies.

### 2. Port 8765 is already in use by another application
- **Solution**: cOCR checks port availability automatically. If port 8765 is occupied, the application tries successive ports (8766, 8767, etc.). To set an explicit port, pass the `--port <number>` parameter.

### 3. GPU acceleration is not detected on systems with NVIDIA hardware
- **Solution**: Verify that `onnxruntime-gpu` is installed in your Python environment and that GPU drivers are up to date. If GPU packages are missing, the engine continues processing on the CPU.

### 4. The desktop window does not appear on Linux when running `python main.py`
- **Solution**: Confirm WebKitGTK packages are installed (`sudo apt-get install libwebkit2gtk-4.1-dev gir1.2-webkit2-4.1`). You can also run cOCR in your browser with `python main.py --browser`.

### 5. Exam question text or answer options appear out of order
- **Solution**: If `auto` mode misorders answer choices in exam scans, switch the layout mode to **`document_mcq`** (Naskah Ujian & Pilihan Ganda). This mode applies dedicated sorting rules for numbered question headers and answer options (A, B, C, D, E).

---

## Project Structure

```
cocr/
├── assets/                       # Icon and logo assets (.ico and .png)
│   ├── cocr.ico                  # Application icon (Windows ICO format)
│   └── cocr.png                  # Application icon (PNG format)
│
├── src/                          # Core source package
│   └── cocr/
│       ├── __init__.py           # Package initialization
│       ├── engine.py             # OCR engine, layout segmentation, and text cleaning
│       ├── server.py             # FastAPI server and pywebview window controller
│       ├── cli.py                # Command-line interface parser
│       ├── i18n.py               # Centralized CLI internationalization dictionaries & helper
│       └── exporters.py          # Document generators (Markdown, DOCX, and PDF)
│
├── web/                          # Desktop frontend assets
│   ├── index.html                # Application layout
│   ├── style.css                 # Interface styling
│   ├── app.js                    # UI logic and progress polling
│   ├── i18n.js                   # Lightweight internationalization engine
│   └── locales/                  # Multi-language dictionary files
│       ├── en.js                 # English localization strings
│       ├── id.js                 # Indonesian localization strings
│       └── README.md             # Localization guide & i18n instructions
│
├── build_tools/                  # Packaging and compilation utilities
│   ├── build_exe.py              # Multi-platform PyInstaller builder
│   ├── cocr.spec                 # PyInstaller spec configuration
│   └── Dockerfile.build          # Docker container for building Linux binaries from Windows
│
├── scripts/                      # Utility scripts
│   └── scan_and_extract.py       # Local extraction testing script
│
├── samples/                      # Sample document images for testing
├── .github/                      # CI/CD automation
│   └── workflows/
│       └── build.yml             # GitHub Actions multi-platform release workflow
│
├── main.py                       # Main application entry point (CLI and GUI)
├── run_gui.bat                   # Quick GUI launcher shortcut for Windows
├── build.bat                     # Standalone build shortcut for Windows
├── build.sh                      # Standalone build shortcut for Linux and macOS
├── build_exe.py                  # Build runner shortcut in project root
├── requirements.txt              # Python library dependencies
├── watermarks.example.json       # Example watermark filter configuration
├── .env.example                  # Example environment variable template
├── LICENSE                       # Project license
├── README.md                     # Default documentation (English)
└── README_ID.md                  # Indonesian documentation
```

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

Copyright © 2026 Dika Ardianta
Copyright © 2026 Hisoka Labs

You are free to use, study, modify, and redistribute this software, provided that derivative works are also distributed under the same license. See the [LICENSE](LICENSE) file for the full license text.
