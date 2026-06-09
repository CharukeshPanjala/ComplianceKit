# WHAT: ROPA PDF generator | CHANGE: new file | WHY: COM-173 — generate Art. 30 register as PDF
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from common.models.ropa import RopaEntry


# ── Colours ───────────────────────────────────────────────────────────────────

NAVY = colors.HexColor("#0F2044")
AMBER = colors.HexColor("#F59E0B")
LIGHT_GRAY = colors.HexColor("#F9FAFB")
MID_GRAY = colors.HexColor("#E5E7EB")
TEXT_GRAY = colors.HexColor("#374151")


# ── Styles ────────────────────────────────────────────────────────────────────

def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontSize=18, textColor=NAVY, spaceAfter=4, fontName="Helvetica-Bold"),
        "subtitle": ParagraphStyle("subtitle", fontSize=10, textColor=TEXT_GRAY, spaceAfter=2),
        "cell": ParagraphStyle("cell", fontSize=7, textColor=TEXT_GRAY, leading=10),
        "cell_bold": ParagraphStyle("cell_bold", fontSize=7, textColor=NAVY, leading=10, fontName="Helvetica-Bold"),
        "badge_active": ParagraphStyle("badge_active", fontSize=7, textColor=colors.HexColor("#065F46"), leading=10),
        "badge_draft": ParagraphStyle("badge_draft", fontSize=7, textColor=colors.HexColor("#92400E"), leading=10),
    }


# ── Entry helpers ─────────────────────────────────────────────────────────────

def _legal_basis_label(value: str | None) -> str:
    labels = {
        "consent": "Consent (Art. 6(1)(a))",
        "contract": "Contract (Art. 6(1)(b))",
        "legal_obligation": "Legal Obligation (Art. 6(1)(c))",
        "vital_interests": "Vital Interests (Art. 6(1)(d))",
        "public_task": "Public Task (Art. 6(1)(e))",
        "legitimate_interests": "Legitimate Interests (Art. 6(1)(f))",
    }
    return labels.get(value or "", value or "—")


def _fmt_list(items: list | None) -> str:
    if not items:
        return "—"
    return ", ".join(str(i) for i in items[:5]) + ("…" if len(items) > 5 else "")


def _fmt_bool(val: bool) -> str:
    return "Yes" if val else "No"


# ── Main export function ──────────────────────────────────────────────────────

def generate_ropa_pdf(entries: list[RopaEntry], company_name: str = "") -> bytes:
    buffer = io.BytesIO()
    s = _styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    elements = []

    # ── Header ────────────────────────────────────────────────────────────────
    name_line = f" — {company_name}" if company_name else ""
    elements.append(Paragraph(f"Records of Processing Activities{name_line}", s["title"]))
    elements.append(Paragraph(f"GDPR Article 30 Register  ·  Generated {date.today().strftime('%d %B %Y')}  ·  {len(entries)} activities", s["subtitle"]))
    elements.append(Spacer(1, 6 * mm))

    if not entries:
        elements.append(Paragraph("No ROPA entries found.", s["cell"]))
        doc.build(elements)
        return buffer.getvalue()

    # ── Table ─────────────────────────────────────────────────────────────────
    headers = [
        Paragraph("Activity", s["cell_bold"]),
        Paragraph("Legal Basis", s["cell_bold"]),
        Paragraph("Data Categories", s["cell_bold"]),
        Paragraph("Data Subjects", s["cell_bold"]),
        Paragraph("Locations", s["cell_bold"]),
        Paragraph("Transfers", s["cell_bold"]),
        Paragraph("Retention", s["cell_bold"]),
        Paragraph("DPIA", s["cell_bold"]),
        Paragraph("Status", s["cell_bold"]),
    ]

    rows = [headers]
    for e in entries:
        status_style = s["badge_active"] if (e.status and e.status.value == "active") else s["badge_draft"]
        rows.append([
            Paragraph(e.activity_name or "—", s["cell"]),
            Paragraph(_legal_basis_label(e.legal_basis.value if e.legal_basis else None), s["cell"]),
            Paragraph(_fmt_list(e.data_categories), s["cell"]),
            Paragraph(_fmt_list(e.data_subject_categories), s["cell"]),
            Paragraph(_fmt_list(e.processing_locations), s["cell"]),
            Paragraph("Yes" if e.third_party_transfers else "No", s["cell"]),
            Paragraph(e.retention_period or "—", s["cell"]),
            Paragraph(_fmt_bool(e.requires_dpia), s["cell"]),
            Paragraph(e.status.value.title() if e.status else "—", status_style),
        ])

    col_widths = [60*mm, 42*mm, 38*mm, 35*mm, 30*mm, 20*mm, 25*mm, 14*mm, 18*mm]

    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 1, AMBER),
    ]))

    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()
