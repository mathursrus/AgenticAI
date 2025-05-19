"""
docx2markdown_custom: Convert .docx files to Markdown, preserving headings, paragraphs, and tables.
"""

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from io import BytesIO
from typing import List

__all__ = ["docx_to_markdown_custom"]

def docx_to_markdown_custom(docx_bytes: bytes) -> str:
    """
    Convert a .docx file (as bytes) to Markdown, preserving headings, paragraphs, and tables.
    Args:
        docx_bytes (bytes): The binary content of a .docx file.
    Returns:
        str: The Markdown representation of the document.
    """
    document = Document(BytesIO(docx_bytes))
    markdown_lines: List[str] = []

    def convert_paragraph(para: Paragraph) -> str:
        style = para.style.name.lower()
        text = ""
        for run in para.runs:
            run_text = run.text.replace("\n", " ")
            if run.bold:
                run_text = f"**{run_text}**"
            if run.italic:
                run_text = f"*{run_text}*"
            text += run_text

        if not text.strip():
            return ""

        if style.startswith('heading'):
            level = style.replace("heading", "").strip()
            try:
                level = int(level)
                return f"{'#' * level} {text.strip()}"
            except ValueError:
                pass  # Unknown heading level fallback

        return text.strip()

    def convert_table(table: Table) -> str:
        rows = table.rows
        if not rows:
            return ""

        md = []
        headers = [cell.text.strip().replace("\n", " ") for cell in rows[0].cells]
        md.append("| " + " | ".join(headers) + " |")
        md.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in rows[1:]:
            values = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            md.append("| " + " | ".join(values) + " |")

        return "\n".join(md)

    # Walk through the document body elements in order
    for element in document.element.body:
        if element.tag.endswith("p"):
            para = Paragraph(element, document)
            md_para = convert_paragraph(para)
            if md_para:
                markdown_lines.append(md_para)

        elif element.tag.endswith("tbl"):
            table = next(tbl for tbl in document.tables if tbl._element == element)
            markdown_lines.append(convert_table(table))

    return "\n\n".join(markdown_lines) 