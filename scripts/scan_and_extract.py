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
import os
import re
import sys
from pathlib import Path
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

# Add src to sys.path for standalone script execution
src_dir = Path(__file__).resolve().parents[1] / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from cocr.engine import load_watermark_patterns

def main():
    ocr = RapidOCR(use_cls=False)
    files = sorted(glob.glob('*.jpeg'))
    print(f"Total JPEG files found: {len(files)}")

    file_info = []
    for f in files:
        with open(f, 'rb') as fp:
            h = hashlib.md5(fp.read()).hexdigest()
        img = Image.open(f)
        w, h_img = img.size
        # Detect page number from footer region
        crop_page = img.crop((0, int(h_img * 0.85), int(w * 0.5), h_img))
        res, _ = ocr(crop_page)
        text = ' '.join([r[1] for r in res]) if res else ''
        match = re.search(r'(\d+)\s*/\s*135', text)
        p = int(match.group(1)) if match else -1
        file_info.append({'file': f, 'page': p, 'hash': h})

    file_info.sort(key=lambda x: x['page'])

    seen_pages = set()
    unique_files = []
    duplicate_files = []

    for item in file_info:
        p = item['page']
        if p in seen_pages:
            duplicate_files.append(item)
        else:
            seen_pages.add(p)
            unique_files.append(item)

    print(f"Unique files: {len(unique_files)}")
    print(f"Duplicate files count: {len(duplicate_files)}")
    for d in duplicate_files:
        print(f"  Duplicate: {d['file']} (matches page {d['page']})")

    def clean_lines(lines):
        cleaned = []
        wm_patterns = load_watermark_patterns()
        for l in lines:
            t = l.strip()
            if any(re.search(pat, t, re.IGNORECASE) for pat in wm_patterns):
                continue
            if len(t) <= 2 and not t.isdigit() and t not in ['A.', 'B.', 'C.', 'D.', '1.', '2.', '3.', '4.', '1)', '2)', '3)', '4)']:
                continue
            cleaned.append(t)
        return cleaned

    extracted_data = {}
    all_md_sections = []

    for idx, item in enumerate(unique_files):
        f = item['file']
        p = item['page']
        img = Image.open(f)
        
        # Top card
        c1 = img.crop((120, 160, 660, 750))
        res1, _ = ocr(c1)
        l1 = clean_lines([r[1] for r in res1] if res1 else [])
        
        # Bottom card
        l2 = []
        if p < 135:
            c2 = img.crop((120, 880, 660, 1260))
            res2, _ = ocr(c2)
            l2 = clean_lines([r[1] for r in res2] if res2 else [])
        
        sec_md = f"### File: `{f}` (Pages {p}" + (f" & {p+1}" if p < 135 else "") + ")\n\n"
        sec_md += f"#### Page {p}\n" + '\n'.join(l1) + "\n\n"
        if l2:
            sec_md += f"#### Page {p+1}\n" + '\n'.join(l2) + "\n\n"
        
        all_md_sections.append(sec_md)
        extracted_data[f] = {
            'status': 'extracted',
            'page_start': p,
            'page_end': p + 1 if p < 135 else p,
            'text_card1': l1,
            'text_card2': l2
        }
        if (idx + 1) % 15 == 0 or idx == len(unique_files) - 1:
            print(f"Processed {idx + 1}/{len(unique_files)} images...")

    for d in duplicate_files:
        extracted_data[d['file']] = {
            'status': 'skipped_duplicate',
            'duplicate_of_page': d['page'],
            'reason': 'Duplicate screenshot of existing page'
        }

    # Save tracker
    with open('extracted_tracker.json', 'w', encoding='utf-8') as jf:
        json.dump({'total_files': len(files), 'unique_count': len(unique_files), 'duplicate_count': len(duplicate_files), 'extracted_files': extracted_data}, jf, indent=2, ensure_ascii=False)

    # Save file list
    with open('extracted_files.txt', 'w', encoding='utf-8') as tf:
        tf.write("# Extracted files (Unique):\n")
        for u in unique_files:
            tf.write(f"{u['file']} (Page {u['page']})\n")
        tf.write("\n# Duplicate files (Skipped):\n")
        for d in duplicate_files:
            tf.write(f"{d['file']} (Duplicate of Page {d['page']})\n")

    # Save full markdown document
    with open('extracted_document.md', 'w', encoding='utf-8') as mf:
        mf.write("# Extracted Documents\n\n")
        mf.write('\n'.join(all_md_sections))

    print("Scan and extraction completed successfully!")

if __name__ == '__main__':
    main()
