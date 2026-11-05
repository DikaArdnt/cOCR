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

import asyncio
import io
import os
import re
import shutil
import sys
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

from cocr.exporters import Exporters
from cocr.engine import OCREngine, check_gpu_support

# PyInstaller runtime check
IS_FROZEN = getattr(sys, "frozen", False)

if IS_FROZEN:
    BUNDLE_DIR = Path(sys._MEIPASS).resolve()
    APP_DIR = Path(sys.executable).resolve().parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parents[2]
    APP_DIR = BUNDLE_DIR
BASE_DIR = APP_DIR


def _load_env():
    """Load environment variables from .env if present."""
    env_file = APP_DIR / ".env"
    if not env_file.is_file():
        env_file = BUNDLE_DIR / ".env"
    if not env_file.is_file():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file)
    except ImportError:
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass

_load_env()

COCR_API_KEY = os.getenv("COCR_API_KEY", "").strip()
IS_CLOUD_MODE = os.getenv("COCR_CLOUD_MODE", "0").lower() in ("1", "true", "yes")
COCR_HOST = os.getenv("COCR_HOST", "127.0.0.1").strip()
try:
    COCR_PORT = int(os.getenv("COCR_PORT", "8765"))
except ValueError:
    COCR_PORT = 8765

app = FastAPI(title="cOCR Workbench", version="1.2.0")

# HTTP security headers
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    return response

# CORS configuration
raw_allowed = [o.strip() for o in os.getenv("COCR_ALLOWED_ORIGINS", "").split(",") if o.strip()]
if not raw_allowed:
    raw_allowed = [
        "http://localhost:8765",
        "http://127.0.0.1:8765",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=raw_allowed,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"],
)

if (BUNDLE_DIR / "web").is_dir():
    WEB_DIR = BUNDLE_DIR / "web"
else:
    WEB_DIR = APP_DIR / "web"

if (BUNDLE_DIR / "assets").is_dir():
    ASSETS_DIR = BUNDLE_DIR / "assets"
else:
    ASSETS_DIR = APP_DIR / "assets"

TEMP_UPLOADS_DIR = APP_DIR / "temp_uploads"
OUTPUTS_DIR = APP_DIR / "outputs"
WEB_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
TEMP_UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# File size and pixel constraints
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB per file limit
MAX_BATCH_SIZE = 100 * 1024 * 1024  # 100 MB total per batch
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "WEBP", "BMP"}

Image.MAX_IMAGE_PIXELS = 50_000_000
MAX_IMAGE_DIMENSION = 8192
MAX_TOTAL_PIXELS = 25_000_000

# Session registry
sessions_data: Dict[str, Dict[str, Any]] = {}
sessions_lock = threading.Lock()


def get_or_create_session(request: Request) -> str:
    """Retrieve or initialize an isolated session ID for the client."""
    sid = (
        request.headers.get("X-Session-ID") or
        request.query_params.get("session_id") or
        request.cookies.get("cocr_session_id") or
        ""
    ).strip()

    if not sid or not re.match(r"^[a-zA-Z0-9_\-]{8,64}$", sid):
        sid = uuid.uuid4().hex

    now = time.time()
    with sessions_lock:
        if sid not in sessions_data:
            sessions_data[sid] = {
                "status": "idle",
                "current_step": 0,
                "total_steps": 0,
                "message": "Menunggu instruksi",
                "elapsed_seconds": 0.0,
                "error": None,
                "data": None,
                "exported_files": {},
                "last_active": now,
                "folder_path": None,
            }
        else:
            sessions_data[sid]["last_active"] = now

        # Prune idle sessions older than 3 hours
        if len(sessions_data) > 30:
            expired = [k for k, v in sessions_data.items() if now - v.get("last_active", 0) > 10800]
            for exp_sid in expired:
                del sessions_data[exp_sid]
                exp_up = TEMP_UPLOADS_DIR / exp_sid
                exp_out = OUTPUTS_DIR / exp_sid
                if exp_up.exists():
                    shutil.rmtree(exp_up, ignore_errors=True)
                if exp_out.exists():
                    shutil.rmtree(exp_out, ignore_errors=True)

    return sid


def verify_api_key(request: Request):
    """Verify API key authentication if COCR_API_KEY is configured."""
    if not COCR_API_KEY:
        return

    api_key = (
        request.headers.get("X-API-Key") or
        request.query_params.get("api_key") or
        ""
    ).strip()

    if not api_key:
        auth_header = request.headers.get("Authorization", "").strip()
        if auth_header.lower().startswith("bearer "):
            api_key = auth_header[7:].strip()

    if not api_key or api_key != COCR_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Akses ditolak: API Key (COCR_API_KEY) tidak valid atau tidak disertakan."
        )


class ScanFolderRequest(BaseModel):
    folder_path: str


class StartOCRRequest(BaseModel):
    folder_path: str
    output_dir: Optional[str] = None
    mode: str = "auto"
    device: str = "cpu"
    formats: List[str] = ["md", "docx", "pdf"]


def clean_path(raw_path: str) -> str:
    """Strip quotes and normalize to an absolute path."""
    if not raw_path:
        return ""
    cleaned = raw_path.strip().strip('"').strip("'").strip()
    return os.path.abspath(os.path.normpath(cleaned))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and illegal characters."""
    base = Path(filename).name.strip()
    stem = Path(base).stem
    ext = Path(base).suffix.lower()
    clean_stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", stem)[:80]
    if not clean_stem:
        clean_stem = "gambar"
    return f"{clean_stem}{ext}"


def is_sensitive_system_path(resolved_path: Path) -> bool:
    """Check whether path points to critical OS or system directories."""
    resolved_str = str(resolved_path).lower()

    # Block access to internal application directories
    protected_roots = [APP_DIR.resolve(), BUNDLE_DIR.resolve()]
    for root in protected_roots:
        protected_repo_items = [
            root / ".git",
            root / ".env",
            root / "watermarks.json",
            root / "web",
            root / ".venv",
            root / ".agents",
        ]
        for prot in protected_repo_items:
            try:
                if resolved_path == prot or resolved_path.relative_to(prot):
                    return True
            except ValueError:
                pass

    if sys.platform == "win32":
        # Reject root drives (e.g., C:\, D:\)
        parts = resolved_path.parts
        if len(parts) <= 1:
            return True

        sensitive_win_keywords = [
            "\\windows",
            "\\program files",
            "\\program files (x86)",
            "\\programdata",
            "\\system volume information",
            "\\$recycle.bin",
            "\\recovery",
            "\\boot",
        ]
        for kw in sensitive_win_keywords:
            if kw in resolved_str:
                return True

        sensitive_user_folders = [
            "\\.ssh",
            "\\.aws",
            "\\.azure",
            "\\.gnupg",
            "\\appdata",
            "\\ntuser",
        ]
        for uf in sensitive_user_folders:
            if uf in resolved_str:
                return True
    else:
        sensitive_unix = [
            "/etc", "/proc", "/sys", "/dev", "/boot", "/root",
            "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/var/log",
        ]
        if resolved_str == "/" or any(resolved_str == su or resolved_str.startswith(su + "/") for su in sensitive_unix):
            return True

        sensitive_unix_user = ["/.ssh", "/.aws", "/.gnupg", "/.bashrc", "/.profile"]
        if any(su in resolved_str for su in sensitive_unix_user):
            return True

    return False


def verify_safe_folder(raw_path: str, session_id: Optional[str] = None) -> Path:
    """Validate folder path against traversal and system boundaries."""
    if not raw_path:
        raise HTTPException(status_code=400, detail="Lokasi direktori tidak boleh kosong.")

    cleaned = clean_path(raw_path)
    target = Path(cleaned).resolve()

    if IS_CLOUD_MODE:
        if not session_id:
            raise HTTPException(status_code=403, detail="Akses ditolak: sesi tidak valid.")

        allowed_upload = (TEMP_UPLOADS_DIR / session_id).resolve()
        allowed_output = (OUTPUTS_DIR / session_id).resolve()

        is_safe = False
        for allowed_root in (allowed_upload, allowed_output):
            try:
                target.relative_to(allowed_root)
                is_safe = True
                break
            except ValueError:
                pass

        if not is_safe:
            raise HTTPException(
                status_code=403,
                detail="Server berjalan dalam Cloud Mode. Akses direktori lokal dibatasi hanya pada berkas unggahan sesi."
            )
        return target

    if is_sensitive_system_path(target):
        raise HTTPException(
            status_code=403,
            detail="Akses ke direktori sistem atau direktori sensitif tersebut ditolak demi keamanan server."
        )

    return target


@app.get("/api/system-info")
def get_system_info():
    gpu = check_gpu_support()
    return {
        "gpu_available": gpu["has_gpu"],
        "device_description": gpu["description"],
        "providers": gpu["providers"],
        "cloud_mode": IS_CLOUD_MODE,
        "auth_required": bool(COCR_API_KEY),
    }


@app.post("/api/browse-folder")
def browse_folder(request: Request):
    """Open native OS folder picker dialog when desktop GUI is active."""
    verify_api_key(request)

    # Headless and cloud server guard
    if IS_CLOUD_MODE:
        raise HTTPException(
            status_code=403,
            detail="Dialog pemilih folder sistem dinonaktifkan dalam Cloud Mode demi keamanan server. Silakan gunakan tab Unggah Berkas."
        )

    if sys.platform != "win32" and not os.environ.get("DISPLAY"):
        raise HTTPException(
            status_code=400,
            detail="Dialog pemilih folder sistem tidak tersedia di lingkungan server headless. Silakan gunakan tab Unggah Berkas."
        )

    selected_path = ""
    handled_by_webview = False

    # Try native dialog when pywebview window is active
    try:
        import webview
        win = webview.active_window()
        if win:
            handled_by_webview = True
            dialog_type = getattr(getattr(webview, "FileDialog", None), "FOLDER", None) or getattr(webview, "FOLDER_DIALOG", 20)
            res = win.create_file_dialog(dialog_type)
            if res and len(res) > 0:
                selected_path = clean_path(res[0])
            else:
                # User cancelled webview dialog; suppress Tkinter fallback
                return {"cancelled": True, "folder_path": "", "files_count": 0}
    except Exception:
        handled_by_webview = False

    # Fall back to Tkinter if webview is unavailable
    if not handled_by_webview:
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            folder = filedialog.askdirectory(title="Pilih Folder Berisi Gambar")
            root.destroy()
            if folder:
                selected_path = clean_path(folder)
            else:
                return {"cancelled": True, "folder_path": "", "files_count": 0}
        except Exception:
            raise HTTPException(status_code=500, detail="Gagal membuka dialog sistem pada host server.")

    if not selected_path:
        return {"cancelled": True, "folder_path": "", "files_count": 0}

    session_id = get_or_create_session(request)
    valid_folder = verify_safe_folder(selected_path, session_id=session_id)
    files = OCREngine.get_image_files(str(valid_folder))
    return {
        "cancelled": False,
        "folder_path": str(valid_folder),
        "files_count": len(files),
        "files_preview": [os.path.basename(f) for f in files[:8]],
    }


@app.post("/api/scan-folder")
def scan_folder(req: ScanFolderRequest, request: Request):
    verify_api_key(request)
    session_id = get_or_create_session(request)

    valid_folder = verify_safe_folder(req.folder_path, session_id=session_id)
    if not valid_folder.is_dir():
        raise HTTPException(status_code=400, detail=f"Direktori '{valid_folder.name}' tidak ditemukan atau bukan folder.")

    folder_str = str(valid_folder)
    files = OCREngine.get_image_files(folder_str)
    return {
        "folder_path": folder_str,
        "base_folder": folder_str,
        "files_count": len(files),
        "files": [os.path.basename(f) for f in files],
    }


def _save_uploads(unique_uploads: List[UploadFile], session_id: str) -> Dict[str, Any]:
    """Save and validate uploaded files into the session-isolated directory."""
    if not unique_uploads:
        raise HTTPException(status_code=400, detail="Tidak ada berkas yang diunggah.")

    session_dir = TEMP_UPLOADS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Clean up only the caller's session directory
    for existing in session_dir.iterdir():
        if existing.is_file():
            try:
                existing.unlink()
            except Exception:
                pass

    saved_files: List[str] = []
    seen_stems: Set[str] = set()
    total_batch_bytes = 0

    for upload in unique_uploads:
        raw_name = getattr(upload, "filename", None) or "gambar.png"
        clean_name = sanitize_filename(raw_name)
        ext = os.path.splitext(clean_name)[1].lower()

        if ext not in ALLOWED_IMAGE_EXTS:
            continue

        stem = Path(clean_name).stem
        if stem in seen_stems:
            clean_name = f"{stem}_{len(saved_files) + 1}{ext}"
        seen_stems.add(stem)

        fileobj = getattr(upload, "file", None)
        content = b""
        if fileobj is not None:
            try:
                fileobj.seek(0)
            except Exception:
                pass
            content = fileobj.read(MAX_FILE_SIZE + 1024)
        elif isinstance(upload, bytes):
            content = upload

        file_size = len(content)
        if file_size == 0:
            continue
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Ukuran berkas '{raw_name}' melebihi batas maksimal 25 MB."
            )

        total_batch_bytes += file_size
        if total_batch_bytes > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Total ukuran berkas unggahan melebihi batas maksimal 100 MB per batch."
            )

        # Validate image integrity and enforce pixel limits
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
                if img.format not in ALLOWED_PIL_FORMATS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Berkas '{raw_name}' bukan format gambar yang didukung ({img.format})."
                    )

            with Image.open(io.BytesIO(content)) as img:
                w, h = img.size
                if w > MAX_IMAGE_DIMENSION or h > MAX_IMAGE_DIMENSION or (w * h) > MAX_TOTAL_PIXELS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Dimensi gambar '{raw_name}' ({w}x{h}) melebihi batas aman maksimum (8192x8192)."
                    )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Berkas '{raw_name}' rusak atau bukan format gambar valid."
            )

        save_path = session_dir / clean_name
        with open(save_path, "wb") as buffer:
            buffer.write(content)

        saved_files.append(clean_name)

    if not saved_files:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada berkas gambar valid yang berhasil diunggah (.jpg, .jpeg, .png, .webp, .bmp)."
        )

    abs_folder = str(session_dir.resolve())
    with sessions_lock:
        if session_id in sessions_data:
            sessions_data[session_id]["folder_path"] = abs_folder

    return {
        "folder_path": abs_folder,
        "files_count": len(saved_files),
        "files": saved_files,
        "session_id": session_id,
    }


@app.post("/api/upload-files")
@app.post("/api/upload-files/")
@app.post("/api/upload-file")
@app.post("/api/upload-file/")
@app.post("/api/upload")
@app.post("/api/upload/")
@app.post("/upload-files")
@app.post("/upload-file")
@app.post("/upload")
async def upload_files_endpoint(request: Request):
    """Handle file uploads with per-session workspace isolation."""
    verify_api_key(request)
    session_id = get_or_create_session(request)

    try:
        form = await request.form()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Gagal membaca payload form: {str(exc)}")

    seen_names: Set[str] = set()
    unique_uploads: List[UploadFile] = []

    for key, value in form.multi_items():
        if hasattr(value, "filename") and value.filename:
            raw_base = Path(value.filename).name.strip()
            if not raw_base or raw_base in seen_names:
                continue
            seen_names.add(raw_base)
            unique_uploads.append(value)

    if not unique_uploads:
        raise HTTPException(status_code=400, detail="Tidak ada berkas yang diunggah.")

    res = _save_uploads(unique_uploads, session_id=session_id)
    return res


def _worker_ocr(session_id: str, folder: str, output_dir: str, mode: str, device: str, formats: List[str]):
    start_time = time.time()

    def update_progress(cur: int, tot: int, msg: str):
        with sessions_lock:
            if session_id in sessions_data:
                sessions_data[session_id]["current_step"] = cur
                sessions_data[session_id]["total_steps"] = tot
                sessions_data[session_id]["message"] = msg
                sessions_data[session_id]["elapsed_seconds"] = round(time.time() - start_time, 1)

    try:
        use_gpu = device.lower() == "gpu"
        engine = OCREngine(use_gpu=use_gpu)

        data = engine.process_folder(
            folder_path=folder,
            mode=mode,
            progress_callback=update_progress,
        )

        os.makedirs(output_dir, exist_ok=True)
        base_name = "ekstraksi_dokumen"
        exported = {}

        if "md" in formats or "markdown" in formats:
            md_path = os.path.join(output_dir, f"{base_name}.md")
            Exporters.to_markdown(data, md_path)
            exported["md"] = md_path

        if "docx" in formats or "word" in formats:
            docx_path = os.path.join(output_dir, f"{base_name}.docx")
            Exporters.to_docx(data, docx_path)
            exported["docx"] = docx_path

        if "pdf" in formats:
            pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
            Exporters.to_pdf(data, pdf_path)
            exported["pdf"] = pdf_path

        with sessions_lock:
            if session_id in sessions_data:
                sessions_data[session_id]["status"] = "completed"
                sessions_data[session_id]["message"] = "Ekstraksi dan ekspor berkas selesai."
                sessions_data[session_id]["data"] = data
                sessions_data[session_id]["exported_files"] = exported
                sessions_data[session_id]["elapsed_seconds"] = round(time.time() - start_time, 2)

    except Exception:
        with sessions_lock:
            if session_id in sessions_data:
                sessions_data[session_id]["status"] = "error"
                sessions_data[session_id]["error"] = "Terjadi kegagalan saat ekstraksi OCR atau penulisan dokumen."
                sessions_data[session_id]["message"] = "Terjadi kesalahan saat pemrosesan."
                sessions_data[session_id]["elapsed_seconds"] = round(time.time() - start_time, 2)


@app.post("/api/start-ocr")
def start_ocr(req: StartOCRRequest, request: Request):
    verify_api_key(request)
    session_id = get_or_create_session(request)

    with sessions_lock:
        sess = sessions_data.setdefault(session_id, {
            "status": "idle",
            "current_step": 0,
            "total_steps": 1,
            "message": "Menunggu instruksi",
            "elapsed_seconds": 0.0,
            "error": None,
            "data": None,
            "exported_files": {},
            "last_active": time.time(),
        })

        if sess["status"] == "running":
            raise HTTPException(status_code=400, detail="Pekerjaan OCR pada sesi ini sedang berjalan.")

        valid_folder = verify_safe_folder(req.folder_path, session_id=session_id)
        if not (valid_folder.is_dir() or valid_folder.is_file()):
            raise HTTPException(status_code=400, detail=f"Direktori masukan '{valid_folder.name}' tidak ditemukan.")

        folder_str = str(valid_folder)

        # Isolate output directory per session in cloud mode
        if IS_CLOUD_MODE or not req.output_dir:
            out_dir = str((OUTPUTS_DIR / session_id).resolve())
        else:
            valid_out = verify_safe_folder(req.output_dir, session_id=session_id)
            out_dir = str(valid_out)

        sess.update({
            "status": "running",
            "current_step": 0,
            "total_steps": 1,
            "message": "Menginisialisasi pekerjaan...",
            "elapsed_seconds": 0.0,
            "error": None,
            "data": None,
            "exported_files": {},
            "last_active": time.time(),
        })

    thread = threading.Thread(
        target=_worker_ocr,
        args=(session_id, folder_str, out_dir, req.mode, req.device, req.formats),
        daemon=True
    )
    thread.start()

    return {"status": "started", "session_id": session_id, "output_dir": out_dir}


@app.get("/api/task-status")
def get_task_status(request: Request):
    verify_api_key(request)
    session_id = get_or_create_session(request)

    with sessions_lock:
        sess = sessions_data.get(session_id)
        if not sess:
            return {
                "status": "idle",
                "current_step": 0,
                "total_steps": 0,
                "message": "Menunggu instruksi",
                "elapsed_seconds": 0.0,
                "error": None,
                "data": None,
                "exported_files": {},
            }

        return {
            "status": sess["status"],
            "current_step": sess["current_step"],
            "total_steps": sess["total_steps"],
            "message": sess["message"],
            "elapsed_seconds": sess["elapsed_seconds"],
            "error": sess["error"],
            "data": sess["data"],
            "exported_files": {k: os.path.basename(v) for k, v in sess["exported_files"].items()},
        }


@app.get("/api/download/{fmt}")
def download_file(fmt: str, request: Request):
    verify_api_key(request)
    fmt = fmt.lower()
    if fmt not in {"md", "docx", "pdf"}:
        raise HTTPException(status_code=400, detail="Format unduhan tidak didukung.")

    session_id = get_or_create_session(request)

    with sessions_lock:
        sess = sessions_data.get(session_id)
        if not sess:
            raise HTTPException(status_code=404, detail="Sesi pekerjaan belum tersedia.")

        fpath = sess.get("exported_files", {}).get(fmt)
        if not fpath or not os.path.exists(fpath):
            raise HTTPException(status_code=404, detail=f"Berkas format '{fmt}' belum tersedia atau tidak ditemukan.")

        resolved_download = Path(fpath).resolve()

        # Validate download path against directory traversal
        if is_sensitive_system_path(resolved_download):
            raise HTTPException(status_code=403, detail="Akses unduhan berkas ditolak.")

        return FileResponse(
            path=str(resolved_download),
            filename=resolved_download.name,
            media_type="application/octet-stream"
        )


# Mount static web assets and shared application icons
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if (WEB_DIR / "style.css").exists() or WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    """Serve the application favicon."""
    for candidate in (
        ASSETS_DIR / "cocr.ico",
        ASSETS_DIR / "cocr.png",
        WEB_DIR / "favicon.ico",
    ):
        if candidate.is_file():
            media = "image/x-icon" if candidate.suffix.lower() == ".ico" else "image/png"
            return FileResponse(str(candidate), media_type=media)
    raise HTTPException(status_code=404, detail="Favicon tidak ditemukan.")


@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(
        content="<h1>Antarmuka Web OCR Sedang Dipersiapkan</h1><p>Silakan muat ulang halaman dalam beberapa detik.</p>"
    )


class ThreadedUvicornServer(uvicorn.Server):
    """Subclass uvicorn Server to allow clean background thread execution without signal conflicts."""
    def install_signal_handlers(self):
        pass


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(start_port: int = 8765, host: str = "127.0.0.1", max_tries: int = 30) -> int:
    for p in range(start_port, start_port + max_tries):
        if is_port_available(p, host):
            return p
    return start_port


def start_gui_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    use_browser: bool = False,
    headless: bool = False,
):
    final_host = host or COCR_HOST
    base_port = port or COCR_PORT
    # Find an available port automatically when binding to localhost
    if final_host in ("127.0.0.1", "localhost") and not is_port_available(base_port, final_host):
        final_port = find_available_port(base_port, host=final_host)
    else:
        final_port = base_port

    url = f"http://{final_host}:{final_port}"

    print("==================================================")
    print("   cOCR Workbench - Visual Document OCR & Extraction")
    print("==================================================")
    print(f"URL Server   : {url}")
    print(f"Mode Operasi : {'Cloud Mode (Terisolasi)' if IS_CLOUD_MODE else 'Desktop Lokal'}")
    if COCR_API_KEY:
        print("Proteksi API : AKTIF (Key Terpasang)")

    # Headless / server mode
    if IS_CLOUD_MODE or headless:
        print("\nMenjalankan server antarmuka grafis di latar belakang...")
        print("Tekan Ctrl+C untuk menghentikan server.\n")
        uvicorn.run(app, host=final_host, port=final_port, log_level="warning")
        return

    # External browser mode (--browser)
    if use_browser:
        print("Mode tampilan: peramban eksternal")
        print("Tekan Ctrl+C untuk menghentikan aplikasi.\n")
        if final_host in ("127.0.0.1", "localhost"):
            def _open_browser():
                time.sleep(1.0)
                webbrowser.open(url)
            threading.Thread(target=_open_browser, daemon=True).start()
        uvicorn.run(app, host=final_host, port=final_port, log_level="warning")
        return

    # Native desktop window (pywebview)
    print("Menyiapkan antarmuka aplikasi...")

    config = uvicorn.Config(app=app, host=final_host, port=final_port, log_level="warning")
    server = ThreadedUvicornServer(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    for _ in range(60):
        if server.started:
            break
        time.sleep(0.05)

    try:
        import webview

        icon_file = None
        for icon_candidate in (
            ASSETS_DIR / "cocr.ico",
            ASSETS_DIR / "cocr.png",
            APP_DIR / "assets" / "cocr.ico",
            APP_DIR / "assets" / "cocr.png",
            BUNDLE_DIR / "assets" / "cocr.ico",
            BUNDLE_DIR / "assets" / "cocr.png",
            BUNDLE_DIR / "cocr.ico",
            APP_DIR / "cocr.ico",
            BUNDLE_DIR / "cocr.png",
            APP_DIR / "cocr.png",
        ):
            if icon_candidate.is_file():
                icon_file = str(icon_candidate)
                break

        window = webview.create_window(
            title="cOCR Workbench",
            url=url,
            width=1240,
            height=840,
            min_size=(880, 600),
            text_select=True,
            confirm_close=False,
        )

        webview.start(icon=icon_file, debug=False)

    except Exception as err:
        print(f"\n[Info] Jendela desktop tidak dapat dimuat: {err}")
        print("Membuka melalui peramban web sebagai fallback...\n")
        webbrowser.open(url)
        try:
            while server_thread.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    finally:
        server.should_exit = True
        server_thread.join(timeout=2.0)
        sys.exit(0)


if __name__ == "__main__":
    start_gui_server()
