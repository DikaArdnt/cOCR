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
import multiprocessing
import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cocr.cli import print_banner, run_cli
from cocr.i18n import detect_cli_lang, get_cli_strings
from cocr.server import start_gui_server


def attach_console_if_needed():
    """Attach stdout/stderr to parent console when launched from a terminal."""
    if sys.platform == "win32":
        try:
            import ctypes
            # -1: ATTACH_PARENT_PROCESS
            ctypes.windll.kernel32.AttachConsole(-1)
        except Exception:
            pass

        if sys.stdout is None:
            try:
                sys.stdout = open("CONOUT$", "w", encoding="utf-8")
            except Exception:
                try:
                    import os
                    sys.stdout = open(os.devnull, "w")
                except Exception:
                    pass

        if sys.stderr is None:
            try:
                sys.stderr = open("CONOUT$", "w", encoding="utf-8")
            except Exception:
                try:
                    import os
                    sys.stderr = open(os.devnull, "w")
                except Exception:
                    pass


def build_parser(lang: str = "en") -> argparse.ArgumentParser:
    s = get_cli_strings(lang)
    parser = argparse.ArgumentParser(description=s["app_desc"])

    parser.add_argument("-l", "--lang", type=str, default=lang, choices=["en", "id"], help=s["lang"])
    parser.add_argument("-i", "--input-dir", type=str, help=s["input_dir"])
    parser.add_argument("-o", "--output-dir", type=str, default=None, help=s["output_dir"])
    parser.add_argument("-f", "--format", type=str, default="all", choices=["md", "docx", "pdf", "all"], help=s["format"])
    parser.add_argument("-d", "--device", type=str, default="cpu", choices=["cpu", "gpu"], help=s["device"])
    parser.add_argument("-m", "--mode", type=str, default="auto", choices=["auto", "quiz", "document_mcq", "worksheet", "full"], help=s["mode"])
    parser.add_argument("--cli", action="store_true", help=s["cli"])
    parser.add_argument("--gui", action="store_true", help=s["gui"])
    parser.add_argument("--browser", action="store_true", help=s["browser"])
    parser.add_argument("--headless", action="store_true", help=s["headless"])
    parser.add_argument("--host", type=str, default=None, help=s["host"])
    parser.add_argument("--port", type=int, default=None, help=s["port"])

    return parser


def main():
    attach_console_if_needed()

    cli_lang = detect_cli_lang()
    parser = build_parser(cli_lang)
    args = parser.parse_args()

    # Re-sync language if explicitly specified via flag
    active_lang = args.lang or cli_lang
    strings = get_cli_strings(active_lang)

    if (args.cli or args.input_dir) and not args.gui:
        if not args.input_dir:
            print(strings["err_input_required"], file=sys.stderr)
            sys.exit(1)
        print_banner(lang=active_lang)
        run_cli(args)
    else:
        start_gui_server(
            host=args.host,
            port=args.port,
            use_browser=args.browser,
            headless=args.headless,
        )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
