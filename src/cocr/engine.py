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

import glob
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import onnxruntime as ort
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

# Guard against decompression bombs and excessive memory usage
Image.MAX_IMAGE_PIXELS = 50_000_000
MAX_IMAGE_DIMENSION = 8192
MAX_TOTAL_PIXELS = 25_000_000


def check_gpu_support() -> Dict[str, Any]:
    providers = ort.get_available_providers()
    has_cuda = "CUDAExecutionProvider" in providers
    has_dml = "DmlExecutionProvider" in providers
    has_gpu = has_cuda or has_dml
    return {
        "has_gpu": has_gpu,
        "cuda": has_cuda,
        "directml": has_dml,
        "providers": providers,
        "description": "CUDA (NVIDIA)" if has_cuda else ("DirectML (AMD/Intel/NVIDIA)" if has_dml else "CPU Only")
    }


def is_tilted_box(box: List[List[float]], angle_threshold_deg: float = 16.0) -> bool:
    if len(box) < 2:
        return False
    p0, p1 = box[0], box[1]
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    angle = abs(math.degrees(math.atan2(dy, dx)))
    return angle > angle_threshold_deg


DEFAULT_WATERMARK_PATTERNS: List[str] = [
    r"\.com",
    r"whatsapp",
]


def load_watermark_patterns(
    custom_patterns: Optional[List[str]] = None,
    config_file: str = "watermarks.json"
) -> List[str]:
    """Load watermark regex patterns from config, falling back to built-in defaults."""
    if custom_patterns is not None:
        return [str(p).strip() for p in custom_patterns if str(p).strip() and len(str(p).strip()) <= 200]

    candidates = []
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        bundle_dir = Path(getattr(sys, "_MEIPASS", exe_dir)).resolve()
        candidates.extend([
            exe_dir / config_file,
            bundle_dir / config_file,
        ])
    candidates.extend([
        Path(__file__).resolve().parents[2] / config_file,
        Path(__file__).resolve().parent / config_file,
        Path.cwd() / config_file,
    ])

    for path in candidates:
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return [str(p).strip() for p in data if str(p).strip() and len(str(p).strip()) <= 200]
                elif isinstance(data, dict):
                    patterns = data.get("watermark_patterns") or data.get("patterns") or []
                    if isinstance(patterns, list):
                        return [str(p).strip() for p in patterns if str(p).strip() and len(str(p).strip()) <= 200]
            except Exception:
                pass

    return list(DEFAULT_WATERMARK_PATTERNS)


class OCREngine:
    SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    DEFAULT_WATERMARK_PATTERNS = DEFAULT_WATERMARK_PATTERNS
    WATERMARK_PATTERNS = DEFAULT_WATERMARK_PATTERNS

    def __init__(
        self,
        use_gpu: bool = False,
        watermark_patterns: Optional[List[str]] = None,
        config_file: str = "watermarks.json"
    ):
        self.gpu_info = check_gpu_support()
        self.use_gpu = use_gpu and self.gpu_info["has_gpu"]
        
        self.watermark_patterns = load_watermark_patterns(
            custom_patterns=watermark_patterns,
            config_file=config_file
        )
        self.WATERMARK_PATTERNS = self.watermark_patterns
        self._compiled_cache = None
        self._compiled_cache_source = None
        
        ocr_kwargs = {"use_cls": False}
        if self.use_gpu:
            if self.gpu_info["cuda"]:
                ocr_kwargs["use_cuda"] = True
            elif self.gpu_info["directml"]:
                ocr_kwargs["use_dml"] = True
        
        try:
            self.ocr = RapidOCR(**ocr_kwargs)
        except Exception:
            # Fall back to CPU if GPU provider initialization fails
            self.use_gpu = False
            self.ocr = RapidOCR(use_cls=False)

    @property
    def compiled_watermarks(self) -> List[re.Pattern]:
        """Return cached compiled regex patterns for watermark filtering."""
        if self._compiled_cache is None or self._compiled_cache_source != self.watermark_patterns:
            compiled = []
            for pat in self.watermark_patterns:
                try:
                    compiled.append(re.compile(pat, re.IGNORECASE))
                except re.error:
                    compiled.append(re.compile(re.escape(pat), re.IGNORECASE))
            self._compiled_cache = compiled
            self._compiled_cache_source = list(self.watermark_patterns)
        return self._compiled_cache

    @staticmethod
    def get_image_files(folder_path: str) -> List[str]:
        if os.path.isfile(folder_path):
            ext = os.path.splitext(folder_path)[1].lower()
            if ext in OCREngine.SUPPORTED_EXTENSIONS:
                return [os.path.abspath(folder_path)]
            return []
        if not os.path.isdir(folder_path):
            return []
        all_files = []
        for ext in OCREngine.SUPPORTED_EXTENSIONS:
            all_files.extend(glob.glob(os.path.join(folder_path, f"*{ext}")))
            all_files.extend(glob.glob(os.path.join(folder_path, f"*{ext.upper()}")))
        return sorted(list(set(all_files)))

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def detect_page_number(self, ocr_results: List[Any], image_height: int) -> Tuple[int, int]:
        for box, text, _ in ocr_results:
            ys = [p[1] for p in box]
            if min(ys) > image_height * 0.82:
                match = re.search(r"(\d+)\s*/\s*(\d+)", text)
                if match:
                    return int(match.group(1)), int(match.group(2))
        return -1, -1

    def filter_and_cluster_boxes(
        self,
        ocr_results: List[Any],
        image_width: int,
        image_height: int,
        is_quiz_layout: bool = True
    ) -> List[Dict[str, Any]]:
        clean_boxes = []

        for box, text, score in ocr_results:
            txt = text.replace("\uff09", ")").replace("\uff08", "(").strip()
            if not txt:
                continue

            ys = [p[1] for p in box]
            xs = [p[0] for p in box]
            y_min, y_max = min(ys), max(ys)
            x_min, x_max = min(xs), max(xs)

            # Filter headers and footers for mobile quiz layout
            if is_quiz_layout and y_max < image_height * 0.12:
                continue

            if is_quiz_layout and y_min > image_height * 0.85:
                continue

            if is_quiz_layout and y_min > image_height * 0.78:
                if txt in ["100%", "+", "A", "B", "C", "D"]:
                    continue

            # Skip diagonal watermark boxes
            if is_tilted_box(box):
                continue

            if any(pat.search(txt) for pat in self.compiled_watermarks):
                continue

            # Skip single-character non-alphanumeric noise
            if len(txt) == 1 and not txt.isalnum() and txt not in ["?", ":", ";"]:
                continue

            clean_boxes.append({
                "text": txt,
                "y_min": y_min,
                "y_max": y_max,
                "y_center": (y_min + y_max) / 2.0,
                "x_min": x_min,
                "x_max": x_max,
                "score": float(score),
            })

        return self._sort_reading_order(clean_boxes)

    @staticmethod
    def _sort_reading_order(boxes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not boxes:
            return []

        sorted_by_y = sorted(boxes, key=lambda b: (b["y_center"], b["x_min"]))
        lines: List[List[Dict[str, Any]]] = []

        for b in sorted_by_y:
            placed = False
            for line in lines:
                avg_y = sum(item["y_center"] for item in line) / len(line)
                avg_h = sum(item["y_max"] - item["y_min"] for item in line) / len(line)
                # Adaptive vertical line threshold based on median font height
                if abs(b["y_center"] - avg_y) <= max(avg_h * 0.45, 6.0):
                    line.append(b)
                    placed = True
                    break
            if not placed:
                lines.append([b])

        lines.sort(key=lambda line: min(item["y_min"] for item in line))
        ordered: List[Dict[str, Any]] = []
        for line in lines:
            line.sort(key=lambda item: item["x_min"])
            ordered.extend(line)

        return ordered

    @staticmethod
    def _group_into_text_lines(boxes: List[Dict[str, Any]]) -> List[str]:
        """Group vertically aligned text boxes into coherent sentence lines."""
        if not boxes:
            return []

        sorted_by_y = sorted(boxes, key=lambda b: (b["y_center"], b["x_min"]))
        lines: List[List[Dict[str, Any]]] = []

        for b in sorted_by_y:
            placed = False
            for line in lines:
                avg_y = sum(item["y_center"] for item in line) / len(line)
                avg_h = sum(item["y_max"] - item["y_min"] for item in line) / len(line)
                if abs(b["y_center"] - avg_y) <= max(avg_h * 0.45, 6.0):
                    line.append(b)
                    placed = True
                    break
            if not placed:
                lines.append([b])

        lines.sort(key=lambda line: min(item["y_min"] for item in line))
        text_lines: List[str] = []
        for line in lines:
            line.sort(key=lambda item: item["x_min"])
            merged = " ".join(item["text"] for item in line).strip()
            if merged and merged != "。":
                text_lines.append(merged)

        return text_lines

    def detect_document_layout(
        self,
        width: int,
        height: int,
        raw_results: List[Any],
        text_lines: List[str]
    ) -> str:
        """
        Klasifikasikan tata letak dokumen:
        - mobile_quiz: format 2 kartu ponsel (rasio tinggi > 1.6 atau terdeteksi navigasi kuis)
        - worksheet: lembar kerja berseksi (A, B, C) dan kalimat rumpang
        - document_mcq: naskah soal pilihan ganda beruntun
        - generic_document: dokumen umum / naratif
        """
        aspect = height / max(width, 1)
        has_page_ratio = False
        has_quiz_nav = False

        for box, text, _ in (raw_results or []):
            t = text.strip()
            ys = [p[1] for p in box]
            if min(ys) > height * 0.82 and re.search(r"\d+\s*/\s*\d+", t):
                has_page_ratio = True
            if min(ys) > height * 0.78 and t in ["100%", "+", "A", "B", "C", "D"]:
                has_quiz_nav = True

        if aspect >= 1.6 or (has_page_ratio and has_quiz_nav) or (aspect > 1.5 and has_page_ratio):
            return "mobile_quiz"

        sec_re = re.compile(r"^([A-D])[\.\)]\s+([A-Z].*)$")
        q_re = re.compile(r"^(\d{1,3})[\.\)]\s*(.*)$")
        opt_re = re.compile(r"^([a-eA-E])(\.{1,3}|\))\s*(.*)$")

        sec_count = sum(1 for l in text_lines if sec_re.match(l))
        q_count = sum(1 for l in text_lines if q_re.match(l))
        opt_count = sum(1 for l in text_lines if opt_re.match(l))

        # Worksheet: at least two sections (A/B/C/D) with blank-fill items
        if sec_count >= 2 and q_count >= 3 and opt_count < q_count:
            return "worksheet"

        # Multiple-choice: numbered questions followed by options (a-e)
        if q_count >= 2 and opt_count >= q_count:
            return "document_mcq"

        return "generic_document"

    def parse_quiz_card(self, boxes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not boxes:
            return None

        question_lines: List[str] = []
        options: List[str] = []
        in_options = False

        opt_re = re.compile(r"^([A-Ea-e][\.\)]|[0-9]+[\.\)])\s*(.*)$")
        standalone_opt_re = re.compile(r"^([A-Ea-e])([A-Z][a-z].*)$")

        for b in boxes:
            t = b["text"]
            match_opt = opt_re.match(t)
            match_stand = standalone_opt_re.match(t)

            if match_opt:
                in_options = True
                prefix = match_opt.group(1)
                body = match_opt.group(2).strip()
                options.append(f"{prefix} {body}" if body else prefix)
            elif match_stand:
                in_options = True
                prefix = f"{match_stand.group(1)}."
                body = match_stand.group(2).strip()
                options.append(f"{prefix} {body}")
            elif in_options:
                options[-1] += f" {t}"
            else:
                question_lines.append(t)

        question_text = " ".join(question_lines).strip()
        return {
            "question": question_text,
            "options": options,
            "raw_text": "\n".join(b["text"] for b in boxes)
        }

    def _parse_mobile_quiz(
        self,
        filtered_boxes: List[Dict[str, Any]],
        height: int,
        page_num: int,
        total_pages: int
    ) -> List[Dict[str, Any]]:
        """Split mobile screenshots into top and bottom cards based on content boundaries."""
        card1_boxes = [b for b in filtered_boxes if b["y_max"] < height * 0.52]
        card2_boxes = [b for b in filtered_boxes if b["y_min"] >= height * 0.52]

        items: List[Dict[str, Any]] = []
        c1 = self.parse_quiz_card(card1_boxes)
        if c1 and (c1["question"] or c1["options"]):
            p1 = page_num if page_num > 0 else 1
            items.append({
                "card_index": 1,
                "page_number": p1,
                "question": c1["question"],
                "options": c1["options"],
                "raw_text": c1["raw_text"]
            })

        c2 = self.parse_quiz_card(card2_boxes)
        if c2 and (c2["question"] or c2["options"]):
            p2 = (page_num + 1) if (page_num > 0 and (total_pages <= 0 or page_num < total_pages)) else (page_num if page_num > 0 else 2)
            items.append({
                "card_index": 2,
                "page_number": p2,
                "question": c2["question"],
                "options": c2["options"],
                "raw_text": c2["raw_text"]
            })
        return items

    def _parse_document_mcq(
        self,
        text_lines: List[str],
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Extract sequential multiple-choice questions and option blocks (a-e)."""
        q_re = re.compile(r"^(\d{1,3})[\.\)]\s*(.*)$")
        opt_re = re.compile(r"^([a-eA-E])(\.{1,3}|\))\s*(.*)$")

        items: List[Dict[str, Any]] = []
        curr_item: Optional[Dict[str, Any]] = None
        in_options = False
        card_counter = 1

        for line in text_lines:
            qm = q_re.match(line)
            om = opt_re.match(line)

            if qm and not om:
                curr_item = {
                    "card_index": card_counter,
                    "page_number": page_num,
                    "number": qm.group(1),
                    "question": qm.group(2).strip(),
                    "options": [],
                    "raw_text": line
                }
                items.append(curr_item)
                card_counter += 1
                in_options = False
            elif om and curr_item is not None:
                in_options = True
                norm_opt = f"{om.group(1).lower()}. {om.group(3).strip()}"
                curr_item["options"].append(norm_opt)
                curr_item["raw_text"] += f"\n{line}"
            elif in_options and curr_item is not None and curr_item["options"]:
                curr_item["options"][-1] += f" {line}"
                curr_item["raw_text"] += f" {line}"
            elif curr_item is not None and not in_options:
                curr_item["question"] = (curr_item["question"] + f" {line}").strip()
                curr_item["raw_text"] += f"\n{line}"

        if not items:
            return self._parse_generic(text_lines, page_num)
        return items

    def _parse_worksheet(
        self,
        text_lines: List[str],
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Extract structured worksheet sections and exercise items."""
        sec_re = re.compile(r"^([A-D])[\.\)]\s+([A-Z].*)$")
        q_re = re.compile(r"^(\d{1,3})[\.\)]\s*(.*)$")

        items: List[Dict[str, Any]] = []
        current_sec = ""
        current_instr = ""
        card_counter = 1

        for line in text_lines:
            sm = sec_re.match(line)
            qm = q_re.match(line)

            if sm:
                current_sec = sm.group(0).strip()
                current_instr = ""
            elif qm:
                curr_item = {
                    "card_index": card_counter,
                    "page_number": page_num,
                    "section": current_sec,
                    "instruction": current_instr,
                    "number": qm.group(1),
                    "question": qm.group(2).strip(),
                    "options": [],
                    "raw_text": line
                }
                items.append(curr_item)
                card_counter += 1
            elif not items or items[-1].get("section") != current_sec:
                current_instr = (current_instr + f" {line}").strip()
            else:
                items[-1]["question"] = (items[-1]["question"] + f" {line}").strip()
                items[-1]["raw_text"] += f"\n{line}"

        if not items:
            return self._parse_generic(text_lines, page_num)
        return items

    def _parse_generic(
        self,
        text_lines: List[str],
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Extract free-form or unstructured prose documents."""
        all_text = " ".join(text_lines).strip()
        return [{
            "card_index": 1,
            "page_number": page_num,
            "question": all_text,
            "options": [],
            "raw_text": "\n".join(text_lines)
        }]

    def process_single_image(
        self,
        file_path: str,
        mode: str = "auto"
    ) -> Dict[str, Any]:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION or (width * height) > MAX_TOTAL_PIXELS:
                    return {
                        "file": file_path,
                        "filename": os.path.basename(file_path),
                        "hash": "",
                        "page": -1,
                        "total_pages": -1,
                        "layout_type": "error",
                        "items": [],
                        "status": "error_oversized",
                        "error": f"Dimensi gambar {width}x{height} melebihi batas aman maksimum.",
                        "width": width,
                        "height": height,
                    }
        except Exception as e:
            return {
                "file": file_path,
                "filename": os.path.basename(file_path),
                "hash": "",
                "page": -1,
                "total_pages": -1,
                "layout_type": "error",
                "items": [],
                "status": "error_corrupted",
                "error": f"Berkas gambar rusak atau tidak dapat dibaca: {str(e)}",
                "width": 0,
                "height": 0,
            }

        file_hash = self.calculate_file_hash(file_path)
        try:
            raw_results, _ = self.ocr(file_path)
        except Exception as ocr_err:
            raw_results = None

        if not raw_results:
            return {
                "file": file_path,
                "filename": os.path.basename(file_path),
                "hash": file_hash,
                "page": -1,
                "total_pages": -1,
                "layout_type": "empty",
                "items": [],
                "status": "empty",
                "width": width,
                "height": height,
            }

        page_num, total_pages = self.detect_page_number(raw_results, height)

        # Group early text boxes for layout detection
        pre_boxes = []
        for box, text, score in raw_results:
            t = text.strip()
            if not t or is_tilted_box(box) or any(pat.search(t) for pat in self.compiled_watermarks):
                continue
            ys = [p[1] for p in box]
            xs = [p[0] for p in box]
            pre_boxes.append({
                "text": t,
                "y_min": min(ys),
                "y_max": max(ys),
                "y_center": (min(ys) + max(ys)) / 2.0,
                "x_min": min(xs),
                "x_max": max(xs),
            })

        pre_lines = self._group_into_text_lines(pre_boxes)
        detected_layout = self.detect_document_layout(width, height, raw_results, pre_lines)

        # Determine target layout
        target_layout = detected_layout if mode == "auto" else mode
        is_quiz_layout = target_layout in ("quiz", "mobile_quiz")

        filtered_boxes = self.filter_and_cluster_boxes(
            raw_results, width, height, is_quiz_layout=is_quiz_layout
        )
        text_lines = self._group_into_text_lines(filtered_boxes)
        cur_page = page_num if page_num > 0 else 1

        if target_layout in ("quiz", "mobile_quiz"):
            items = self._parse_mobile_quiz(filtered_boxes, height, page_num, total_pages)
        elif target_layout in ("document_mcq", "mcq"):
            items = self._parse_document_mcq(text_lines, cur_page)
        elif target_layout in ("worksheet", "cloze"):
            items = self._parse_worksheet(text_lines, cur_page)
        else:
            items = self._parse_generic(text_lines, cur_page)

        return {
            "file": file_path,
            "filename": os.path.basename(file_path),
            "hash": file_hash,
            "page": page_num,
            "total_pages": total_pages,
            "layout_type": target_layout,
            "items": items,
            "status": "success",
            "width": width,
            "height": height,
        }

    def process_folder(
        self,
        folder_path: str,
        mode: str = "auto",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        image_files = self.get_image_files(folder_path)
        total_files = len(image_files)

        if total_files == 0:
            return {
                "folder": folder_path,
                "total_files": 0,
                "unique_files": 0,
                "duplicate_files": 0,
                "results": [],
                "duplicates": [],
            }

        # Read page numbers and hashes to order pages
        file_previews = []
        for idx, fpath in enumerate(image_files):
            if progress_callback:
                progress_callback(idx + 1, total_files * 2, f"Memeriksa indeks berkas: {os.path.basename(fpath)}")
            
            try:
                with Image.open(fpath) as img:
                    w, h = img.size
                    if w > MAX_IMAGE_DIMENSION or h > MAX_IMAGE_DIMENSION or (w * h) > MAX_TOTAL_PIXELS:
                        continue
                    bottom_crop = img.crop((0, int(h * 0.82), int(w * 0.6), h))
                    res_p, _ = self.ocr(bottom_crop)
                    p_text = " ".join([r[1] for r in res_p]) if res_p else ""
                    match = re.search(r"(\d+)\s*/\s*(\d+)", p_text)
                    detected_page = int(match.group(1)) if match else -1
                    total_detected = int(match.group(2)) if match else -1
            except Exception:
                detected_page = -1
                total_detected = -1

            try:
                fhash = self.calculate_file_hash(fpath)
            except Exception:
                fhash = ""

            file_previews.append({
                "path": fpath,
                "filename": os.path.basename(fpath),
                "page": detected_page,
                "total_pages": total_detected,
                "hash": fhash
            })

        def sort_key(item: Dict[str, Any]):
            if item["page"] > 0:
                return (0, item["page"])
            nums = re.findall(r"\d+", item["filename"])
            return (1, int(nums[-1]) if nums else item["filename"])

        file_previews.sort(key=sort_key)

        # Deduplicate files by content hash and page number
        seen_hashes = set()
        seen_pages = set()
        unique_list = []
        duplicate_list = []

        for item in file_previews:
            h = item["hash"]
            p = item["page"]
            if h in seen_hashes:
                duplicate_list.append({**item, "reason": "Hash berkas identik"})
            elif p > 0 and p in seen_pages:
                duplicate_list.append({**item, "reason": f"Halaman {p} sudah diproses"})
            else:
                seen_hashes.add(h)
                if p > 0:
                    seen_pages.add(p)
                unique_list.append(item)

        # Extract content from unique files
        processed_results = []
        for idx, item in enumerate(unique_list):
            step = total_files + idx + 1
            if progress_callback:
                progress_callback(step, total_files + len(unique_list), f"Mengekstrak teks: {item['filename']}")
            
            res = self.process_single_image(item["path"], mode=mode)
            if res["page"] <= 0 and item["page"] > 0:
                res["page"] = item["page"]
                res["total_pages"] = item["total_pages"]
            processed_results.append(res)

        return {
            "folder": folder_path,
            "total_files": total_files,
            "unique_files": len(unique_list),
            "duplicate_files": len(duplicate_list),
            "results": processed_results,
            "duplicates": duplicate_list,
            "device_used": "GPU" if self.use_gpu else "CPU"
        }
