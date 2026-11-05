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

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

# Ensure src directory is in sys.path when executed directly
_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from cocr.engine import OCREngine, check_gpu_support
from cocr.exporters import Exporters
from cocr.i18n import detect_cli_lang, get_cli_strings


def print_banner(lang: str = "en"):
    strings = get_cli_strings(lang)
    gpu_info = check_gpu_support()
    print("cOCR Workbench")
    print(strings["device_banner"].format(device=gpu_info["description"]))
    print(strings["formats_banner"])


def run_cli(args):
    lang = getattr(args, "lang", "en")
    strings = get_cli_strings(lang)

    input_dir = os.path.abspath(args.input_dir)
    if not os.path.isdir(input_dir):
        print(strings["err_input_not_found"].format(path=input_dir), file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.abspath(args.output_dir) if args.output_dir else os.path.join(input_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    use_gpu = args.device.lower() == "gpu"
    print(strings["init_engine"].format(device="GPU" if use_gpu else "CPU"))

    engine = OCREngine(use_gpu=use_gpu)
    active_device = engine.gpu_info["description"] if engine.use_gpu else "CPU"
    print(strings["engine_ready"].format(device=active_device))

    files = engine.get_image_files(input_dir)
    if not files:
        print(strings["warn_no_images"].format(path=input_dir))
        print(strings["supported_extensions"])
        sys.exit(0)

    print(strings["found_files"].format(count=len(files)))
    print(strings["segmentation_mode"].format(mode=args.mode))
    print(strings["output_directory"].format(path=output_dir))

    start_time = time.time()

    def on_progress(current: int, total: int, message: str):
        percent = int((current / max(total, 1)) * 100)
        bar_len = 24
        filled = int(bar_len * current / max(total, 1))
        bar = "=" * filled + "-" * (bar_len - filled)
        sys.stdout.write(f"\r[{bar}] {percent:3d}% | {message[:40]:<40}")
        sys.stdout.flush()

    data = engine.process_folder(
        folder_path=input_dir,
        mode=args.mode,
        progress_callback=on_progress
    )
    sys.stdout.write("\n\n")

    elapsed = time.time() - start_time
    print(strings["completed"].format(time=elapsed))
    print(strings["scanned_files"].format(count=data["total_files"]))
    print(strings["unique_files"].format(count=data["unique_files"]))
    print(strings["duplicate_files"].format(count=data["duplicate_files"]))

    fmt = args.format.lower()
    exported_files: List[str] = []

    base_name = "hasil_ekstraksi_dokumen"
    if fmt in ["md", "all", "markdown"]:
        md_file = os.path.join(output_dir, f"{base_name}.md")
        Exporters.to_markdown(data, md_file)
        exported_files.append(md_file)

    if fmt in ["docx", "all", "word"]:
        docx_file = os.path.join(output_dir, f"{base_name}.docx")
        Exporters.to_docx(data, docx_file)
        exported_files.append(docx_file)

    if fmt in ["pdf", "all"]:
        pdf_file = os.path.join(output_dir, f"{base_name}.pdf")
        Exporters.to_pdf(data, pdf_file)
        exported_files.append(pdf_file)

    print(strings["generated_files"])
    for out in exported_files:
        size_kb = os.path.getsize(out) / 1024
        print(f"  -> {out} ({size_kb:.1f} KB)")
    print(strings["done"])


def build_cli_parser(lang: str = "en") -> argparse.ArgumentParser:
    s = get_cli_strings(lang)
    parser = argparse.ArgumentParser(description=s["app_desc_cli"])
    parser.add_argument("-l", "--lang", type=str, default=lang, choices=["en", "id"], help=s["lang"])
    parser.add_argument("-i", "--input-dir", type=str, help=s["input_dir"])
    parser.add_argument("-o", "--output-dir", type=str, default=None, help=s["output_dir"])
    parser.add_argument("-f", "--format", type=str, default="all", choices=["md", "docx", "pdf", "all"], help=s["format"])
    parser.add_argument("-d", "--device", type=str, default="cpu", choices=["cpu", "gpu"], help=s["device"])
    parser.add_argument("-m", "--mode", type=str, default="auto", choices=["auto", "quiz", "document_mcq", "worksheet", "full"], help=s["mode"])
    parser.add_argument("--gui", action="store_true", help=s["gui"])
    return parser


def main():
    cli_lang = detect_cli_lang()
    parser = build_cli_parser(cli_lang)
    args = parser.parse_args()

    active_lang = args.lang or cli_lang
    strings = get_cli_strings(active_lang)

    if args.gui or len(sys.argv) == 1:
        from cocr.server import start_gui_server
        start_gui_server()
    else:
        if not args.input_dir:
            print(strings["err_input_required"], file=sys.stderr)
            sys.exit(1)
        print_banner(lang=active_lang)
        run_cli(args)


if __name__ == "__main__":
    main()
