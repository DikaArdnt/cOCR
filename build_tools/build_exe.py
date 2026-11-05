#!/usr/bin/env python3
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

"""
Skrip Otomasi Build Standalone Executable untuk cOCR Workbench.
Mendukung Windows (.exe), Linux (ELF Binary), dan macOS (.app Bundle).
"""

import argparse
import os
import platform
import shutil
import stat
import sys
import time
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


def get_root_dir() -> Path:
    """Mengembalikan direktori root proyek."""
    here = Path(__file__).resolve().parent
    return here.parent if here.name in ("build_tools", "packaging") else here


def ensure_icon(root_dir: Path) -> Path:
    """Memastikan file ikon cocr.ico dan cocr.png tersedia di folder assets/ di root proyek."""
    asset_dir = root_dir / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)

    ico_path = asset_dir / "cocr.ico"
    png_path = asset_dir / "cocr.png"

    if not (ico_path.is_file() and png_path.is_file()):
        try:
            from PIL import Image, ImageDraw

            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([16, 16, 240, 240], radius=48, fill=(15, 23, 42, 255), outline=(99, 102, 241, 255), width=6)
            draw.rounded_rectangle([60, 48, 196, 208], radius=16, fill=(248, 250, 252, 255))
            draw.polygon([(160, 48), (196, 84), (160, 84)], fill=(203, 213, 225, 255))
            draw.rounded_rectangle([78, 100, 178, 112], radius=4, fill=(100, 116, 139, 255))
            draw.rounded_rectangle([78, 126, 178, 138], radius=4, fill=(100, 116, 139, 255))
            draw.rounded_rectangle([78, 152, 140, 164], radius=4, fill=(100, 116, 139, 255))
            draw.rounded_rectangle([44, 135, 212, 145], radius=5, fill=(6, 182, 212, 255))
            draw.line([(44, 120), (44, 160)], fill=(6, 182, 212, 255), width=5)
            draw.line([(212, 120), (212, 160)], fill=(6, 182, 212, 255), width=5)

            img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            img.save(png_path, format="PNG")
            print("[INFO] Berkas icon cocr.ico dan cocr.png berhasil digenerate di assets/.")
        except Exception as e:
            print(f"[WARN] Tidak dapat membuat ikon otomatis: {e}")

    return ico_path if IS_WINDOWS else png_path


def create_usage_guide(dist_dir: Path):
    """Menulis panduan ringkas bagi pengguna per sistem operasi."""
    guide_path = dist_dir / "CARA_PENGGUNAAN.txt"

    if IS_WINDOWS:
        launch_instruction = "Klik ganda berkas 'cOCR.exe'."
        output_instruction = "folder 'outputs/' di samping cOCR.exe"
    elif IS_MACOS:
        launch_instruction = "Buka 'cOCR Workbench.app' (atau pindahkan ke folder Applications)."
        output_instruction = "folder 'outputs/' di samping aplikasi"
    else:
        launch_instruction = "Jalankan './cOCR' dari terminal atau klik ganda executable 'cOCR'."
        output_instruction = "folder 'outputs/' di samping biner cOCR"

    content = (
        "Panduan Penggunaan cOCR Workbench\n"
        "\n"
        "1. Menjalankan aplikasi:\n"
        f"   - {launch_instruction}\n"
        "   - Jendela desktop cOCR Workbench akan terbuka.\n"
        "\n"
        "2. Mengekstrak dokumen:\n"
        "   - Pilih 'Folder Dokumen' atau 'Unggah Berkas'.\n"
        "   - Tentukan mode tata letak dokumen.\n"
        "   - Tentukan format berkas (Markdown, Word, atau PDF).\n"
        "   - Klik tombol 'Mulai Ekstraksi Dokumen'.\n"
        "\n"
        "3. Lokasi berkas hasil:\n"
        f"   - Hasil ekstraksi tersimpan di {output_instruction}.\n"
        "\n"
        "4. Menutup aplikasi:\n"
        "   - Tutup jendela aplikasi (tombol silang).\n"
        "   - Server latar belakang akan otomatis berhenti.\n"
    )
    try:
        guide_path.write_text(content, encoding="utf-8")
    except Exception:
        pass


def check_linux_prerequisites():
    """Memeriksa pustaka WebKitGTK jika berjalan di Linux."""
    if not IS_LINUX:
        return
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        try:
            gi.require_version("WebKit2", "4.1")
        except ValueError:
            gi.require_version("WebKit2", "4.0")
        from gi.repository import WebKit2
        print("[INFO] WebKitGTK runtime terdeteksi dengan baik di Linux.")
    except Exception as e:
        print("\n[PERINGATAN] Runtime WebKitGTK belum terpasang di sistem Linux ini:")
        print(f"  Detail: {e}")
        print("  Untuk distribusi Debian/Ubuntu, silakan jalankan:")
        print("    sudo apt-get update && sudo apt-get install -y libwebkit2gtk-4.1-dev gir1.2-webkit2-4.1")
        print("  (Aplikasi tetap dapat dikompilasi, namun jendela GUI native membutuhkan WebKitGTK).\n")


def main():
    os_name = "Windows" if IS_WINDOWS else ("macOS" if IS_MACOS else "Linux")
    parser = argparse.ArgumentParser(description=f"Builder Standalone Executable cOCR Workbench ({os_name})")
    parser.add_argument(
        "--mode",
        choices=["onedir", "onefile"],
        default="onedir",
        help="Pilihan arsitektur build: 'onedir' (folder portabel, startup kilat - direkomendasikan) atau 'onefile' (1 file mandiri)."
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Sertakan jendela terminal konsol saat aplikasi dijalankan (berguna untuk debugging)."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Bersihkan cache build lama dan folder dist sebelum melakukan kompilasi."
    )

    args = parser.parse_args()
    root_dir = get_root_dir()

    print("\n" + "=" * 62)
    print(f"      cOCR Workbench - {os_name} Executable Builder")
    print("=" * 62)
    print(f"Sistem Operasi   : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Direktori Proyek : {root_dir}")
    print(f"Arsitektur Build : {args.mode.upper()}")
    print(f"Jendela Aplikasi : {'Windowed (Tanpa Konsol)' if not args.console else 'Dengan Konsol Debug'}")
    print(f"Bersihkan Cache  : {'Ya' if args.clean else 'Tidak'}")
    print("=" * 62 + "\n")

    try:
        import PyInstaller
        import PyInstaller.__main__
    except ImportError:
        print("[ERROR] PyInstaller belum terpasang. Jalankan: pip install pyinstaller atau uv pip install pyinstaller")
        sys.exit(1)

    try:
        import webview
    except ImportError:
        print("[ERROR] pywebview belum terpasang. Jalankan: pip install pywebview atau uv pip install pywebview")
        sys.exit(1)

    if IS_LINUX:
        check_linux_prerequisites()

    ensure_icon(root_dir)

    build_dir = root_dir / "build"
    dist_dir = root_dir / "dist"

    if args.clean:
        print("[1/3] Membersihkan folder build dan dist...")
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
        if dist_dir.exists():
            shutil.rmtree(dist_dir, ignore_errors=True)
    else:
        print("[1/3] Menyiapkan direktori build...")

    os.environ["COCR_BUILD_MODE"] = args.mode
    os.environ["COCR_WINDOWED"] = "0" if args.console else "1"

    spec_file = root_dir / "build_tools" / "cocr.spec"
    if not spec_file.is_file():
        spec_file = root_dir / "cocr.spec"
    if not spec_file.is_file():
        print(f"[ERROR] Berkas spesifikasi PyInstaller ({spec_file}) tidak ditemukan.")
        sys.exit(1)

    print(f"[2/3] Mengompilasi via PyInstaller ({args.mode})...")

    pyinstaller_args = [
        str(spec_file),
        "--noconfirm",
    ]
    if args.clean:
        pyinstaller_args.append("--clean")

    start_time = time.time()
    try:
        PyInstaller.__main__.run(pyinstaller_args)
    except Exception as e:
        print(f"\n[ERROR] Kompilasi gagal: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time

    print("[3/3] Menyiapkan berkas distribusi...")

    if IS_MACOS and (dist_dir / "cOCR Workbench.app").exists():
        app_path = dist_dir / "cOCR Workbench.app"
        create_usage_guide(dist_dir)
        final_target = app_path
    elif args.mode == "onedir":
        target_dir = dist_dir / "cOCR_Workbench"
        create_usage_guide(target_dir)

        if (root_dir / "watermarks.example.json").is_file():
            shutil.copy2(root_dir / "watermarks.example.json", target_dir / "watermarks.example.json")
        if (root_dir / ".env.example").is_file():
            shutil.copy2(root_dir / ".env.example", target_dir / ".env.example")

        exe_name = "cOCR.exe" if IS_WINDOWS else "cOCR"
        final_target = target_dir / exe_name

        if not IS_WINDOWS and final_target.is_file():
            final_target.chmod(final_target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    else:
        create_usage_guide(dist_dir)
        exe_name = "cOCR.exe" if IS_WINDOWS else "cOCR"
        final_target = dist_dir / exe_name
        if not IS_WINDOWS and final_target.is_file():
            final_target.chmod(final_target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print("\nBuild selesai.")
    print(f"Durasi kompilasi : {elapsed:.1f} detik")
    print(f"Lokasi output    : {final_target}")

    if final_target.is_file():
        size_mb = final_target.stat().st_size / (1024 * 1024)
        print(f"Ukuran biner     : {size_mb:.1f} MB")
    elif final_target.is_dir():
        total_size = sum(f.stat().st_size for f in final_target.rglob('*') if f.is_file())
        print(f"Ukuran paket     : {total_size / (1024 * 1024):.1f} MB")


if __name__ == "__main__":
    main()
