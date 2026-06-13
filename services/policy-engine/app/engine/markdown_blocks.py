# WHAT: Markdown parser for policy documents | CHANGE: new file | WHY: COM-176 — converts policy Markdown content into a neutral block list shared by the PDF and DOCX exporters

from __future__ import annotations

import re
from dataclasses import dataclass


# ── Inline spans ──────────────────────────────────────────────────────────────

@dataclass
class Span:
    text: str
    bold: bool = False
    italic: bool = False


_INLINE_RE = re.compile(
    r"\*\*\*(?P<bolditalic>.+?)\*\*\*"
    r"|\*\*(?P<bold>.+?)\*\*"
    r"|__(?P<bold2>.+?)__"
    r"|\*(?P<italic>.+?)\*"
    r"|_(?P<italic2>.+?)_"
)


def parse_inline(text: str) -> list[Span]:
    spans: list[Span] = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            spans.append(Span(text[pos:m.start()]))
        if m.group("bolditalic") is not None:
            spans.append(Span(m.group("bolditalic"), bold=True, italic=True))
        elif m.group("bold") is not None:
            spans.append(Span(m.group("bold"), bold=True))
        elif m.group("bold2") is not None:
            spans.append(Span(m.group("bold2"), bold=True))
        elif m.group("italic") is not None:
            spans.append(Span(m.group("italic"), italic=True))
        elif m.group("italic2") is not None:
            spans.append(Span(m.group("italic2"), italic=True))
        pos = m.end()
    if pos < len(text):
        spans.append(Span(text[pos:]))
    return spans or [Span(text)]


# ── Block types ───────────────────────────────────────────────────────────────

@dataclass
class Heading:
    level: int
    spans: list[Span]


@dataclass
class Paragraph:
    spans: list[Span]


@dataclass
class ListItem:
    spans: list[Span]
    ordered: bool


@dataclass
class Table:
    headers: list[list[Span]]
    rows: list[list[list[Span]]]


Block = Heading | Paragraph | ListItem | Table


# ── Block parser ──────────────────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
_ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$")


def parse_markdown(content: str) -> list[Block]:
    """Parse policy Markdown into headings, paragraphs, list items and tables."""
    lines = content.replace("\r\n", "\n").split("\n")
    blocks: list[Block] = []
    i, n = 0, len(lines)

    while i < n:
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            blocks.append(Heading(level=level, spans=parse_inline(heading_match.group(2).strip())))
            i += 1
            continue

        bullet_match = _BULLET_RE.match(line)
        if bullet_match:
            blocks.append(ListItem(spans=parse_inline(bullet_match.group(1).strip()), ordered=False))
            i += 1
            continue

        ordered_match = _ORDERED_RE.match(line)
        if ordered_match:
            blocks.append(ListItem(spans=parse_inline(ordered_match.group(1).strip()), ordered=True))
            i += 1
            continue

        if "|" in line and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1].strip()):
            headers = [parse_inline(c) for c in _split_table_row(line)]
            i += 2
            rows: list[list[list[Span]]] = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([parse_inline(c) for c in _split_table_row(lines[i])])
                i += 1
            blocks.append(Table(headers=headers, rows=rows))
            continue

        para_lines = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not _is_block_start(lines[i]):
            para_lines.append(lines[i].strip())
            i += 1
        blocks.append(Paragraph(spans=parse_inline(" ".join(para_lines))))

    return blocks


def _is_block_start(line: str) -> bool:
    stripped = line.strip()
    return bool(
        _HEADING_RE.match(stripped)
        or _BULLET_RE.match(stripped)
        or _ORDERED_RE.match(stripped)
        or "|" in stripped
    )


def _split_table_row(line: str) -> list[str]:
    cells = line.strip()
    if cells.startswith("|"):
        cells = cells[1:]
    if cells.endswith("|"):
        cells = cells[:-1]
    return [c.strip() for c in cells.split("|")]
