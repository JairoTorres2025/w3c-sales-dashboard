#!/usr/bin/env python3
# Build Wolf Reps PDF from Markdown using ReportLab (clickable external links)

from __future__ import annotations
import os
import re
from typing import List
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, ListFlowable, ListItem

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
MD_PATH = os.path.join(DOCS_DIR, 'WolfReps-Guide.md')
PDF_PATH = os.path.join(DOCS_DIR, 'WolfReps-Guide.pdf')

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def ensure_dirs():
    os.makedirs(DOCS_DIR, exist_ok=True)


def md_link_to_html(text: str) -> str:
    # Convert [text](url) to <a href="url">text</a>
    def repl(m):
        label = m.group(1)
        url = m.group(2)
        return f'<a href="{url}">{label}</a>'
    return LINK_RE.sub(repl, text)


def parse_markdown(md_text: str) -> List:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        'Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=10.5, leading=14, spaceAfter=6
    )
    h1 = ParagraphStyle('Heading1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, spaceAfter=10, textColor=colors.HexColor('#0b3d91'))
    h2 = ParagraphStyle('Heading2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, leading=18, spaceAfter=8, textColor=colors.HexColor('#0b3d91'))
    h3 = ParagraphStyle('Heading3', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=12, leading=16, spaceAfter=6, textColor=colors.HexColor('#0b3d91'))
    bullet = ParagraphStyle('Bullet', parent=body, leftIndent=14, bulletIndent=6)

    flows: List = []

    lines = md_text.splitlines()

    # Optional top image: parse first image on the first non-empty line
    idx = 0
    while idx < len(lines) and lines[idx].strip() == '':
        idx += 1
    if idx < len(lines):
        m = IMG_RE.search(lines[idx])
        if m:
            img_path = m.group(1).strip()
            # strip optional angle brackets
            if img_path.startswith('<') and img_path.endswith('>'):
                img_path = img_path[1:-1]
            if os.path.exists(img_path):
                try:
                    flows.append(RLImage(img_path, width=180, height=60, hAlign='LEFT'))
                    flows.append(Spacer(1, 10))
                except Exception:
                    pass
            # remove image line so it doesn't show as text
            lines[idx] = ''

    # Parse remaining
    i = 0
    pending_bullets: List[str] = []
    para_buf: List[str] = []

    def flush_paragraph():
        nonlocal para_buf
        if para_buf:
            text = '\n'.join(para_buf).strip()
            if text:
                text = md_link_to_html(text)
                flows.append(Paragraph(text, body))
            para_buf = []

    def flush_bullets():
        nonlocal pending_bullets
        if pending_bullets:
            items = []
            for raw in pending_bullets:
                txt = md_link_to_html(raw)
                items.append(ListItem(Paragraph(txt, body), leftIndent=0))
            flows.append(ListFlowable(items, bulletType='bullet', start=None, leftIndent=10, bulletFontName='Helvetica', bulletFontSize=10))
            pending_bullets = []

    while i < len(lines):
        line = lines[i]
        s = line.rstrip()
        if s.strip() == '':
            flush_paragraph(); flush_bullets(); flows.append(Spacer(1, 4)); i += 1; continue
        if s.startswith('---') and set(s.strip()) == {'-'}:
            flush_paragraph(); flush_bullets(); flows.append(Spacer(1, 8)); i += 1; continue
        if s.startswith('# '):
            flush_paragraph(); flush_bullets(); flows.append(Paragraph(s[2:].strip(), h1)); i += 1; continue
        if s.startswith('## '):
            flush_paragraph(); flush_bullets(); flows.append(Paragraph(s[3:].strip(), h2)); i += 1; continue
        if s.startswith('### '):
            flush_paragraph(); flush_bullets(); flows.append(Paragraph(s[4:].strip(), h3)); i += 1; continue
        if s.lstrip().startswith('- '):
            flush_paragraph()
            # capture consecutive bullet lines
            bullet_text = s.lstrip()[2:].strip()
            pending_bullets.append(bullet_text)
            i += 1
            # if next lines keep bullets, let loop continue; flush happens on block end
            # continue without flushing here
            # but if it's the last line, flush after loop
            if i >= len(lines):
                flush_bullets()
            continue
        # normal paragraph line
        para_buf.append(s)
        i += 1

    flush_paragraph(); flush_bullets()
    return flows


def build_pdf():
    ensure_dirs()
    if not os.path.exists(MD_PATH):
        raise FileNotFoundError(f"Markdown guide not found: {MD_PATH}")
    # delete previous
    try:
        if os.path.exists(PDF_PATH):
            os.remove(PDF_PATH)
    except Exception:
        pass

    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md = f.read()

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=LETTER,
        leftMargin=48,
        rightMargin=48,
        topMargin=54,
        bottomMargin=48,
        title='W3C Sales Dashboard — Wolf Reps Guide',
        author='Wolf Carports',
        subject='Dashboard user guide',
        creator='W3C',
    )

    flows = parse_markdown(md)
    doc.build(flows)


if __name__ == '__main__':
    build_pdf()
