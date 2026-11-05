# -*- mode: python ; coding: utf-8 -*-
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

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# Tentukan root proyek secara dinamis
SPEC_DIR = Path(os.path.abspath(SPECPATH))
PROJECT_ROOT = SPEC_DIR.parent if SPEC_DIR.name in ("build_tools", "packaging") else SPEC_DIR

is_windows = sys.platform == "win32"
is_macos = sys.platform == "darwin"
is_linux = sys.platform.startswith("linux")

# Kumpulkan aset statis proyek
datas = [
    (str(PROJECT_ROOT / "web"), "web"),
    (str(PROJECT_ROOT / "watermarks.example.json"), "."),
]

# Tambahkan direktori assets bersama jika ada
if (PROJECT_ROOT / "assets").is_dir():
    datas.append((str(PROJECT_ROOT / "assets"), "assets"))

# Tambahkan ikon aplikasi jika tersedia di root
for icon_candidate in (
    PROJECT_ROOT / "assets" / "cocr.ico",
    PROJECT_ROOT / "cocr.ico",
):
    if icon_candidate.is_file():
        datas.append((str(icon_candidate), "."))
        break

for png_candidate in (
    PROJECT_ROOT / "assets" / "cocr.png",
    PROJECT_ROOT / "cocr.png",
):
    if png_candidate.is_file():
        datas.append((str(png_candidate), "."))
        break

binaries = []
hiddenimports = [
    "cocr",
    "cocr.engine",
    "cocr.server",
    "cocr.cli",
    "cocr.exporters",
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "starlette",
    "starlette.middleware",
    "starlette.middleware.cors",
    "python_multipart",
    "docx",
    "reportlab",
    "PIL",
    "tkinter",
    "tkinter.filedialog",
    "webview",
]

# Tambahkan backend platform-spesifik untuk pywebview
if is_windows:
    hiddenimports.extend([
        "clr_loader",
        "pythonnet",
        "webview.platforms.winforms",
    ])
elif is_macos:
    hiddenimports.extend([
        "webview.platforms.cocoa",
    ])
else:  # Linux / Unix
    hiddenimports.extend([
        "webview.platforms.gtk",
    ])

# Kumpulkan seluruh data & model ONNX dari rapidocr_onnxruntime
r_datas, r_binaries, r_hidden = collect_all("rapidocr_onnxruntime")
datas.extend(r_datas)
binaries.extend(r_binaries)
hiddenimports.extend(r_hidden)

# Kumpulkan seluruh pustaka DLL/SO/DYLIB onnxruntime
o_datas, o_binaries, o_hidden = collect_all("onnxruntime")
datas.extend(o_datas)
binaries.extend(o_binaries)
hiddenimports.extend(o_hidden)

# Kumpulkan data webview (Edge WebView2 / Cocoa / WebKitGTK)
w_datas, w_binaries, w_hidden = collect_all("webview")
datas.extend(w_datas)
binaries.extend(w_binaries)
hiddenimports.extend(w_hidden)

# Kumpulkan data docx dan reportlab
datas.extend(collect_data_files("docx"))
datas.extend(collect_data_files("reportlab"))

# Hapus duplikat dari hiddenimports
hiddenimports = list(dict.fromkeys(hiddenimports))

# Mode build: onedir (default) atau onefile melalui environment variable COCR_BUILD_MODE
build_mode = os.getenv("COCR_BUILD_MODE", "onedir").strip().lower()
is_windowed = os.getenv("COCR_WINDOWED", "1").strip().lower() in ("1", "true", "yes")

# Pilih format ikon yang sesuai per sistem operasi
icon_path = None
ico_asset = PROJECT_ROOT / "assets" / "cocr.ico"
icns_asset = PROJECT_ROOT / "assets" / "cocr.icns"
png_asset = PROJECT_ROOT / "assets" / "cocr.png"

if is_windows:
    if ico_asset.is_file():
        icon_path = str(ico_asset)
    elif (PROJECT_ROOT / "cocr.ico").is_file():
        icon_path = str(PROJECT_ROOT / "cocr.ico")
elif is_macos:
    if icns_asset.is_file():
        icon_path = str(icns_asset)
    elif png_asset.is_file():
        icon_path = str(png_asset)
elif png_asset.is_file():
    icon_path = str(png_asset)

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT), str(PROJECT_ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "scipy", "pytest", "torch", "IPython"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

if build_mode == "onefile":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="cOCR",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=not is_windowed,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="cOCR",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=not is_windowed,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name="cOCR_Workbench",
    )

# Bundle khusus macOS (.app package)
if is_macos:
    app = BUNDLE(
        coll if build_mode == "onedir" else exe,
        name="cOCR Workbench.app",
        icon=icon_path,
        bundle_identifier="com.cocr.workbench",
        info_plist={
            "CFBundleDisplayName": "cOCR Workbench",
            "CFBundleName": "cOCR Workbench",
            "CFBundleShortVersionString": "1.2.0",
            "NSHighResolutionCapable": "True",
            "NSRequiresAquaSystemAppearance": "False",
            "LSBackgroundOnly": "0",
        },
    )
