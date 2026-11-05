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

import html
import os
from datetime import datetime
from typing import Any, Dict, List

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#57606a"))
        
        self.setStrokeColor(colors.HexColor("#d0d7de"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 28 * cm, 19 * cm, 28 * cm)
        self.drawString(2 * cm, 28.2 * cm, "Hasil Ekstraksi Dokumen - cOCR Workbench")

        self.line(2 * cm, 1.8 * cm, 19 * cm, 1.8 * cm)
        page_text = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(19 * cm, 1.3 * cm, page_text)
        self.restoreState()


class Exporters:
    @staticmethod
    def to_markdown(data: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        lines: List[str] = []

        lines.append("# Hasil Ekstraksi Dokumen")
        lines.append("")
        lines.append(f"Waktu Ekstraksi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Berkas: {data.get('total_files', 0)} (Unik: {data.get('unique_files', 0)}, Duplikat: {data.get('duplicate_files', 0)})")
        lines.append(f"Perangkat OCR: {data.get('device_used', 'CPU')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        item_counter = 1
        for res in data.get("results", []):
            filename = res.get("filename", "")
            page = res.get("page", -1)
            items = res.get("items", [])

            lines.append(f"## Berkas: `{filename}`")
            if page > 0:
                lines.append(f"*Halaman Terdeteksi: {page}*")
            lines.append("")

            current_section = None
            for item in items:
                card_idx = item.get("card_index", 1)
                page_num = item.get("page_number", page)
                q_text = item.get("question", "").strip()
                options = item.get("options", [])
                section = item.get("section")
                instruction = item.get("instruction")

                if section and section != current_section:
                    current_section = section
                    lines.append(f"### Bagian: {section}")
                    if instruction:
                        lines.append(f"*{instruction}*")
                    lines.append("")

                num_label = f"Butir {item_counter}"
                if item.get("number"):
                    num_label += f" [Asli: No. {item.get('number')}]"
                lines.append(f"#### {num_label} (Halaman {page_num})")
                lines.append("")
                if q_text:
                    if options:
                        lines.append("**Butir Pertanyaan:**")
                    else:
                        lines.append("**Konten Teks:**")
                    lines.append(f"> {q_text}")
                    lines.append("")

                if options:
                    lines.append("**Pilihan Jawaban:**")
                    for opt in options:
                        lines.append(f"- {opt}")
                    lines.append("")
                elif not q_text:
                    lines.append("*Teks tidak terdeteksi.*")
                    lines.append("")

                lines.append("---")
                lines.append("")
                item_counter += 1

        content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    @staticmethod
    def to_docx(data: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc = docx.Document()

        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        style_normal = doc.styles["Normal"]
        font = style_normal.font
        font.name = "Calibri"
        font.size = Pt(11)
        font.color.rgb = RGBColor(0x24, 0x29, 0x2F)

        title_p = doc.add_paragraph()
        title_run = title_p.add_run("Hasil Ekstraksi Dokumen")
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        title_p.paragraph_format.space_after = Pt(4)

        sub_p = doc.add_paragraph()
        sub_text = (
            f"Waktu Ekstraksi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Total Berkas: {data.get('total_files', 0)} | "
            f"Perangkat: {data.get('device_used', 'CPU')}"
        )
        sub_run = sub_p.add_run(sub_text)
        sub_run.font.size = Pt(9.5)
        sub_run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        sub_p.paragraph_format.space_after = Pt(16)

        hr_table = doc.add_table(rows=1, cols=1)
        hr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = hr_table.cell(0, 0)
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E2E8F0"/>')
        tcPr.append(shd)
        cell.width = Inches(6.8)
        cell.paragraphs[0].paragraph_format.space_before = Pt(0)
        cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        
        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        item_counter = 1
        for res in data.get("results", []):
            filename = res.get("filename", "")
            page = res.get("page", -1)
            items = res.get("items", [])

            file_h = doc.add_paragraph()
            file_run = file_h.add_run(f"Berkas: {filename}")
            file_run.font.size = Pt(13)
            file_run.font.bold = True
            file_run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            file_h.paragraph_format.space_before = Pt(14)
            file_h.paragraph_format.space_after = Pt(6)

            current_section = None
            for item in items:
                page_num = item.get("page_number", page)
                q_text = item.get("question", "").strip()
                options = item.get("options", [])
                section = item.get("section")
                instruction = item.get("instruction")

                if section and section != current_section:
                    current_section = section
                    sec_p = doc.add_paragraph()
                    sec_run = sec_p.add_run(f"Bagian: {section}")
                    sec_run.font.size = Pt(12)
                    sec_run.font.bold = True
                    sec_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
                    sec_p.paragraph_format.space_before = Pt(12)
                    sec_p.paragraph_format.space_after = Pt(2)
                    if instruction:
                        instr_p = doc.add_paragraph()
                        instr_run = instr_p.add_run(instruction)
                        instr_run.font.italic = True
                        instr_run.font.size = Pt(9.5)
                        instr_run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
                        instr_p.paragraph_format.space_after = Pt(6)

                # Question box with left accent border
                q_table = doc.add_table(rows=1, cols=1)
                q_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                q_cell = q_table.cell(0, 0)
                q_cell.width = Inches(6.8)

                cell_tcPr = q_cell._tc.get_or_add_tcPr()
                cell_shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
                cell_tcPr.append(cell_shd)

                tcBorders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="none"/>'
                    f'<w:left w:val="single" w:sz="24" w:space="0" w:color="3B82F6"/>'
                    f'<w:bottom w:val="none"/>'
                    f'<w:right w:val="none"/>'
                    f'</w:tcBorders>'
                )
                cell_tcPr.append(tcBorders)

                cp = q_cell.paragraphs[0]
                cp.paragraph_format.space_before = Pt(4)
                cp.paragraph_format.space_after = Pt(4)
                cp.paragraph_format.left_indent = Inches(0.1)

                num_run = cp.add_run(f"Butir {item_counter} (Halaman {page_num})\n")
                num_run.font.bold = True
                num_run.font.size = Pt(10.5)
                num_run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

                body_run = cp.add_run(q_text if q_text else "Teks tidak terdeteksi.")
                body_run.font.size = Pt(10.5)

                if options:
                    opt_title = doc.add_paragraph()
                    opt_title.paragraph_format.space_before = Pt(8)
                    opt_title.paragraph_format.space_after = Pt(4)
                    ot_run = opt_title.add_run("Pilihan Jawaban:")
                    ot_run.font.bold = True
                    ot_run.font.size = Pt(10)
                    ot_run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

                    for opt in options:
                        opt_p = doc.add_paragraph(style="List Bullet")
                        opt_p.paragraph_format.space_before = Pt(2)
                        opt_p.paragraph_format.space_after = Pt(2)
                        opt_p.paragraph_format.left_indent = Inches(0.3)
                        opt_run = opt_p.add_run(opt)
                        opt_run.font.size = Pt(10)

                doc.add_paragraph().paragraph_format.space_after = Pt(8)
                item_counter += 1

        doc.save(output_path)
        return output_path

    @staticmethod
    def to_pdf(data: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.2 * cm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )

        meta_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        )

        file_header_style = ParagraphStyle(
            "FileHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
        )

        question_title_style = ParagraphStyle(
            "QuestionTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1e40af"),
            spaceAfter=3,
        )

        question_body_style = ParagraphStyle(
            "QuestionBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#1e293b"),
            alignment=TA_JUSTIFY,
        )

        option_style = ParagraphStyle(
            "OptionItem",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#334155"),
            leftIndent=14,
            spaceBefore=2,
            spaceAfter=2,
        )

        section_header_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=2,
        )

        instruction_style = ParagraphStyle(
            "InstructionMeta",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=5,
        )

        story = []

        story.append(Paragraph("Hasil Ekstraksi Dokumen", title_style))
        meta_str = (
            f"Waktu Ekstraksi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Total Berkas: {data.get('total_files', 0)} (Unik: {data.get('unique_files', 0)}) | "
            f"Perangkat: {data.get('device_used', 'CPU')}"
        )
        story.append(Paragraph(html.escape(meta_str), meta_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        item_counter = 1
        for res in data.get("results", []):
            filename = res.get("filename", "")
            page = res.get("page", -1)
            items = res.get("items", [])

            safe_filename = html.escape(str(filename))
            story.append(Paragraph(f"Berkas: {safe_filename}", file_header_style))

            current_section = None
            for item in items:
                page_num = item.get("page_number", page)
                q_text = item.get("question", "").strip()
                options = item.get("options", [])
                section = item.get("section")
                instruction = item.get("instruction")

                if section and section != current_section:
                    current_section = section
                    story.append(Paragraph(f"Bagian: {html.escape(section)}", section_header_style))
                    if instruction:
                        story.append(Paragraph(html.escape(instruction), instruction_style))

                card_flowables = []

                # Escape XML entities to protect ReportLab parser
                safe_q_text = html.escape(q_text) if q_text else "Teks tidak terdeteksi."
                q_cell_content = [
                    Paragraph(f"Butir {item_counter} (Halaman {page_num})", question_title_style),
                    Spacer(1, 2),
                    Paragraph(safe_q_text, question_body_style),
                ]
                
                table_card = Table(
                    [[q_cell_content]],
                    colWidths=[17 * cm],
                )
                table_card.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("LINEBEFORE", (0, 0), (0, -1), 2.5, colors.HexColor("#3b82f6")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]))

                card_flowables.append(table_card)
                card_flowables.append(Spacer(1, 4))

                if options:
                    for opt in options:
                        safe_opt = html.escape(str(opt))
                        card_flowables.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_opt}", option_style))
                    card_flowables.append(Spacer(1, 6))

                card_flowables.append(Spacer(1, 6))
                story.append(KeepTogether(card_flowables))
                item_counter += 1

        doc.build(story, canvasmaker=NumberedCanvas)
        return output_path
