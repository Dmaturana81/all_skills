#!/usr/bin/env python3
"""Vuelca un Markdown en el templado Word de VERT Analytics.

Conserva portada (si corresponde), encabezado, pie, márgenes y estilos.
Los títulos del Markdown se aplican como heading 1 … heading 9 del templado.
"""

from __future__ import annotations

import argparse
import random
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union
from urllib.parse import unquote

from docx import Document
from docx.document import Document as DocumentObject
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import CONTENT_TYPE as CT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.parts.numbering import NumberingPart
from docx.shared import Emu, Pt, RGBColor, Twips
from docx.table import Table
from docx.text.paragraph import Paragraph
from lxml import etree
from PIL import Image as PILImage

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
ACCENT = "0F4761"
CAPTION = RGBColor(0x59, 0x59, 0x59)
CONTENT_WIDTH_TWIPS = 9071  # A4 11906 − margen izq. 1701 − margen der. 1134
CONTENT_WIDTH = Twips(CONTENT_WIDTH_TWIPS)

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"

HEADING_NAMES = {
    1: ("heading 1", "título 1"),
    2: ("heading 2", "título 2"),
    3: ("heading 3", "título 3"),
    4: ("heading 4", "título 4"),
    5: ("heading 5", "título 5"),
    6: ("heading 6", "título 6"),
    7: ("heading 7", "título 7"),
    8: ("heading 8", "título 8"),
    9: ("heading 9", "título 9"),
}

TOKEN_RE = re.compile(
    r"\*\*\*(?P<bi>[^*]+)\*\*\*"
    r"|\*\*(?P<b>[^*]+)\*\*"
    r"|\*(?P<i>[^*]+)\*"
    r"|`(?P<code>[^`]+)`"
    r"|\[(?P<lt>[^\]]+)\]\((?P<lu>[^)\s]+)\)"
    r"|!\[(?P<ia>[^\]]*)\]\((?P<is>[^)\s]+)\)"
)
HEADING_RE = re.compile(r"^(#{1,9})\s+(.*?)\s*#*\s*$")
OL_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
UL_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
HR_RE = re.compile(r"^(\*\s*){3,}$|^-{3,}$|^_{3,}$")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)$")
FENCE_RE = re.compile(r"^```")


@dataclass
class Heading:
    level: int
    text: str


@dataclass
class Para:
    text: str


@dataclass
class ListBlock:
    ordered: bool
    items: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class TableBlock:
    rows: list[list[str]]
    header: bool


@dataclass
class ImageBlock:
    alt: str
    src: str


@dataclass
class CodeBlock:
    text: str


Block = Union[Heading, Para, ListBlock, TableBlock, ImageBlock, CodeBlock]


def parse_markdown(text: str) -> list[Block]:
    """Convierte Markdown en bloques. Las reglas horizontales se omiten."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: list[Block] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if HR_RE.match(stripped):
            index += 1
            continue
        if FENCE_RE.match(stripped):
            index += 1
            body: list[str] = []
            while index < len(lines) and not FENCE_RE.match(lines[index].strip()):
                body.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            blocks.append(CodeBlock("\n".join(body)))
            continue
        heading = HEADING_RE.match(stripped)
        if heading and not line.startswith(" "):
            blocks.append(Heading(len(heading.group(1)), heading.group(2).strip()))
            index += 1
            continue
        image = IMAGE_RE.match(stripped)
        if image:
            blocks.append(ImageBlock(image.group(1).strip(), image.group(2).strip()))
            index += 1
            continue
        if stripped.startswith("|"):
            table, index = _read_table(lines, index)
            blocks.append(table)
            continue
        if OL_RE.match(line) or UL_RE.match(line):
            listing, index = _read_list(lines, index)
            blocks.append(listing)
            continue
        if stripped.startswith(">"):
            quote, index = _read_quote(lines, index)
            blocks.append(quote)
            continue
        paragraph, index = _read_paragraph(lines, index)
        if paragraph.text:
            blocks.append(paragraph)
    return blocks


def _read_paragraph(lines: Sequence[str], index: int) -> tuple[Para, int]:
    parts: list[str] = []
    while index < len(lines):
        line = lines[index]
        if not line.strip() or _starts_block(line):
            break
        hard = line.endswith("  ") or line.endswith("\\")
        parts.append(line.strip())
        index += 1
        if index < len(lines) and lines[index].strip() and not _starts_block(lines[index]):
            parts.append("\n" if hard else " ")
    return Para("".join(parts).strip()), index


def _starts_block(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if HR_RE.match(stripped) or FENCE_RE.match(stripped) or stripped.startswith("|"):
        return True
    if stripped.startswith(">"):
        return True
    if IMAGE_RE.match(stripped):
        return True
    if HEADING_RE.match(stripped) and not line.startswith(" "):
        return True
    return bool(OL_RE.match(line) or UL_RE.match(line))


def _read_list(lines: Sequence[str], index: int) -> tuple[ListBlock, int]:
    ordered = OL_RE.match(lines[index]) is not None
    items: list[tuple[int, str]] = []
    while index < len(lines):
        line = lines[index]
        match = (OL_RE if ordered else UL_RE).match(line)
        if match is None:
            break
        indent = len(match.group(1).replace("\t", "  "))
        level = min(indent // 2, 2)
        text = match.group(3) if ordered else match.group(2)
        index += 1
        extra: list[str] = []
        while index < len(lines) and lines[index].startswith(("  ", "\t")) and lines[index].strip():
            if OL_RE.match(lines[index]) or UL_RE.match(lines[index]):
                break
            extra.append(lines[index].strip())
            index += 1
        if extra:
            text = text + " " + " ".join(extra)
        items.append((level, text.strip()))
    return ListBlock(ordered, items), index


def _read_quote(lines: Sequence[str], index: int) -> tuple[Para, int]:
    parts: list[str] = []
    while index < len(lines) and lines[index].strip().startswith(">"):
        parts.append(re.sub(r"^>\s?", "", lines[index].strip()))
        index += 1
    return Para(" ".join(parts).strip()), index


def _read_table(lines: Sequence[str], index: int) -> tuple[TableBlock, int]:
    raw: list[list[str]] = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        raw.append(_split_row(lines[index]))
        index += 1
    header = False
    rows = raw
    if len(raw) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in raw[1]):
        header = any(cell.strip() for cell in raw[0])
        rows = [raw[0]] + raw[2:] if header else raw[2:]
    width = max((len(row) for row in rows), default=0)
    padded = [row + [""] * (width - len(row)) for row in rows]
    return TableBlock(padded, header), index


def _split_row(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def style_named(document: DocumentObject, *names: str):
    """Busca un estilo por su nombre visible, sin depender del styleId."""
    wanted = {name.lower() for name in names}
    for style in document.styles:
        if style.name and style.name.lower() in wanted:
            return style
    return None


def heading_style(document: DocumentObject, level: int):
    names = HEADING_NAMES.get(min(max(level, 1), 9), HEADING_NAMES[1])
    found = style_named(document, *names)
    if found is None:
        raise SystemExit(f"El templado no tiene el estilo {names[0]!r}.")
    return found


class Lists:
    """Crea una lista de Word nueva cada vez, para que la numeración reinicie."""

    def __init__(self, document: DocumentObject) -> None:
        self._element = _numbering_element(document)

    def new(self, ordered: bool) -> int:
        kind = "decimal" if ordered else "bullet"
        abstract_id = _abstract_id(self._element, kind)
        return _add_num(self._element, abstract_id)


def _numbering_element(document: DocumentObject):
    try:
        part = document.part.part_related_by(RT.NUMBERING)
        return part.element
    except KeyError:
        element = parse_xml(
            '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
        )
        part = NumberingPart(
            PackURI("/word/numbering.xml"),
            CT.WML_NUMBERING,
            element,
            document.part.package,
        )
        document.part.relate_to(part, RT.NUMBERING)
        return element


def _abstract_id(element, kind: str) -> str:
    fmt = "decimal" if kind == "decimal" else "bullet"
    for abstract in element.findall(qn("w:abstractNum")):
        for level in abstract.findall(qn("w:lvl")):
            if level.get(qn("w:ilvl")) != "0":
                continue
            num_fmt = level.find(qn("w:numFmt"))
            if num_fmt is not None and num_fmt.get(qn("w:val")) == fmt:
                return abstract.get(qn("w:abstractNumId"))
    abstract_id = _next_attr(element, qn("w:abstractNum"), qn("w:abstractNumId"))
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), abstract_id)
    nsid = OxmlElement("w:nsid")
    nsid.set(qn("w:val"), f"{random.randint(0, 0xFFFFFFFF):08X}")
    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "hybridMultilevel")
    abstract.append(nsid)
    abstract.append(multi)
    if kind == "decimal":
        texts = ("%1.", "%2.", "%3.")
        fonts = (None, None, None)
        fmt_name = "decimal"
    else:
        texts = ("•", "◦", "▪")
        fonts = (None, None, None)
        fmt_name = "bullet"
    for ilvl, text in enumerate(texts):
        abstract.append(_numbering_level(ilvl, fmt_name, text, 720 + ilvl * 720, fonts[ilvl]))
    first_num = element.find(qn("w:num"))
    if first_num is not None:
        first_num.addprevious(abstract)
    else:
        element.append(abstract)
    return abstract_id


def _numbering_level(ilvl: int, fmt: str, text: str, left: int, font: Optional[str]):
    level = OxmlElement("w:lvl")
    level.set(qn("w:ilvl"), str(ilvl))
    start = OxmlElement("w:start")
    start.set(qn("w:val"), "1")
    num_fmt = OxmlElement("w:numFmt")
    num_fmt.set(qn("w:val"), fmt)
    lvl_text = OxmlElement("w:lvlText")
    lvl_text.set(qn("w:val"), text)
    justify = OxmlElement("w:lvlJc")
    justify.set(qn("w:val"), "left")
    paragraph = OxmlElement("w:pPr")
    indent = OxmlElement("w:ind")
    indent.set(qn("w:left"), str(left))
    indent.set(qn("w:hanging"), "360")
    paragraph.append(indent)
    level.extend((start, num_fmt, lvl_text, justify, paragraph))
    if font:
        run_props = OxmlElement("w:rPr")
        fonts = OxmlElement("w:rFonts")
        fonts.set(qn("w:ascii"), font)
        fonts.set(qn("w:hAnsi"), font)
        run_props.append(fonts)
        level.append(run_props)
    return level


def _add_num(element, abstract_id: str) -> int:
    num_id = int(_next_attr(element, qn("w:num"), qn("w:numId"), start=1))
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(num_id))
    ref = OxmlElement("w:abstractNumId")
    ref.set(qn("w:val"), str(abstract_id))
    num.append(ref)
    element.append(num)
    return num_id


def _next_attr(element, tag: str, attr: str, start: int = 0) -> str:
    values = []
    for node in element.findall(tag):
        raw = node.get(attr)
        if raw and raw.isdigit():
            values.append(int(raw))
    return str(max(values, default=start - 1) + 1)


def add_inline(
    paragraph: Paragraph,
    text: str,
    *,
    color: Optional[RGBColor] = None,
    size: Optional[Pt] = None,
    force_bold: bool = False,
    force_italic: bool = False,
) -> None:
    """Escribe texto con negrita, cursiva, código, enlaces e imágenes en línea."""
    cursor = 0
    for match in TOKEN_RE.finditer(text):
        if match.start() > cursor:
            _add_plain(
                paragraph,
                text[cursor : match.start()],
                color=color,
                size=size,
                bold=force_bold,
                italic=force_italic,
            )
        if match.group("bi") is not None:
            _add_plain(
                paragraph,
                match.group("bi"),
                color=color,
                size=size,
                bold=True,
                italic=True,
            )
        elif match.group("b") is not None:
            _add_plain(paragraph, match.group("b"), color=color, size=size, bold=True, italic=force_italic)
        elif match.group("i") is not None:
            _add_plain(paragraph, match.group("i"), color=color, size=size, bold=force_bold, italic=True)
        elif match.group("code") is not None:
            _add_code(paragraph, match.group("code"), color=color, size=size, bold=force_bold)
        elif match.group("lt") is not None:
            _add_hyperlink(
                paragraph,
                match.group("lt"),
                match.group("lu"),
                size=size,
                bold=force_bold,
                italic=force_italic,
            )
        elif match.group("ia") is not None:
            pass
        cursor = match.end()
    if cursor < len(text):
        _add_plain(
            paragraph,
            text[cursor:],
            color=color,
            size=size,
            bold=force_bold,
            italic=force_italic,
        )


def _add_plain(
    paragraph: Paragraph,
    text: str,
    *,
    color: Optional[RGBColor],
    size: Optional[Pt],
    bold: bool,
    italic: bool,
) -> None:
    chunks = text.split("\n")
    for index, chunk in enumerate(chunks):
        if index:
            paragraph.add_run().add_break()
        if chunk == "":
            continue
        run = paragraph.add_run(chunk)
        if bold:
            run.bold = True
        if italic:
            run.italic = True
        if color is not None:
            run.font.color.rgb = color
        if size is not None:
            run.font.size = size


def _add_code(
    paragraph: Paragraph,
    text: str,
    *,
    color: Optional[RGBColor],
    size: Optional[Pt],
    bold: bool,
) -> None:
    run = paragraph.add_run(text)
    run.font.name = "Consolas"
    run._r.rPr.rFonts.set(qn("w:cs"), "Consolas")
    run.font.size = size or Pt(10.5)
    if bold:
        run.bold = True
    if color is not None:
        run.font.color.rgb = color
    else:
        shade = OxmlElement("w:shd")
        shade.set(qn("w:val"), "clear")
        shade.set(qn("w:color"), "auto")
        shade.set(qn("w:fill"), "F3F6F8")
        run._r.rPr.append(shade)


def _add_hyperlink(
    paragraph: Paragraph,
    text: str,
    url: str,
    *,
    size: Optional[Pt],
    bold: bool,
    italic: bool,
) -> None:
    relation = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relation)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), ACCENT)
    props.extend((underline, color))
    if bold:
        props.append(OxmlElement("w:b"))
    if italic:
        props.append(OxmlElement("w:i"))
    if size is not None:
        size_el = OxmlElement("w:sz")
        size_el.set(qn("w:val"), str(int(size.pt * 2)))
        props.append(size_el)
    text_el = OxmlElement("w:t")
    text_el.set(XML_SPACE, "preserve")
    text_el.text = text
    run.extend((props, text_el))
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def _apply_num(paragraph: Paragraph, num_id: int, level: int) -> None:
    props = paragraph._p.get_or_add_pPr()
    numbering = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), str(level))
    nid = OxmlElement("w:numId")
    nid.set(qn("w:val"), str(num_id))
    numbering.extend((ilvl, nid))
    props.append(numbering)


def _shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:shd")):
        tc_pr.remove(old)
    shade = OxmlElement("w:shd")
    shade.set(qn("w:val"), "clear")
    shade.set(qn("w:color"), "auto")
    shade.set(qn("w:fill"), fill)
    tc_pr.append(shade)


def _set_table_geometry(table: Table) -> None:
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    for tag in ("w:tblStyle", "w:tblW", "w:tblInd", "w:jc", "w:tblBorders", "w:tblCellMar", "w:tblLayout"):
        for node in tbl_pr.findall(qn(tag)):
            tbl_pr.remove(node)
    width = OxmlElement("w:tblW")
    width.set(qn("w:w"), str(CONTENT_WIDTH_TWIPS))
    width.set(qn("w:type"), "dxa")
    indent = OxmlElement("w:tblInd")
    indent.set(qn("w:w"), "0")
    indent.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), ACCENT)
        borders.append(border)
    margins = OxmlElement("w:tblCellMar")
    for edge, value in (("top", "50"), ("left", "80"), ("bottom", "50"), ("right", "80")):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:w"), value)
        node.set(qn("w:type"), "dxa")
        margins.append(node)
    tbl_pr.extend((width, indent, layout, borders, margins))

    cols = len(table.columns)
    weights = []
    for col in range(cols):
        longest = 0
        for row in table.rows:
            for line in row.cells[col].text.splitlines():
                longest = max(longest, len(line))
        # Un párrafo largo no se queda con toda la tabla; sí se respeta la etiqueta.
        weights.append(min(max(longest, 4), 42))
    total = sum(weights) or 1
    minimum = 900
    widths = [int(CONTENT_WIDTH_TWIPS * weight / total) for weight in weights]
    for index, width in enumerate(widths):
        if width >= minimum:
            continue
        donor = max(range(len(widths)), key=lambda item: widths[item])
        deficit = minimum - width
        if widths[donor] - deficit < minimum:
            continue
        widths[index] = minimum
        widths[donor] -= deficit
    widths[-1] += CONTENT_WIDTH_TWIPS - sum(widths)
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for child in list(grid):
            grid.remove(child)
    else:
        grid = OxmlElement("w:tblGrid")
        tbl_pr.addnext(grid)
    for width_twips in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width_twips))
        grid.append(col)
    for row in table.rows:
        for index, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            for old in tc_pr.findall(qn("w:tcW")):
                tc_pr.remove(old)
            cell_width = OxmlElement("w:tcW")
            cell_width.set(qn("w:w"), str(widths[index]))
            cell_width.set(qn("w:type"), "dxa")
            tc_pr.append(cell_width)


def _fill_cell(cell, text: str, *, header: bool, normal) -> None:
    paragraph = cell.paragraphs[0]
    paragraph.style = normal
    paragraph.clear()
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.line_spacing = 1.08
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    if header:
        _shade_cell(cell, ACCENT)
        add_inline(paragraph, text, color=RGBColor(0xFF, 0xFF, 0xFF), size=Pt(11), force_bold=True)
        tr_pr = cell._tc.getparent().get_or_add_trPr()
        if tr_pr.find(qn("w:tblHeader")) is None:
            tr_pr.append(OxmlElement("w:tblHeader"))
    else:
        add_inline(paragraph, text, size=Pt(11))


def _resolve_image(src: str, base: Path) -> Optional[Path]:
    if src.startswith(("http://", "https://")):
        return None
    candidate = (base / unquote(src)).resolve()
    return candidate if candidate.is_file() else None


def _openable_image(path: Path) -> tuple[Path, Optional[Path]]:
    """Return a path Pillow can open. SVG is rasterized to a temporary PNG."""
    if path.suffix.lower() != ".svg":
        return path, None
    handle = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    handle.close()
    png = Path(handle.name)
    subprocess.run(
        ["rsvg-convert", "-d", "144", "-p", "144", "-o", str(png), str(path)],
        check=True,
    )
    return png, png


def _picture_size(path: Path) -> Emu:
    with PILImage.open(path) as image:
        width, height = image.size
    max_width = int(CONTENT_WIDTH)
    max_height = int(Emu(914400 * 7.2))
    if width <= 0 or height <= 0:
        return CONTENT_WIDTH
    scaled = max_width
    if height * scaled / width > max_height:
        scaled = int(max_height * width / height)
    return Emu(scaled)


def _add_image(document: DocumentObject, block: ImageBlock, base: Path, stats: dict) -> None:
    path = _resolve_image(block.src, base)
    if path is not None:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(8)
        paragraph.paragraph_format.space_after = Pt(2)
        embed, temporary = _openable_image(path)
        try:
            paragraph.add_run().add_picture(str(embed), width=_picture_size(embed))
        finally:
            if temporary is not None:
                temporary.unlink()
        stats["images"] += 1
    else:
        stats["missing_images"].append(block.src)
    if block.alt or path is None:
        caption = document.add_paragraph()
        caption.paragraph_format.space_before = Pt(0)
        caption.paragraph_format.space_after = Pt(8)
        note = block.alt or Path(unquote(block.src)).name
        if path is None:
            note = f"{note} — imagem não encontrada ({Path(unquote(block.src)).name})"
        run = caption.add_run(note)
        run.italic = True
        run.font.size = Pt(10)
        run.font.color.rgb = CAPTION


def _render(document: DocumentObject, blocks: Iterable[Block], base: Path) -> dict:
    normal = style_named(document, "Normal", "normal")
    lists = Lists(document)
    stats = {"headings": {}, "tables": 0, "lists": 0, "images": 0, "missing_images": []}
    title = ""
    for block in blocks:
        if isinstance(block, Heading):
            paragraph = document.add_paragraph()
            paragraph.style = heading_style(document, block.level)
            add_inline(paragraph, block.text)
            stats["headings"][block.level] = stats["headings"].get(block.level, 0) + 1
            if not title:
                title = re.sub(r"[*`]", "", block.text).strip()
        elif isinstance(block, Para):
            paragraph = document.add_paragraph()
            if normal is not None:
                paragraph.style = normal
            add_inline(paragraph, block.text)
        elif isinstance(block, ListBlock):
            num_id = lists.new(block.ordered)
            stats["lists"] += 1
            for level, text in block.items:
                paragraph = document.add_paragraph()
                if normal is not None:
                    paragraph.style = normal
                _apply_num(paragraph, num_id, level)
                add_inline(paragraph, text)
        elif isinstance(block, TableBlock):
            if not block.rows:
                continue
            table = document.add_table(rows=len(block.rows), cols=len(block.rows[0]))
            for row_index, row in enumerate(block.rows):
                for col_index, cell_text in enumerate(row):
                    _fill_cell(
                        table.rows[row_index].cells[col_index],
                        cell_text,
                        header=block.header and row_index == 0,
                        normal=normal,
                    )
            _set_table_geometry(table)
            stats["tables"] += 1
        elif isinstance(block, ImageBlock):
            _add_image(document, block, base, stats)
        elif isinstance(block, CodeBlock):
            paragraph = document.add_paragraph()
            if normal is not None:
                paragraph.style = normal
            paragraph.paragraph_format.space_before = Pt(6)
            paragraph.paragraph_format.space_after = Pt(6)
            shade = OxmlElement("w:shd")
            shade.set(qn("w:val"), "clear")
            shade.set(qn("w:color"), "auto")
            shade.set(qn("w:fill"), "F3F6F8")
            paragraph._p.get_or_add_pPr().append(shade)
            run = paragraph.add_run(block.text)
            run.font.name = "Consolas"
            run.font.size = Pt(10)
    if title:
        document.core_properties.title = title
    document.add_paragraph()
    return stats


def _clear_body(document: DocumentObject) -> None:
    body = document.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def _page_break(document: DocumentObject) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run()
    break_el = OxmlElement("w:br")
    break_el.set(qn("w:type"), "page")
    run._r.append(break_el)


def format_relatorio(markdown: Path, output: Path, *, cover: bool) -> dict:
    """Genera el .docx a partir del Markdown y del templado elegido."""
    template = ASSETS / ("template.docx" if cover else "template_no_cover.docx")
    if not template.is_file():
        raise SystemExit(f"No está el templado: {template}")
    if not markdown.is_file():
        raise SystemExit(f"No está el Markdown: {markdown}")
    document = Document(str(template))
    _clear_body(document)
    if cover:
        _page_break(document)
    blocks = parse_markdown(markdown.read_text(encoding="utf-8"))
    stats = _render(document, blocks, markdown.parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output))
    _validate(output, cover)
    stats["output"] = str(output)
    stats["cover"] = cover
    return stats


def _validate(path: Path, cover: bool) -> None:
    with zipfile.ZipFile(path) as package:
        root = etree.fromstring(package.read("word/document.xml"))
        body = root.find(f"{{{W_NS}}}body")
        sect = body.find(f"{{{W_NS}}}sectPr")
        has_title = sect.find(f"{{{W_NS}}}titlePg") is not None
        if has_title != cover:
            raise SystemExit("La portada del templado no quedó como se pidió.")
        headers = sect.findall(f"{{{W_NS}}}headerReference")
        footers = sect.findall(f"{{{W_NS}}}footerReference")
        if len(headers) < 2 or len(footers) < 2:
            raise SystemExit("Se perdieron el encabezado o el pie del templado.")
        media = [name for name in package.namelist() if name.startswith("word/media/")]
        expected = 3 if cover else 2
        if len(media) < expected:
            raise SystemExit("Se perdieron las imágenes del templado.")
        first = body.find(f"{{{W_NS}}}p")
        breaks = [
            node
            for node in first.findall(f".//{{{W_NS}}}br")
            if node.get(f"{{{W_NS}}}type") == "page"
        ]
        if cover and not breaks:
            raise SystemExit("El texto quedó encima de la portada.")
        if not cover and breaks:
            raise SystemExit("La versión sin portada abre con una página en blanco.")


def _print_stats(stats: dict) -> None:
    mode = "con portada" if stats["cover"] else "sin portada"
    levels = ", ".join(f"título {level} × {count}" for level, count in sorted(stats["headings"].items()))
    print(f"Plantilla: {mode}")
    print(f"Salida: {stats['output']}")
    print(f"Títulos: {levels or 'ninguno'}")
    print(f"Tablas: {stats['tables']}")
    print(f"Listas: {stats['lists']}")
    print(f"Imágenes incrustadas: {stats['images']}")
    if stats["missing_images"]:
        print("Imágenes no encontradas:")
        for src in stats["missing_images"]:
            print(f"  - {src}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vuelca un Markdown en el templado Word de VERT Analytics."
    )
    parser.add_argument("markdown", type=Path, help="Relatório en Markdown")
    parser.add_argument("-o", "--output", type=Path, help="Ruta del .docx")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cover", action="store_true", help="Usa la plantilla con portada")
    group.add_argument("--no-cover", action="store_true", help="Usa la plantilla sin portada")
    args = parser.parse_args(argv)
    markdown = args.markdown.expanduser().resolve()
    suffix = "com-capa" if args.cover else "sem-capa"
    output = args.output or markdown.with_name(f"{markdown.stem}-{suffix}.docx")
    output = output.expanduser().resolve()
    stats = format_relatorio(markdown, output, cover=args.cover)
    _print_stats(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
