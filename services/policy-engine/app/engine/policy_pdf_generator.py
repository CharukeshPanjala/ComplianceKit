# WHAT: Policy PDF generator | CHANGE: new file | WHY: COM-176 — render a policy's Markdown content as a branded PDF for download

import io
from datetime import date
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from common.models.policy import Policy

from app.engine.markdown_blocks import (
    parse_markdown,
    Span,
    Heading as MdHeading,
    Paragraph as MdParagraph,
    ListItem as MdListItem,
    Table as MdTable,
)


# ── Colours ───────────────────────────────────────────────────────────────────

NAVY = colors.HexColor("#0F2044")
AMBER = colors.HexColor("#F59E0B")
LIGHT_GRAY = colors.HexColor("#F9FAFB")
MID_GRAY = colors.HexColor("#E5E7EB")
TEXT_GRAY = colors.HexColor("#374151")


# ── Styles ────────────────────────────────────────────────────────────────────

def _styles() -> dict[str, ParagraphStyle]:
    return {
        "title": ParagraphStyle("title", fontSize=18, textColor=NAVY, spaceAfter=4, fontName="Helvetica-Bold"),
        "subtitle": ParagraphStyle("subtitle", fontSize=9, textColor=TEXT_GRAY, spaceAfter=2),
        "h1": ParagraphStyle("h1", fontSize=15, textColor=NAVY, spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"),
        "h2": ParagraphStyle("h2", fontSize=12, textColor=NAVY, spaceBefore=10, spaceAfter=5, fontName="Helvetica-Bold"),
        "h3": ParagraphStyle("h3", fontSize=10.5, textColor=NAVY, spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold"),
        "body": ParagraphStyle("body", fontSize=9.5, textColor=TEXT_GRAY, leading=14, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", fontSize=9.5, textColor=TEXT_GRAY, leading=14, leftIndent=12, spaceAfter=2),
        "cell": ParagraphStyle("cell", fontSize=8, textColor=TEXT_GRAY, leading=11),
        "cell_bold": ParagraphStyle("cell_bold", fontSize=8, textColor=colors.white, leading=11, fontName="Helvetica-Bold"),
    }


# ── Inline span rendering ─────────────────────────────────────────────────────

def _spans_to_html(spans: list[Span]) -> str:
    parts = []
    for sp in spans:
        text = escape(sp.text)
        if sp.bold and sp.italic:
            text = f"<b><i>{text}</i></b>"
        elif sp.bold:
            text = f"<b>{text}</b>"
        elif sp.italic:
            text = f"<i>{text}</i>"
        parts.append(text)
    return "".join(parts)


# ── Table rendering ───────────────────────────────────────────────────────────

def _render_table(block: MdTable, s: dict[str, ParagraphStyle]) -> Table:
    header_row = [Paragraph(_spans_to_html(cell), s["cell_bold"]) for cell in block.headers]
    rows: list[list[Paragraph]] = [header_row]
    for row in block.rows:
        rows.append([Paragraph(_spans_to_html(cell), s["cell"]) for cell in row])

    num_cols = len(block.headers) or 1
    available_width = A4[0] - 40 * mm
    col_width = available_width / num_cols

    table = Table(rows, colWidths=[col_width] * num_cols, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 1, AMBER),
    ]))
    return table


# ── Generic markdown renderer ─────────────────────────────────────────────────

def render_markdown_pdf(title: str, subtitle: str, content: str) -> bytes:
    """Render a title, subtitle and Markdown body as a branded PDF."""
    buffer = io.BytesIO()
    s = _styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    elements = []
    elements.append(Paragraph(escape(title), s["title"]))
    elements.append(Paragraph(escape(subtitle), s["subtitle"]))
    elements.append(Spacer(1, 6 * mm))

    blocks = parse_markdown(content or "")
    skipped_h1 = False
    ordered_counter = 0

    for block in blocks:
        if not isinstance(block, MdListItem) or not block.ordered:
            ordered_counter = 0

        if isinstance(block, MdHeading):
            if block.level == 1 and not skipped_h1:
                skipped_h1 = True
                continue
            style = {1: s["h1"], 2: s["h2"], 3: s["h3"]}.get(block.level, s["h3"])
            elements.append(Paragraph(_spans_to_html(block.spans), style))
        elif isinstance(block, MdParagraph):
            elements.append(Paragraph(_spans_to_html(block.spans), s["body"]))
        elif isinstance(block, MdListItem):
            if block.ordered:
                ordered_counter += 1
                bullet = f"{ordered_counter}."
            else:
                bullet = "•"
            elements.append(Paragraph(f"{bullet} {_spans_to_html(block.spans)}", s["bullet"]))
        elif isinstance(block, MdTable):
            elements.append(_render_table(block, s))
            elements.append(Spacer(1, 4 * mm))

    if not blocks:
        elements.append(Paragraph("This document has no content yet.", s["body"]))

    doc.build(elements)
    return buffer.getvalue()


# ── Main export function ──────────────────────────────────────────────────────

def generate_policy_pdf(policy: Policy) -> bytes:
    status_label = policy.status.value.replace("_", " ").title() if policy.status else "Draft"
    title = policy.title or "Policy"
    if policy.tenant_name:
        title = f"{title} — {policy.tenant_name}"
    subtitle = (
        f"Generated {date.today().strftime('%d %B %Y')}  ·  "
        f"Version {policy.current_version}  ·  {status_label}"
    )
    return render_markdown_pdf(title, subtitle, policy.content or "")
