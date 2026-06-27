#!/usr/bin/env python3
"""
Builds "React Native Engineer — 100 Interview Q&A" as a polished PDF.

Content is generated as JSON (one file per section) under scratchpad/qa and
assembled here. Each question renders:  Theory -> Answer -> Code -> Diagram.

Run:  python3 build_pdf.py
"""

import os
import re
import glob
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Flowable,
)

HERE = os.path.dirname(os.path.abspath(__file__))
QA_DIR = os.path.join(
    "/private/tmp/claude-501/-Users-ioss-Documents-StudyProjects-interview-basic"
    "/b9116a51-457d-407a-a59f-4b9c66c0ea26/scratchpad/qa"
)
OUT_PATH = os.path.join(HERE, "Rinshad_FullStack_150_Interview_QA.pdf")

CANDIDATE = "Mohammed Rinshad M I"
ROLE = "Full-Stack Engineer · React · Next.js · Node.js · Golang · AI/LLM"
YEAR = "2026"
GUIDE_TITLE = "Full-Stack Engineer — 150 Interview Q&A"

# ---------------- Palette ----------------
INK        = HexColor("#0F172A")   # near-black slate
INK_SOFT   = HexColor("#334155")
MUTED      = HexColor("#64748B")
HAIR       = HexColor("#E2E8F0")
PAGE_BG    = white

THEORY_BG  = HexColor("#EFF6FF")   # light blue
THEORY_AC  = HexColor("#2563EB")
ANSWER_BG  = HexColor("#ECFDF5")   # light green
ANSWER_AC  = HexColor("#059669")

CODE_BG    = HexColor("#0B1220")   # dark navy
CODE_FG    = HexColor("#E5E7EB")
CODE_COMM  = HexColor("#7DD3A8")   # comment green
CODE_LABEL = HexColor("#93C5FD")

DIAG_BG    = HexColor("#0F172A")   # blueprint navy
DIAG_FG    = HexColor("#BAE6FD")
DIAG_LABEL = HexColor("#FBBF24")

# 10 section accent colors
SECTION_COLORS = [
    HexColor("#2563EB"),  # 1 blue
    HexColor("#7C3AED"),  # 2 violet
    HexColor("#0891B2"),  # 3 cyan
    HexColor("#DB2777"),  # 4 pink
    HexColor("#EA580C"),  # 5 orange
    HexColor("#16A34A"),  # 6 green
    HexColor("#0D9488"),  # 7 teal
    HexColor("#DC2626"),  # 8 red
    HexColor("#4F46E5"),  # 9 indigo
    HexColor("#9333EA"),  # 10 purple
]

# ---------------- Geometry ----------------
PAGE_W, PAGE_H = A4
MARGIN_X = 16 * mm
MARGIN_T = 20 * mm
MARGIN_B = 16 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

CODE_FONT = "Courier"
CODE_FS = 7
CODE_LEAD = 9.6
CODE_PAD = 8
# usable text width inside a code box -> char capacity
_CHAR_W = CODE_FS * 0.6
CODE_MAXCHARS = int((CONTENT_W - 2 * CODE_PAD) / _CHAR_W) - 1   # ~108


# ---------------- Styles ----------------
styles = getSampleStyleSheet()


def mkstyle(name, **kw):
    return ParagraphStyle(name, parent=styles["Normal"], **kw)


QSTYLE = mkstyle("Q", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
                 textColor=INK, spaceAfter=2)
BODY = mkstyle("Body", fontName="Helvetica", fontSize=9.3, leading=13.6,
               textColor=INK_SOFT)
BODY_T = mkstyle("BodyT", fontName="Helvetica", fontSize=9.3, leading=13.6,
                 textColor=HexColor("#1E3A8A"))
BODY_A = mkstyle("BodyA", fontName="Helvetica", fontSize=9.3, leading=13.6,
                 textColor=HexColor("#065F46"))
LABEL = mkstyle("Label", fontName="Helvetica-Bold", fontSize=7.5, leading=10,
                textColor=MUTED)


def md_to_para(text):
    """Escape XML, convert **bold** -> <b>, keep it safe for Paragraph."""
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t


# ---------------- Code wrapping ----------------
def wrap_code(code, max_chars=CODE_MAXCHARS):
    out = []
    for raw in code.replace("\t", "    ").rstrip("\n").split("\n"):
        if len(raw) <= max_chars:
            out.append(raw)
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        cont = " " * indent + "  "
        line = raw
        while len(line) > max_chars:
            cut = max_chars
            sp = line.rfind(" ", indent + 1, cut)
            if sp <= indent + 1:
                sp = cut
            out.append(line[:sp])
            line = cont + line[sp:].lstrip(" ")
        out.append(line)
    return out


def is_comment(line):
    s = line.lstrip()
    return s.startswith(("//", "#", "--", "/*", "*"))


# ---------------- Flowables ----------------
class MonoBlock(Flowable):
    """Splittable monospace block (code or diagram) with a label band."""

    def __init__(self, lines, label, *, bg, fg, label_color,
                 comment_color=None, font_size=CODE_FS, leading=CODE_LEAD,
                 width=None, _label_h=None):
        Flowable.__init__(self)
        self.lines = lines
        self.label = label
        self.bg = bg
        self.fg = fg
        self.label_color = label_color
        self.comment_color = comment_color
        self.font_size = font_size
        self.leading = leading
        self.pad = CODE_PAD
        self._w = width
        self.label_h = (16 if label else 0) if _label_h is None else _label_h

    def wrap(self, availW, availH):
        self.width = self._w or availW
        self.height = self.label_h + self.pad * 2 + len(self.lines) * self.leading
        return self.width, self.height

    def split(self, availW, availH):
        room = availH - self.label_h - self.pad * 2
        n = int(room // self.leading)
        if n >= len(self.lines):
            return [self]
        if n < 4:                      # too little room -> move whole block down
            return []
        first = MonoBlock(self.lines[:n], self.label, bg=self.bg, fg=self.fg,
                          label_color=self.label_color,
                          comment_color=self.comment_color,
                          font_size=self.font_size, leading=self.leading,
                          width=self._w)
        cont_label = (self.label + "  (continued)") if self.label else None
        rest = MonoBlock(self.lines[n:], cont_label, bg=self.bg, fg=self.fg,
                         label_color=self.label_color,
                         comment_color=self.comment_color,
                         font_size=self.font_size, leading=self.leading,
                         width=self._w)
        return [first, rest]

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=0)
        top = self.height
        if self.label:
            c.setFillColor(self.label_color)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(self.pad, top - 11, self.label)
            # subtle divider under label
            c.setStrokeColor(Color(1, 1, 1, 0.08))
            c.setLineWidth(0.5)
            c.line(self.pad, top - self.label_h + 2,
                   self.width - self.pad, top - self.label_h + 2)
            top -= self.label_h
        c.setFont(CODE_FONT, self.font_size)
        ty = top - self.pad - self.font_size
        for ln in self.lines:
            if self.comment_color is not None and is_comment(ln):
                c.setFillColor(self.comment_color)
            else:
                c.setFillColor(self.fg)
            c.drawString(self.pad, ty, ln)
            ty -= self.leading


class LabeledBox(Flowable):
    """Tinted box with an accent left-bar, a label, and wrapped prose."""

    def __init__(self, label, para, *, bg, accent, width=None):
        Flowable.__init__(self)
        self.label = label
        self.para = para
        self.bg = bg
        self.accent = accent
        self._w = width
        self.pad = 9
        self.label_h = 13

    def wrap(self, availW, availH):
        self.width = self._w or availW
        inner = self.width - 2 * self.pad - 4
        _, ph = self.para.wrap(inner, availH)
        self.para_h = ph
        self.height = self.label_h + self.pad * 2 + ph
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.roundRect(0, 0, 4, self.height, 2, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(self.pad + 4, self.height - 11, self.label.upper())
        self.para.drawOn(c, self.pad + 4, self.pad)


class SectionBanner(Flowable):
    def __init__(self, number, title, blurb, color, qrange, width=CONTENT_W):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.blurb = blurb
        self.color = color
        self.qrange = qrange
        self.width = width
        self.height = 26 * mm

    def wrap(self, *a):
        return self.width, self.height

    def draw(self):
        c = self.canv
        h = self.height
        c.setFillColor(self.color)
        c.roundRect(0, 0, self.width, h, 7, fill=1, stroke=0)
        # number chip
        c.setFillColor(Color(1, 1, 1, 0.16))
        c.roundRect(7 * mm, h / 2 - 8 * mm, 16 * mm, 16 * mm, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(7 * mm + 8 * mm, h / 2 - 3.2 * mm, str(self.number))
        tx = 28 * mm
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14.5)
        c.drawString(tx, h / 2 + 2.5 * mm, self.title)
        c.setFillColor(Color(1, 1, 1, 0.9))
        c.setFont("Helvetica", 8.4)
        blurb = self.blurb
        if len(blurb) > 96:
            blurb = blurb[:93] + "..."
        c.drawString(tx, h / 2 - 3.4 * mm, blurb)
        # q-range pill, right
        c.setFillColor(Color(1, 1, 1, 0.16))
        pw = 24 * mm
        c.roundRect(self.width - pw - 6 * mm, h / 2 - 4 * mm, pw, 8 * mm, 4,
                    fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self.width - pw / 2 - 6 * mm, h / 2 - 1.2 * mm,
                            self.qrange)


class QBadge(Flowable):
    def __init__(self, qnum, section_title, color, width=CONTENT_W):
        Flowable.__init__(self)
        self.qnum = qnum
        self.section_title = section_title
        self.color = color
        self.width = width
        self.height = 7.6 * mm

    def wrap(self, *a):
        return self.width, self.height

    def draw(self):
        c = self.canv
        h = self.height
        c.setFillColor(self.color)
        c.roundRect(0, 0, 17 * mm, h, 3.5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawCentredString(8.5 * mm, h / 2 - 1.3 * mm, "Q%d" % self.qnum)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(19 * mm, h / 2 - 1.0 * mm, self.section_title.upper())
        c.setStrokeColor(HAIR)
        c.setLineWidth(0.6)
        c.line(19 * mm, 0.6 * mm, self.width, 0.6 * mm)


class HRule(Flowable):
    def __init__(self, width=CONTENT_W, color=HAIR, thick=0.6, pad=0):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thick = thick
        self.height = pad

    def wrap(self, *a):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thick)
        c.line(0, self.height / 2, self.width, self.height / 2)


class CoverBackground(Flowable):
    def __init__(self, w, h):
        Flowable.__init__(self)
        self.w = w
        self.h = h

    def wrap(self, *a):
        return 0, 0

    def draw(self):
        c = self.canv
        # vertical gradient bands (dark navy -> indigo)
        steps = 120
        c1 = (0x0B, 0x12, 0x20)
        c2 = (0x1E, 0x1B, 0x4B)
        for i in range(steps):
            t = i / (steps - 1)
            r = (c1[0] + (c2[0] - c1[0]) * t) / 255
            g = (c1[1] + (c2[1] - c1[1]) * t) / 255
            b = (c1[2] + (c2[2] - c1[2]) * t) / 255
            c.setFillColor(Color(r, g, b))
            y = self.h - (i + 1) * (self.h / steps)
            c.rect(-MARGIN_X, y, self.w, self.h / steps + 1, fill=1, stroke=0)
        # accent dots row
        cols = ["#2563EB", "#7C3AED", "#0891B2", "#DB2777", "#EA580C",
                "#16A34A", "#0D9488", "#DC2626", "#4F46E5", "#9333EA"]
        for i, hexc in enumerate(cols):
            c.setFillColor(HexColor(hexc))
            c.circle(-MARGIN_X + 22 * mm + i * 16.4 * mm,
                     self.h - 250, 3.0 * mm, fill=1, stroke=0)


# ---------------- Page decoration ----------------
def on_content_page(canvas_obj, doc):
    c = canvas_obj
    c.saveState()
    # header
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, PAGE_H - 12 * mm, GUIDE_TITLE)
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 12 * mm, CANDIDATE)
    c.setStrokeColor(HAIR)
    c.setLineWidth(0.6)
    c.line(MARGIN_X, PAGE_H - 14 * mm, PAGE_W - MARGIN_X, PAGE_H - 14 * mm)
    # footer
    c.line(MARGIN_X, 12 * mm, PAGE_W - MARGIN_X, 12 * mm)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, 8.4 * mm, "Interview Preparation · " + YEAR)
    c.drawRightString(PAGE_W - MARGIN_X, 8.4 * mm, "Page %d" % doc.page)
    c.restoreState()


def on_cover_page(canvas_obj, doc):
    c = canvas_obj
    c.saveState()
    # vertical gradient (dark navy -> indigo), full bleed
    steps = 140
    c1 = (0x0B, 0x12, 0x20)
    c2 = (0x1E, 0x1B, 0x4B)
    band = PAGE_H / steps
    for i in range(steps):
        t = i / (steps - 1)
        r = (c1[0] + (c2[0] - c1[0]) * t) / 255
        g = (c1[1] + (c2[1] - c1[1]) * t) / 255
        b = (c1[2] + (c2[2] - c1[2]) * t) / 255
        c.setFillColor(Color(r, g, b))
        c.rect(0, PAGE_H - (i + 1) * band, PAGE_W, band + 1, fill=1, stroke=0)
    # top hairline accent
    c.setStrokeColor(HexColor("#334155"))
    c.setLineWidth(0.8)
    c.line(MARGIN_X, PAGE_H - 16 * mm, PAGE_W - MARGIN_X, PAGE_H - 16 * mm)
    # accent dot row near the footer
    cols = ["#2563EB", "#7C3AED", "#0891B2", "#DB2777", "#EA580C",
            "#16A34A", "#0D9488", "#DC2626", "#4F46E5", "#9333EA"]
    spacing = (PAGE_W - 2 * MARGIN_X) / (len(cols) - 1)
    for i, hexc in enumerate(cols):
        c.setFillColor(HexColor(hexc))
        c.circle(MARGIN_X + i * spacing, 22 * mm, 2.6 * mm, fill=1, stroke=0)
    c.restoreState()


# ---------------- Build story ----------------
def load_sections():
    files = sorted(glob.glob(os.path.join(QA_DIR, "sec_*.json")),
                   key=lambda p: int(re.search(r"sec_(\d+)", p).group(1)))
    secs = []
    for f in files:
        secs.append(json.load(open(f)))
    return secs


SECTION_BLURBS = {
    1: "Closures, this, event loop, promises, types, generics, utility types, JS to TS.",
    2: "Components, hooks, JSX, RSC, App Router, rendering, code-splitting, performance.",
    3: "Context, Redux Toolkit, thunks, selectors, Zustand, TanStack Query caching.",
    4: "Event loop, middleware, JWT, validation, error handling, Sequelize, REST design.",
    5: "Goroutines, channels, interfaces, Gin middleware, GORM, clean architecture.",
    6: "SQL vs NoSQL, indexing, transactions, Postgres, MongoDB, Redis, pgvector.",
    7: "JWT rotation, OAuth, rate limiting, Stripe / PayPal / Razorpay webhooks.",
    8: "Embeddings, semantic search, RAG, streaming, tool calling, vector indexing.",
    9: "WebSockets, reconnection, Redis pub/sub, Yjs CRDT, presence and scaling.",
    10: "Clean architecture, monorepo, Docker, CI/CD, Nginx, PM2, testing, monitoring.",
}


def lang_label(lang):
    return {
        "tsx": "TypeScript / TSX", "ts": "TypeScript", "go": "Go",
        "sql": "SQL", "yaml": "YAML", "bash": "Shell / Bash",
        "js": "JavaScript", "json": "JSON", "dockerfile": "Dockerfile",
    }.get(lang, lang.upper())


def build():
    sections = load_sections()
    total_q = sum(len(s["items"]) for s in sections)

    story = []

    # ---------- COVER ----------  (gradient drawn by on_cover_page)
    story.append(Spacer(1, 40 * mm))
    cap = mkstyle("cap", fontName="Helvetica-Bold", fontSize=11,
                  textColor=HexColor("#93C5FD"), alignment=TA_CENTER,
                  leading=14)
    story.append(Paragraph("INTERVIEW PREPARATION GUIDE", cap))
    story.append(Spacer(1, 6 * mm))
    title = mkstyle("title", fontName="Helvetica-Bold", fontSize=33,
                    textColor=white, alignment=TA_CENTER, leading=38)
    story.append(Paragraph("150 Full-Stack", title))
    story.append(Paragraph("Interview Q&amp;A", title))
    story.append(Spacer(1, 5 * mm))
    sub = mkstyle("sub", fontName="Helvetica", fontSize=12.5,
                  textColor=HexColor("#C7D2FE"), alignment=TA_CENTER, leading=18)
    story.append(Paragraph(
        "Theory · Strong Answers · Example Code · Architecture Diagrams", sub))
    story.append(Spacer(1, 30 * mm))

    chip = mkstyle("chip", fontName="Helvetica-Bold", fontSize=10.5,
                   textColor=white, alignment=TA_CENTER)
    stat_tbl = Table(
        [["150", "10", "150", "8"],
         ["Questions", "Sections", "Diagrams", "Languages"]],
        colWidths=[CONTENT_W / 4] * 4)
    stat_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 24),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, 1), 9),
        ("TEXTCOLOR", (0, 1), (-1, 1), HexColor("#A5B4FC")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
    ]))
    story.append(stat_tbl)
    story.append(Spacer(1, 24 * mm))
    namest = mkstyle("name", fontName="Helvetica-Bold", fontSize=15,
                     textColor=white, alignment=TA_CENTER)
    rolest = mkstyle("role", fontName="Helvetica", fontSize=9.5,
                     textColor=HexColor("#94A3B8"), alignment=TA_CENTER,
                     leading=14, spaceBefore=3)
    story.append(Paragraph("Prepared for " + CANDIDATE, namest))
    story.append(Paragraph(ROLE + "  ·  " + YEAR, rolest))
    story.append(PageBreak())

    # ---------- HOW TO USE ----------
    h2 = mkstyle("h2", fontName="Helvetica-Bold", fontSize=17, textColor=INK,
                 spaceAfter=4)
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("How to Use This Guide", h2))
    story.append(Spacer(1, 1.5 * mm))
    story.append(HRule(thick=1.2, color=THEORY_AC, pad=2))
    story.append(Spacer(1, 4 * mm))
    intro = mkstyle("intro", fontName="Helvetica", fontSize=9.6, leading=15,
                    textColor=INK_SOFT)
    story.append(Paragraph(
        "This guide turns your resume into <b>150 realistic, interview-ready "
        "questions</b> across the full stack you actually work in — JavaScript "
        "&amp; TypeScript, React/Next.js, Node.js, Golang, databases, real-time, "
        "AI/LLM features, payments and DevOps. Every question is answered in four "
        "layers so you understand it, not just memorise it:", intro))
    story.append(Spacer(1, 4 * mm))

    legend = [
        ("THEORY", "The concept and the <i>why</i> — what the interviewer is "
         "really probing for.", THEORY_AC, THEORY_BG),
        ("ANSWER", "A natural, confident spoken answer you can deliver out "
         "loud. <b>Bold</b> terms are keywords to land.", ANSWER_AC, ANSWER_BG),
        ("CODE", "A concise, correct example — what good looks like in real "
         "code.", CODE_LABEL, CODE_BG),
        ("ARCHITECTURE", "An ASCII diagram of the flow or system, so you can "
         "draw it on a whiteboard.", DIAG_LABEL, DIAG_BG),
    ]
    for lab, desc, ac, bg in legend:
        chip_p = Paragraph("<b>%s</b>" % lab,
                           mkstyle("lg", fontName="Helvetica-Bold", fontSize=8.5,
                                   textColor=white, alignment=TA_CENTER))
        desc_p = Paragraph(desc, BODY)
        t = Table([[chip_p, desc_p]], colWidths=[30 * mm, CONTENT_W - 30 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), ac),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            ("LINEBELOW", (1, 0), (1, 0), 0.5, HAIR),
        ]))
        story.append(t)
        story.append(Spacer(1, 3 * mm))

    story.append(Spacer(1, 4 * mm))
    tip = LabeledBox(
        "Pro tip",
        Paragraph("Read the <b>answers out loud</b>. Interviews reward fluent "
                  "delivery, not perfect recall. When you give a number from "
                  "your resume (35% latency cut, 30% faster delivery), have a "
                  "one-line 'how I measured it' ready for the follow-up.",
                  BODY),
        bg=HexColor("#FEF9C3"), accent=HexColor("#CA8A04"))
    story.append(tip)

    # ---------- CONTENTS ----------
    story.append(PageBreak())
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Contents", h2))
    story.append(Spacer(1, 1.5 * mm))
    story.append(HRule(thick=1.2, color=THEORY_AC, pad=2))
    story.append(Spacer(1, 5 * mm))
    qstart = 1
    for s in sections:
        idx = s["section"]
        color = SECTION_COLORS[idx - 1]
        n = len(s["items"])
        qrange = "Q%d–Q%d" % (qstart, qstart + n - 1)
        qstart += n
        numchip = Paragraph(
            "<b>%d</b>" % idx,
            mkstyle("tocn", fontName="Helvetica-Bold", fontSize=13,
                    textColor=white, alignment=TA_CENTER))
        titlep = Paragraph(
            "<b>%s</b>" % s["title"],
            mkstyle("toct", fontName="Helvetica-Bold", fontSize=11,
                    textColor=INK))
        blurbp = Paragraph(
            SECTION_BLURBS.get(idx, ""),
            mkstyle("tocb", fontName="Helvetica", fontSize=8.2,
                    textColor=MUTED, leading=11))
        rangep = Paragraph(
            qrange,
            mkstyle("tocr", fontName="Helvetica-Bold", fontSize=9.5,
                    textColor=color, alignment=TA_CENTER))
        inner = Table([[titlep], [blurbp]], colWidths=[CONTENT_W - 14 * mm - 24 * mm])
        inner.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (0, 0), 0),
            ("BOTTOMPADDING", (0, 0), (0, 0), 1),
            ("TOPPADDING", (0, 1), (0, 1), 0),
        ]))
        row = Table([[numchip, inner, rangep]],
                    colWidths=[14 * mm, CONTENT_W - 14 * mm - 24 * mm, 24 * mm])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("VALIGN", (1, 0), (1, 0), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (1, 0), (1, 0), 9),
            ("ROUNDEDCORNERS", [5, 5, 5, 5]),
            ("LINEBELOW", (1, 0), (2, 0), 0.6, HAIR),
        ]))
        story.append(row)
        story.append(Spacer(1, 2.6 * mm))

    # ---------- SECTIONS ----------
    qnum = 0
    for s in sections:
        idx = s["section"]
        color = SECTION_COLORS[idx - 1]
        n = len(s["items"])
        qrange = "Q%d–Q%d" % (qnum + 1, qnum + n)
        story.append(PageBreak())
        story.append(SectionBanner(idx, s["title"],
                                   SECTION_BLURBS.get(idx, ""), color, qrange))
        story.append(Spacer(1, 6 * mm))

        for it in s["items"]:
            qnum += 1
            head = [
                QBadge(qnum, s["title"], color),
                Spacer(1, 1.6 * mm),
                Paragraph(md_to_para(it["q"]), QSTYLE),
                Spacer(1, 2.4 * mm),
                LabeledBox("Theory", Paragraph(md_to_para(it["theory"]), BODY_T),
                           bg=THEORY_BG, accent=THEORY_AC),
            ]
            story.append(KeepTogether(head))
            story.append(Spacer(1, 2.4 * mm))
            story.append(LabeledBox(
                "Strong Answer",
                Paragraph(md_to_para(it["answer"]), BODY_A),
                bg=ANSWER_BG, accent=ANSWER_AC))
            story.append(Spacer(1, 2.4 * mm))

            code_lines = wrap_code(it["code"])
            story.append(MonoBlock(
                code_lines,
                "CODE  ·  " + lang_label(it["lang"]),
                bg=CODE_BG, fg=CODE_FG, label_color=CODE_LABEL,
                comment_color=CODE_COMM))

            diag = it.get("diagram", "").strip("\n")
            if diag.strip():
                story.append(Spacer(1, 2.4 * mm))
                dlines = wrap_code(diag, max_chars=CODE_MAXCHARS)
                story.append(MonoBlock(
                    dlines, "ARCHITECTURE / FLOW",
                    bg=DIAG_BG, fg=DIAG_FG, label_color=DIAG_LABEL,
                    font_size=7.2, leading=9.4))

            story.append(Spacer(1, 4 * mm))
            story.append(HRule(thick=0.6, color=HAIR))
            story.append(Spacer(1, 4 * mm))

    # ---------- DOC ----------
    doc = BaseDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B,
        title="150 Full-Stack Interview Q&A — " + CANDIDATE,
        author=CANDIDATE)

    cover_frame = Frame(MARGIN_X, MARGIN_B, CONTENT_W, PAGE_H - MARGIN_B - 8 * mm,
                        id="cover", leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0)
    content_frame = Frame(MARGIN_X, MARGIN_B, CONTENT_W,
                          PAGE_H - MARGIN_T - MARGIN_B - 4 * mm,
                          id="content", leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=on_cover_page),
        PageTemplate(id="Content", frames=[content_frame],
                     onPage=on_content_page),
    ])

    # first page = cover, rest = content
    story.insert(0, NextTemplateMarker("Cover"))
    # switch to content right after cover pagebreak: insert marker
    # find first PageBreak (end of cover) and put a template switch after it
    return doc, story, total_q


class NextTemplateMarker:
    """Lightweight marker resolved below into NextPageTemplate."""
    def __init__(self, name):
        self.name = name


def main():
    from reportlab.platypus import NextPageTemplate
    doc, story, total_q = build()
    # resolve template flow: Cover for page 1, Content afterwards.
    final = [NextPageTemplate("Content")]
    # remove our placeholder marker(s)
    story = [f for f in story if not isinstance(f, NextTemplateMarker)]
    # Cover template is the default first page; after the first PageBreak we
    # are already requesting Content via the NextPageTemplate above (applies
    # from page 2 onward).
    final.extend(story)
    doc.build(final)
    size = os.path.getsize(OUT_PATH)
    print("Built %s  (%d questions, %.0f KB)" %
          (OUT_PATH, total_q, size / 1024))


if __name__ == "__main__":
    main()
