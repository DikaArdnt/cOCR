# cOCR Workbench
#
# Copyright (C) 2026 Dika Ardianta
# Copyright (C) 2026 Hisoka Labs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# See LICENSE for details.

import os
import sys
from typing import Any, Dict

CLI_MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "app_desc": "cOCR Workbench: Batch visual document extraction to Markdown, DOCX, and PDF (GUI & CLI).",
        "app_desc_cli": "cOCR Workbench: Batch visual document extraction to Markdown, DOCX, and PDF.",
        "lang": "CLI language for messages and help text (default: en).",
        "input_dir": "Path to folder containing document images (.jpeg, .png, .jpg, .webp, .bmp).",
        "output_dir": "Output directory path (default: <input-dir>/output).",
        "format": "Export format: md, docx, pdf, or all (default: all).",
        "device": "Compute device: cpu or gpu (default: cpu).",
        "mode": "Layout mode: auto, quiz (dual-card mobile), document_mcq (multiple-choice), worksheet, full.",
        "cli": "Run in Command Line Interface (CLI) mode without opening GUI.",
        "gui": "Launch native desktop GUI application (default).",
        "browser": "Open GUI in external default web browser instead of native window.",
        "headless": "Run GUI backend server without opening a window or browser.",
        "host": "Host address for GUI web server (default: 127.0.0.1 or COCR_HOST).",
        "port": "Port for GUI web server (default: 8765 or COCR_PORT).",
        "err_input_required": "Error: -i/--input-dir argument is required in CLI mode.",
        "err_input_not_found": "Error: Input directory '{path}' does not exist.",
        "warn_no_images": "Warning: No supported image files found in '{path}'.",
        "supported_extensions": "Supported extensions: .jpg, .jpeg, .png, .webp, .bmp",
        "device_banner": "Device    : {device}",
        "formats_banner": "Formats   : Markdown (.md), Word (.docx), PDF (.pdf)\n",
        "init_engine": "Initializing OCR engine ({device})...",
        "engine_ready": "Engine ready using: {device}",
        "found_files": "Found {count} image file(s) to process.",
        "segmentation_mode": "Segmentation Mode: {mode}",
        "output_directory": "Output Directory : {path}\n",
        "completed": "Extraction completed in {time:.2f} seconds.",
        "scanned_files": "- Total files scanned   : {count}",
        "unique_files": "- Unique files processed: {count}",
        "duplicate_files": "- Duplicate files skipped: {count}",
        "generated_files": "\nGenerated output files:",
        "done": "\nDone.",
    },
    "id": {
        "app_desc": "cOCR Workbench: Ekstraksi batch dokumen visual ke Markdown, DOCX, dan PDF (GUI & CLI).",
        "app_desc_cli": "cOCR Workbench: Ekstraksi batch dokumen visual ke Markdown, DOCX, dan PDF.",
        "lang": "Bahasa tampilan antarmuka CLI dan bantuan (default: id).",
        "input_dir": "Path folder berisi gambar dokumen (.jpeg, .png, .jpg, .webp, .bmp).",
        "output_dir": "Path folder penyimpanan hasil (default: <input-dir>/output).",
        "format": "Pilihan format keluaran: md, docx, pdf, atau all (default: all).",
        "device": "Pilihan komputasi: cpu atau gpu (default: cpu).",
        "mode": "Mode tata letak: auto (otomatis), quiz (2 kartu ponsel), document_mcq (naskah pilihan ganda), worksheet (lembar kerja), full (dokumen penuh).",
        "cli": "Jalankan mode Command Line Interface (CLI) tanpa membuka antarmuka GUI.",
        "gui": "Jalankan antarmuka GUI desktop native (default).",
        "browser": "Buka antarmuka GUI di peramban web eksternal alih-alih jendela desktop bawaan.",
        "headless": "Jalankan server GUI di latar belakang tanpa membuka jendela maupun peramban.",
        "host": "Host address untuk server web GUI (default: 127.0.0.1 atau dari COCR_HOST).",
        "port": "Port untuk server web GUI (default: 8765 atau dari COCR_PORT).",
        "err_input_required": "Kesalahan: Mode CLI memerlukan argumen -i / --input-dir.",
        "err_input_not_found": "Kesalahan: Direktori masukan '{path}' tidak ditemukan.",
        "warn_no_images": "Peringatan: Tidak ada berkas gambar yang ditemukan di '{path}'.",
        "supported_extensions": "Ekstensi yang didukung: .jpg, .jpeg, .png, .webp, .bmp",
        "device_banner": "Perangkat : {device}",
        "formats_banner": "Format    : Markdown (.md), Word (.docx), PDF (.pdf)\n",
        "init_engine": "Memulai inisialisasi mesin OCR ({device})...",
        "engine_ready": "Mesin siap berjalan menggunakan: {device}",
        "found_files": "Ditemukan {count} berkas gambar untuk diproses.",
        "segmentation_mode": "Mode Segmentasi : {mode}",
        "output_directory": "Direktori Output: {path}\n",
        "completed": "Ekstraksi selesai dalam {time:.2f} detik.",
        "scanned_files": "- Total berkas dipindai : {count}",
        "unique_files": "- Berkas unik diproses  : {count}",
        "duplicate_files": "- Berkas duplikat lewati: {count}",
        "generated_files": "\nBerkas keluaran berhasil dibuat:",
        "done": "\nSelesai.",
    },
}


def detect_cli_lang() -> str:
    """Detect language preference from CLI arguments or environment variables."""
    raw_args = sys.argv[1:]
    for idx, arg in enumerate(raw_args):
        if arg in ("--lang", "-l") and idx + 1 < len(raw_args):
            val = raw_args[idx + 1].strip().lower()
            if val in ("id", "in", "indonesia", "indonesian"):
                return "id"
            if val in ("en", "eng", "english"):
                return "en"
        elif arg.startswith("--lang="):
            val = arg.split("=", 1)[1].strip().lower()
            if val in ("id", "in", "indonesia", "indonesian"):
                return "id"
            if val in ("en", "eng", "english"):
                return "en"

    env_lang = (os.environ.get("COCR_LANG") or os.environ.get("LANG") or "").lower()
    if env_lang.startswith("id"):
        return "id"
    return "en"


def get_cli_strings(lang: str = "en") -> Dict[str, str]:
    """Return dictionary of localized CLI strings with English fallback."""
    base = dict(CLI_MESSAGES.get("en", {}))
    if lang != "en" and lang in CLI_MESSAGES:
        base.update(CLI_MESSAGES[lang])
    return base
