#!/usr/bin/env python3
"""
Extract all 100 Q&A from the existing Rinshad_RN_100_Interview_QA.pdf,
replace the STRONG ANSWER for Q26–Q50 with the user's custom answers,
and rebuild the PDF with the same polished design.

Run:  python3 rebuild_rn_pdf.py
"""

import os
import re
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Flowable, NextPageTemplate,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PDF = os.path.join(HERE, "Rinshad_RN_100_Interview_QA.pdf")
OUT_PATH = os.path.join(HERE, "Rinshad_RN_100_Interview_QA.pdf")

CANDIDATE = "Mohammed Rinshad M I"
ROLE = "React Native Engineer · iOS & Android · AI-Powered Mobile Apps"
YEAR = "2026"
GUIDE_TITLE = "React Native Engineer — 100 Interview Q&A"

# ──────────────── Palette ────────────────
INK        = HexColor("#0F172A")
INK_SOFT   = HexColor("#334155")
MUTED      = HexColor("#64748B")
HAIR       = HexColor("#E2E8F0")
PAGE_BG    = white

THEORY_BG  = HexColor("#EFF6FF")
THEORY_AC  = HexColor("#2563EB")
ANSWER_BG  = HexColor("#ECFDF5")
ANSWER_AC  = HexColor("#059669")

CODE_BG    = HexColor("#0B1220")
CODE_FG    = HexColor("#E5E7EB")
CODE_COMM  = HexColor("#7DD3A8")
CODE_LABEL = HexColor("#93C5FD")

DIAG_BG    = HexColor("#0F172A")
DIAG_FG    = HexColor("#BAE6FD")
DIAG_LABEL = HexColor("#FBBF24")

SECTION_COLORS = [
    HexColor("#2563EB"),  HexColor("#7C3AED"),  HexColor("#0891B2"),
    HexColor("#DB2777"),  HexColor("#EA580C"),  HexColor("#16A34A"),
    HexColor("#0D9488"),  HexColor("#DC2626"),  HexColor("#4F46E5"),
    HexColor("#9333EA"),
]

# ──────────────── Geometry ────────────────
PAGE_W, PAGE_H = A4
MARGIN_X = 16 * mm
MARGIN_T = 20 * mm
MARGIN_B = 16 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

CODE_FONT = "Courier"
CODE_FS = 7
CODE_LEAD = 9.6
CODE_PAD = 8
_CHAR_W = CODE_FS * 0.6
CODE_MAXCHARS = int((CONTENT_W - 2 * CODE_PAD) / _CHAR_W) - 1

# ──────────────── Styles ────────────────
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
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t


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


# ──────────────── Flowables ────────────────
class MonoBlock(Flowable):
    def __init__(self, lines, label, *, bg, fg, label_color,
                 comment_color=None, font_size=CODE_FS, leading=CODE_LEAD,
                 width=None, _label_h=None):
        Flowable.__init__(self)
        self.lines = lines; self.label = label; self.bg = bg; self.fg = fg
        self.label_color = label_color; self.comment_color = comment_color
        self.font_size = font_size; self.leading = leading
        self.pad = CODE_PAD; self._w = width
        self.label_h = (16 if label else 0) if _label_h is None else _label_h

    def wrap(self, availW, availH):
        self.width = self._w or availW
        self.height = self.label_h + self.pad * 2 + len(self.lines) * self.leading
        return self.width, self.height

    def split(self, availW, availH):
        room = availH - self.label_h - self.pad * 2
        n = int(room // self.leading)
        if n >= len(self.lines): return [self]
        if n < 4: return []
        first = MonoBlock(self.lines[:n], self.label, bg=self.bg, fg=self.fg,
                          label_color=self.label_color, comment_color=self.comment_color,
                          font_size=self.font_size, leading=self.leading, width=self._w)
        cont_label = (self.label + "  (continued)") if self.label else None
        rest = MonoBlock(self.lines[n:], cont_label, bg=self.bg, fg=self.fg,
                         label_color=self.label_color, comment_color=self.comment_color,
                         font_size=self.font_size, leading=self.leading, width=self._w)
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
    def __init__(self, label, para, *, bg, accent, width=None):
        Flowable.__init__(self)
        self.label = label; self.para = para; self.bg = bg
        self.accent = accent; self._w = width; self.pad = 9; self.label_h = 13

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
        self.number = number; self.title = title; self.blurb = blurb
        self.color = color; self.qrange = qrange
        self.width = width; self.height = 26 * mm

    def wrap(self, *a): return self.width, self.height

    def draw(self):
        c = self.canv; h = self.height
        c.setFillColor(self.color)
        c.roundRect(0, 0, self.width, h, 7, fill=1, stroke=0)
        c.setFillColor(Color(1, 1, 1, 0.16))
        c.roundRect(7*mm, h/2-8*mm, 16*mm, 16*mm, 5, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(7*mm+8*mm, h/2-3.2*mm, str(self.number))
        tx = 28*mm; c.setFillColor(white); c.setFont("Helvetica-Bold", 14.5)
        c.drawString(tx, h/2+2.5*mm, self.title)
        c.setFillColor(Color(1,1,1,0.9)); c.setFont("Helvetica", 8.4)
        blurb = self.blurb[:93]+"..." if len(self.blurb)>96 else self.blurb
        c.drawString(tx, h/2-3.4*mm, blurb)
        c.setFillColor(Color(1,1,1,0.16)); pw=24*mm
        c.roundRect(self.width-pw-6*mm, h/2-4*mm, pw, 8*mm, 4, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self.width-pw/2-6*mm, h/2-1.2*mm, self.qrange)


class QBadge(Flowable):
    def __init__(self, qnum, section_title, color, width=CONTENT_W):
        Flowable.__init__(self)
        self.qnum = qnum; self.section_title = section_title
        self.color = color; self.width = width; self.height = 7.6*mm

    def wrap(self, *a): return self.width, self.height

    def draw(self):
        c = self.canv; h = self.height
        c.setFillColor(self.color)
        c.roundRect(0, 0, 17*mm, h, 3.5, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 9.5)
        c.drawCentredString(8.5*mm, h/2-1.3*mm, "Q%d" % self.qnum)
        c.setFillColor(MUTED); c.setFont("Helvetica-Bold", 7.5)
        c.drawString(19*mm, h/2-1.0*mm, self.section_title.upper())
        c.setStrokeColor(HAIR); c.setLineWidth(0.6)
        c.line(19*mm, 0.6*mm, self.width, 0.6*mm)


class HRule(Flowable):
    def __init__(self, width=CONTENT_W, color=HAIR, thick=0.6, pad=0):
        Flowable.__init__(self)
        self.width = width; self.color = color; self.thick = thick; self.height = pad

    def wrap(self, *a): return self.width, self.height

    def draw(self):
        c = self.canv; c.setStrokeColor(self.color); c.setLineWidth(self.thick)
        c.line(0, self.height/2, self.width, self.height/2)


# ──────────────── Page decoration ────────────────
def on_content_page(canvas_obj, doc):
    c = canvas_obj; c.saveState()
    c.setFont("Helvetica-Bold", 8); c.setFillColor(MUTED)
    c.drawString(MARGIN_X, PAGE_H-12*mm, GUIDE_TITLE)
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W-MARGIN_X, PAGE_H-12*mm, CANDIDATE)
    c.setStrokeColor(HAIR); c.setLineWidth(0.6)
    c.line(MARGIN_X, PAGE_H-14*mm, PAGE_W-MARGIN_X, PAGE_H-14*mm)
    c.line(MARGIN_X, 12*mm, PAGE_W-MARGIN_X, 12*mm)
    c.setFont("Helvetica", 8); c.setFillColor(MUTED)
    c.drawString(MARGIN_X, 8.4*mm, "Interview Preparation · "+YEAR)
    c.drawRightString(PAGE_W-MARGIN_X, 8.4*mm, "Page %d" % doc.page)
    c.restoreState()


def on_cover_page(canvas_obj, doc):
    c = canvas_obj; c.saveState()
    steps = 140; c1 = (0x0B,0x12,0x20); c2 = (0x1E,0x1B,0x4B)
    band = PAGE_H / steps
    for i in range(steps):
        t = i/(steps-1)
        r = (c1[0]+(c2[0]-c1[0])*t)/255
        g = (c1[1]+(c2[1]-c1[1])*t)/255
        b = (c1[2]+(c2[2]-c1[2])*t)/255
        c.setFillColor(Color(r,g,b))
        c.rect(0, PAGE_H-(i+1)*band, PAGE_W, band+1, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#334155")); c.setLineWidth(0.8)
    c.line(MARGIN_X, PAGE_H-16*mm, PAGE_W-MARGIN_X, PAGE_H-16*mm)
    cols = ["#2563EB","#7C3AED","#0891B2","#DB2777","#EA580C",
            "#16A34A","#0D9488","#DC2626","#4F46E5","#9333EA"]
    spacing = (PAGE_W-2*MARGIN_X)/(len(cols)-1)
    for i, hexc in enumerate(cols):
        c.setFillColor(HexColor(hexc))
        c.circle(MARGIN_X+i*spacing, 22*mm, 2.6*mm, fill=1, stroke=0)
    c.restoreState()


def lang_label(lang):
    return {"tsx":"TypeScript / TSX","ts":"TypeScript","go":"Go",
            "sql":"SQL","yaml":"YAML","bash":"Shell / Bash",
            "js":"JavaScript","json":"JSON","dockerfile":"Dockerfile",
            }.get(lang, lang.upper())


# ──────────────── Extract from existing PDF ────────────────
def extract_qa_from_pdf(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    sections_meta = [
        (1, "React Native Core & Fundamentals", 1, 10),
        (2, "TypeScript & JavaScript (ES6+)", 11, 20),
        (3, "State Management & Data Fetching", 21, 30),
        (4, "Animations, Gestures & Performance", 31, 40),
        (5, "Native Modules & the New Architecture", 41, 50),
        (6, "Offline-First, SQLite, Geolocation & Background Tasks", 51, 60),
        (7, "Real-Time: WebSockets, WebRTC & CRDTs", 61, 70),
        (8, "AI / LLM Features on Mobile", 71, 80),
        (9, "Backend & Data", 81, 90),
        (10, "Payments, Releases, Testing & DevOps", 91, 100),
    ]

    q_pattern = re.compile(r'^Q(\d+)\n', re.MULTILINE)
    q_positions = [(m.start(), int(m.group(1)), m.end()) for m in q_pattern.finditer(full_text)]

    valid_q_positions = []
    for pos, qnum, end_pos in q_positions:
        remainder = full_text[end_pos:end_pos + 2000]
        if "THEORY\n" in remainder or "THEORY" in remainder[:500]:
            valid_q_positions.append((pos, qnum, end_pos))

    qa_items = {}
    for i, (pos, qnum, end_pos) in enumerate(valid_q_positions):
        block_end = valid_q_positions[i+1][0] if i+1 < len(valid_q_positions) else len(full_text)
        block = full_text[end_pos:block_end]
        item = parse_q_block(block, qnum)
        if item:
            qa_items[qnum] = item

    sections = []
    for sec_num, sec_title, q_start, q_end in sections_meta:
        items = []
        for qn in range(q_start, q_end + 1):
            if qn in qa_items:
                items.append(qa_items[qn])
            else:
                print(f"WARNING: Q{qn} not found in PDF extraction")
                items.append({"q": f"Question {qn}", "theory": "", "answer": "", "code": "", "lang": "tsx", "diagram": ""})
        sections.append({"section": sec_num, "title": sec_title, "items": items})
    return sections


def parse_q_block(block, qnum):
    block = re.sub(r'React Native Engineer — 100 Interview Q&A\n', '', block)
    block = re.sub(r'Mohammed Rinshad M I\n', '', block)
    block = re.sub(r'Interview Preparation · 2026\n', '', block)
    block = re.sub(r'Page \d+\n', '', block)

    theory_match = re.search(r'\nTHEORY\n', block)
    answer_match = re.search(r'\nSTRONG ANSWER\n', block)
    code_match = re.search(r'\nCODE\s+·\s+(.+?)\n', block)
    diag_match = re.search(r'\nARCHITECTURE / FLOW\n', block)

    if not theory_match or not answer_match:
        print(f"Q{qnum}: Could not find THEORY or STRONG ANSWER markers")
        return None

    section_headers = [
        "REACT NATIVE CORE & FUNDAMENTALS", "TYPESCRIPT & JAVASCRIPT (ES6+)",
        "STATE MANAGEMENT & DATA FETCHING", "ANIMATIONS, GESTURES & PERFORMANCE",
        "NATIVE MODULES & THE NEW ARCHITECTURE",
        "OFFLINE-FIRST, SQLITE, GEOLOCATION & BACKGROUND TASKS",
        "REAL-TIME: WEBSOCKETS, WEBRTC & CRDTS", "AI / LLM FEATURES ON MOBILE",
        "BACKEND & DATA", "PAYMENTS, RELEASES, TESTING & DEVOPS",
    ]
    pre_theory = block[:theory_match.start()].strip()
    question_text = pre_theory
    for header in section_headers:
        question_text = question_text.replace(header + "\n", "").replace(header, "")
    question_text = question_text.strip()

    theory = block[theory_match.end():answer_match.start()].strip()

    answer_start = answer_match.end()
    answer_end = code_match.start() if code_match else (diag_match.start() if diag_match else len(block))
    answer = block[answer_start:answer_end].strip()

    code = ""; lang = "tsx"
    if code_match:
        lang_raw = code_match.group(1).strip()
        if "continued" not in lang_raw: lang = lang_raw
        code_start = code_match.end()
        code_end = diag_match.start() if diag_match else len(block)
        code = block[code_start:code_end].strip()
        code = re.sub(r'CODE\s+·\s+.+?\(continued\)\n?', '', code)
        code = re.sub(r'React Native Engineer — 100 Interview Q&A\n?', '', code)
        code = re.sub(r'Mohammed Rinshad M I\n?', '', code)
        code = re.sub(r'Interview Preparation · 2026\n?', '', code)
        code = re.sub(r'Page \d+\n?', '', code)

    lang_map = {"TypeScript / TSX":"tsx","TypeScript":"ts","Go":"go","SQL":"sql",
                "YAML":"yaml","Shell / Bash":"bash","JavaScript":"js","JSON":"json","Dockerfile":"dockerfile"}
    lang = lang_map.get(lang, lang.lower().replace(" ", ""))

    diagram = ""
    if diag_match:
        diagram = block[diag_match.end():].strip()
        diagram = re.sub(r'ARCHITECTURE / FLOW\s+\(continued\)\n?', '', diagram)
        diagram = re.sub(r'React Native Engineer — 100 Interview Q&A\n?', '', diagram)
        diagram = re.sub(r'Mohammed Rinshad M I\n?', '', diagram)
        diagram = re.sub(r'Interview Preparation · 2026\n?', '', diagram)
        diagram = re.sub(r'Page \d+\n?', '', diagram)

    return {"q": question_text, "theory": theory, "answer": answer, "code": code, "lang": lang, "diagram": diagram}


# ──────────────── Replacement Answers Q26–Q50 ────────────────
REPLACEMENT_ANSWERS = {
    26: "React Query (TanStack Query) is a library for managing server state, which is data fetched from an API. It automatically handles data fetching, caching, loading states, error handling, and refetching, so I don't have to implement that logic myself. Server state is different from client state because it comes from the backend, can change at any time, and needs to stay in sync with the server. Client state is data that belongs to the app itself, such as theme, authentication status, or whether a modal is open. I use React Query for API data and Redux or Zustand for application state.",
    27: "React Query caches API responses using a unique queryKey, so if I revisit a screen, it can show cached data immediately instead of making another API call. staleTime defines how long the cached data is considered fresh. During that time, React Query won't refetch the data. Once the data becomes stale, it can automatically refetch in the background when needed, such as when the app regains focus or the query runs again. When I update data on the server, such as creating or editing an item, I use invalidateQueries() to mark the related query as stale. React Query then refetches the latest data, keeping the UI in sync with the server.",
    28: "useMutation is used for operations that change data on the server, such as creating, updating, or deleting items. It provides methods like mutate() along with loading and error states. For a better user experience, I use optimistic updates. Before the server responds, I immediately update the UI so the app feels faster. If the API call fails, I roll back the change. After the request completes, I invalidate the related query so React Query fetches the latest data from the server and keeps the UI in sync.",
    29: "It depends on the type of state I'm managing. I use React Query for server state, such as data from APIs, because it handles fetching, caching, loading, errors, and refetching automatically. For client state, I choose between Zustand and Redux Toolkit. Zustand is my choice for small to medium projects or simple global state because it's lightweight and easy to use. Redux Toolkit is better for large applications with complex state, where I need a structured architecture, middleware, and powerful debugging tools. In many real-world projects, I use React Query for API data and Zustand or Redux Toolkit for client state, letting each tool do what it's designed for.",
    30: "Normalizing state means storing data in a flat structure instead of deeply nested objects or arrays. Typically, I store items in an object using their id as the key and keep a separate array of IDs. This makes updates more efficient because when one item changes, I only update that item instead of replacing the entire collection. As a result, fewer components re-render, which improves performance. In Redux Toolkit, I can use createEntityAdapter to manage normalized state more easily.",
    31: "React Native mainly has two threads: the JavaScript (JS) thread and the UI thread. The JS thread runs my application logic, React components, API calls, and business logic. The UI thread is responsible for rendering the interface, handling touch events, and drawing frames on the screen. Animations can become janky when they're driven by the JS thread and that thread is busy with heavy work, such as large re-renders or expensive calculations. Since the JS thread can't send animation updates fast enough, the animation starts to stutter. To avoid this, I use the native driver when possible or React Native Reanimated, which runs animations directly on the UI thread. This keeps animations smooth even if the JS thread is busy.",
    32: "The Animated API is built into React Native and is suitable for simple animations like fading, scaling, or moving a component. When used with useNativeDriver, supported animations run on the native side, improving performance. Reanimated is a more powerful animation library. It runs animation logic on the UI thread, making it ideal for complex animations, gestures, and highly interactive user interfaces. It provides features like shared values, animated styles, and smooth gesture-based animations. I use the built-in Animated API for simple animations, and I choose Reanimated when I need high-performance animations, gesture handling, or more advanced animation features.",
    33: "useSharedValue creates a value that can be updated without causing a React re-render. I use it to store animated values like position, scale, or opacity. useAnimatedStyle uses those shared values to create animated styles. Whenever a shared value changes, the animated style updates automatically on the UI thread, making animations smooth and performant. Together, they let me build high-performance animations because updates happen on the UI thread instead of triggering React re-renders.",
    34: "A worklet is a function that runs on the UI thread instead of the JavaScript thread. Reanimated uses worklets to execute animation logic directly on the UI thread, which keeps animations smooth even when the JS thread is busy. runOnJS is used when a worklet needs to call JavaScript code, such as updating React state, navigating to another screen, or calling a normal JavaScript function. runOnUI does the opposite—it lets me start a worklet from the JavaScript thread. In short, worklets run on the UI thread, React state runs on the JS thread, runOnJS goes from UI → JS, and runOnUI goes from JS → UI.",
    35: "react-native-gesture-handler provides smooth and reliable gesture handling. For a pan gesture, I create a Gesture.Pan(), handle events like onUpdate and onEnd, and wrap the component with a GestureDetector. Inside the gesture callbacks, I update Reanimated shared values, and useAnimatedStyle uses those values to move the UI. Since the gesture and animation run on the UI thread, the interaction stays smooth even if the JavaScript thread is busy.",
    36: "Achieving 60 FPS means the app renders 60 frames every second, which gives users smooth animations and scrolling. Since one frame has about 16 milliseconds to render, any work that takes longer than that can cause dropped frames and make the UI feel laggy. Common causes are heavy JavaScript work, unnecessary re-renders, large lists, expensive layouts, and JavaScript-driven animations. To avoid dropped frames, I optimize re-renders with React.memo, useMemo, and useCallback, use FlatList or FlashList for large lists, and use Reanimated or the native driver so animations run on the UI thread.",
    37: "By default, when a parent component re-renders, its child components also re-render. To avoid unnecessary re-renders, I use React.memo, useCallback, and useMemo when they provide a real performance benefit. React.memo prevents a child component from re-rendering if its props haven't changed. useCallback memoizes functions so their reference stays the same when passing them to child components. useMemo memoizes expensive calculations or objects so they aren't recreated on every render. I don't use them everywhere. I use them only when profiling shows unnecessary re-renders, especially in list items or performance-critical screens.",
    38: "FlatList is already optimized with virtualization, but for large lists I tune a few important props. keyExtractor provides a stable key for each item, helping React update the list efficiently. getItemLayout is useful when all items have the same height because it skips measuring and improves scrolling and scrollToIndex performance. windowSize controls how many items are rendered around the visible area, helping balance performance and memory usage. removeClippedSubviews removes off-screen views, reducing memory usage, especially on Android. I also memoize the renderItem component using React.memo and adjust props like initialNumToRender and maxToRenderPerBatch for very large lists.",
    39: "Hermes is the JavaScript engine optimized for React Native and is the default engine in modern React Native apps. Its main goal is to improve app performance. Hermes compiles JavaScript into bytecode during the build process, so the app starts faster because it doesn't need to parse and compile all the JavaScript at launch. It also reduces memory usage and can decrease app size. I use Hermes because it improves startup performance, makes the app more responsive, and works well with React Native debugging and profiling tools.",
    40: "My approach is to measure first and optimize second. I don't guess where the problem is. I start with the React Native Performance Monitor to check if the JS thread or UI thread is dropping frames. If I suspect unnecessary re-renders, I use React DevTools or the React Profiler to identify which components are rendering too often. For deeper performance analysis, I use Flipper and Hermes profiling tools to inspect CPU usage and overall app performance. Once I identify the bottleneck, I apply the appropriate optimization, such as reducing re-renders, optimizing lists, or moving animations to Reanimated, and then I profile again to verify the improvement.",
    41: "A native module is a way for React Native's JavaScript code to communicate with native Android or iOS code. I use it when I need access to platform-specific features or native SDKs that aren't available through React Native or an existing library. For example, if I need to integrate a payment SDK, a Bluetooth device, advanced camera features, or a custom native API, I would write a native module. Otherwise, I prefer using existing community libraries because they save development time and are well tested.",
    42: "In the old React Native architecture, the JavaScript thread and the native side were separated and communicated through a bridge. Whenever JavaScript needed to interact with native code, the data had to be serialized, sent across the bridge, and deserialized on the other side. The main problem was performance. Frequent communication, large amounts of data, or JavaScript-driven animations could overload the bridge, causing delays, dropped frames, and janky animations. The new React Native architecture replaces the bridge with JSI, which allows JavaScript to communicate directly with native code without serialization, making interactions faster and more efficient.",
    43: "JSI, or JavaScript Interface, is the technology behind React Native's New Architecture. It allows JavaScript to communicate directly with native code without going through the old bridge. In the old architecture, data had to be serialized and sent across the bridge. With JSI, JavaScript can call native functions directly, which makes communication much faster and reduces latency. JSI is the foundation for TurboModules and Fabric, helping React Native deliver better performance and a smoother user experience.",
    44: "TurboModules are the new way of writing native modules in React Native's New Architecture. Compared to the old native modules, they're faster and more efficient because they use JSI instead of the bridge. The old native modules were loaded when the app started, and every call had to go through the bridge. TurboModules are loaded only when they're actually needed (lazy loading), and JavaScript communicates with them directly through JSI. This improves startup time and overall performance. They also support code generation, which provides better type safety between JavaScript and native code.",
    45: "Fabric is React Native's new rendering system and part of the New Architecture. Its job is to convert React components into native UI elements like UIView on iOS or android.view on Android. The old rendering system relied on the bridge, which could introduce delays and dropped frames. Fabric uses JSI for more direct communication with native code, making rendering faster and more efficient. It also works better with modern React features like concurrent rendering and Suspense. As a result, Fabric provides smoother UI updates, better performance, and a more responsive user experience.",
    46: "Codegen is a tool in React Native's New Architecture that automatically generates native code from a TypeScript specification. I define a TypeScript interface describing the methods, parameters, and return types of a native module or component. Codegen then generates the corresponding native code for iOS and Android. This keeps the JavaScript and native sides in sync and provides type safety. If the interface changes and the native implementation isn't updated, the build fails instead of causing runtime errors.",
    47: "To create a native module in Swift, I create a class that extends NSObject and expose it to React Native using @objc. I then expose the methods I want JavaScript to call. React Native registers the module, allowing JavaScript to access it. On the JavaScript side, I import the module from NativeModules and call its methods just like any other JavaScript function. If the operation is asynchronous, I expose it as a Promise so it can be used with async/await. In practice, I only write native modules when I need to integrate a native SDK or access platform-specific features that aren't available through existing React Native libraries.",
    48: "I write a native module when I only need native functionality, but if I need to display a native UI component, I wrap it as a native view using a ViewManager. A ViewManager creates and manages the native view, exposes its properties to JavaScript, and sends native events back to JavaScript. This lets React Native use native UI components just like built-in components. Examples include maps, video players, camera previews, or other platform-specific UI components. In the New Architecture, this is handled through Fabric and Codegen.",
    49: "Autolinking is a React Native feature that automatically connects native libraries to your iOS and Android projects. Before autolinking, developers had to manually update Xcode and Gradle files whenever they installed a native package. Now, after installing a library and running pod install on iOS or rebuilding the app, React Native detects the native module and links it automatically. Once linked, the module is available in JavaScript through NativeModules or the library's API. One important thing to remember is that adding a native module requires a native rebuild—it won't work with just a Metro reload.",
    50: "JavaScript and native code run on different threads and communicate with each other. Native code performs its work and then sends the result back to JavaScript. For communication, I choose the approach based on the use case: Promises for a single asynchronous result, like fetching data or starting audio playback. Callbacks for simple one-time responses, though they're less common today. Events when native needs to continuously send updates, such as download progress, location updates, or audio playback progress. In general, I prefer Promises for one-time operations and Events for ongoing updates.",
}


# ──────────────── Section blurbs ────────────────
SECTION_BLURBS = {
    1: "Components, JSX, hooks, lists, layout, platform code and re-renders.",
    2: "Types vs interfaces, generics, utility types, async, and the JS to TS migration.",
    3: "Context, Redux Toolkit, thunks, selectors, React Query caching & mutations.",
    4: "Threads, Reanimated worklets, gestures, 60fps, memoization & profiling.",
    5: "Bridge vs JSI, TurboModules, Fabric, Codegen and Swift native modules.",
    6: "SQLite, outbox/sync, background geolocation, backoff and idempotency.",
    7: "WebSockets, reconnection, Yjs CRDTs, presence, WebRTC and scaling.",
    8: "Streaming chat, on-device Whisper, tool calling, RAG, embeddings & VAD.",
    9: "REST, Express, JWT rotation, SQL vs NoSQL, indexing, Redis & idempotency.",
    10: "Payments & webhooks, signing, staged rollout, Fastlane, CI/CD, tests, Sentry.",
}


# ──────────────── Build ────────────────
def build(sections):
    total_q = sum(len(s["items"]) for s in sections)
    story = []

    # ─── COVER ───
    story.append(Spacer(1, 40*mm))
    cap = mkstyle("cap", fontName="Helvetica-Bold", fontSize=11,
                  textColor=HexColor("#93C5FD"), alignment=TA_CENTER, leading=14)
    story.append(Paragraph("INTERVIEW PREPARATION GUIDE", cap))
    story.append(Spacer(1, 6*mm))
    title = mkstyle("title", fontName="Helvetica-Bold", fontSize=33,
                    textColor=white, alignment=TA_CENTER, leading=38)
    story.append(Paragraph("100 React Native", title))
    story.append(Paragraph("Interview Q&amp;A", title))
    story.append(Spacer(1, 5*mm))
    sub = mkstyle("sub", fontName="Helvetica", fontSize=12.5,
                  textColor=HexColor("#C7D2FE"), alignment=TA_CENTER, leading=18)
    story.append(Paragraph("Theory · Strong Answers · Example Code · Architecture Diagrams", sub))
    story.append(Spacer(1, 30*mm))

    stat_tbl = Table(
        [["100","10","85+","6"],["Questions","Sections","Diagrams","Languages"]],
        colWidths=[CONTENT_W/4]*4)
    stat_tbl.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,0),24),
        ("TEXTCOLOR",(0,0),(-1,0),white), ("FONTNAME",(0,1),(-1,1),"Helvetica"),
        ("FONTSIZE",(0,1),(-1,1),9), ("TEXTCOLOR",(0,1),(-1,1),HexColor("#A5B4FC")),
        ("ALIGN",(0,0),(-1,-1),"CENTER"), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,0),0), ("BOTTOMPADDING",(0,0),(-1,0),12),
        ("TOPPADDING",(0,1),(-1,1),0),
    ]))
    story.append(stat_tbl)
    story.append(Spacer(1, 24*mm))
    namest = mkstyle("name", fontName="Helvetica-Bold", fontSize=15, textColor=white, alignment=TA_CENTER)
    rolest = mkstyle("role", fontName="Helvetica", fontSize=9.5,
                     textColor=HexColor("#94A3B8"), alignment=TA_CENTER, leading=14, spaceBefore=3)
    story.append(Paragraph("Prepared for " + CANDIDATE, namest))
    story.append(Paragraph(ROLE + "  ·  " + YEAR, rolest))
    story.append(PageBreak())

    # ─── HOW TO USE ───
    h2 = mkstyle("h2", fontName="Helvetica-Bold", fontSize=17, textColor=INK, spaceAfter=4)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("How to Use This Guide", h2))
    story.append(Spacer(1, 1.5*mm))
    story.append(HRule(thick=1.2, color=THEORY_AC, pad=2))
    story.append(Spacer(1, 4*mm))
    intro = mkstyle("intro", fontName="Helvetica", fontSize=9.6, leading=15, textColor=INK_SOFT)
    story.append(Paragraph(
        "This guide turns your resume into <b>100 realistic, interview-ready "
        "questions</b> across the full stack you actually work in "
        "— React Native, TypeScript, native modules, real-time, AI/LLM features, "
        "backend, payments and DevOps. Every question is answered in four "
        "layers so you understand it, not just memorise it:", intro))
    story.append(Spacer(1, 4*mm))

    legend = [
        ("THEORY", "The concept and the <i>why</i> — what the interviewer is really probing for.", THEORY_AC, THEORY_BG),
        ("ANSWER", "A natural, confident spoken answer you can deliver out loud. <b>Bold</b> terms are keywords to land.", ANSWER_AC, ANSWER_BG),
        ("CODE", "A concise, correct example — what good looks like in real code.", CODE_LABEL, CODE_BG),
        ("ARCHITECTURE", "An ASCII diagram of the flow or system, so you can draw it on a whiteboard.", DIAG_LABEL, DIAG_BG),
    ]
    for lab, desc, ac, bg in legend:
        chip_p = Paragraph("<b>%s</b>" % lab, mkstyle("lg", fontName="Helvetica-Bold", fontSize=8.5, textColor=white, alignment=TA_CENTER))
        desc_p = Paragraph(desc, BODY)
        t = Table([[chip_p, desc_p]], colWidths=[30*mm, CONTENT_W-30*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,0),ac), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(1,0),(1,0),8), ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6), ("ROUNDEDCORNERS",[4,4,4,4]),
            ("LINEBELOW",(1,0),(1,0),0.5,HAIR),
        ]))
        story.append(t); story.append(Spacer(1, 3*mm))

    story.append(Spacer(1, 4*mm))
    tip = LabeledBox("Pro tip", Paragraph(
        "Read the <b>answers out loud</b>. Interviews reward fluent delivery, not perfect recall. "
        "When you give a number from your resume (35% latency cut, 30% faster delivery), have a "
        "one-line 'how I measured it' ready for the follow-up.", BODY),
        bg=HexColor("#FEF9C3"), accent=HexColor("#CA8A04"))
    story.append(tip)

    # ─── CONTENTS ───
    story.append(PageBreak())
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Contents", h2))
    story.append(Spacer(1, 1.5*mm))
    story.append(HRule(thick=1.2, color=THEORY_AC, pad=2))
    story.append(Spacer(1, 5*mm))
    qstart = 1
    for s in sections:
        idx = s["section"]; color = SECTION_COLORS[idx-1]; n = len(s["items"])
        qrange = "Q%d–Q%d" % (qstart, qstart+n-1); qstart += n
        numchip = Paragraph("<b>%d</b>" % idx, mkstyle("tocn", fontName="Helvetica-Bold", fontSize=13, textColor=white, alignment=TA_CENTER))
        titlep = Paragraph("<b>%s</b>" % s["title"], mkstyle("toct", fontName="Helvetica-Bold", fontSize=11, textColor=INK))
        blurbp = Paragraph(SECTION_BLURBS.get(idx,""), mkstyle("tocb", fontName="Helvetica", fontSize=8.2, textColor=MUTED, leading=11))
        rangep = Paragraph(qrange, mkstyle("tocr", fontName="Helvetica-Bold", fontSize=9.5, textColor=color, alignment=TA_CENTER))
        inner = Table([[titlep],[blurbp]], colWidths=[CONTENT_W-14*mm-24*mm])
        inner.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(0,0),0),("BOTTOMPADDING",(0,0),(0,0),1),("TOPPADDING",(0,1),(0,1),0)]))
        row = Table([[numchip,inner,rangep]], colWidths=[14*mm, CONTENT_W-14*mm-24*mm, 24*mm])
        row.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),color),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("VALIGN",(1,0),(1,0),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(1,0),(1,0),9),("ROUNDEDCORNERS",[5,5,5,5]),("LINEBELOW",(1,0),(2,0),0.6,HAIR)]))
        story.append(row); story.append(Spacer(1, 2.6*mm))

    # ─── SECTIONS ───
    qnum = 0
    for s in sections:
        idx = s["section"]; color = SECTION_COLORS[idx-1]; n = len(s["items"])
        qrange = "Q%d–Q%d" % (qnum+1, qnum+n)
        story.append(PageBreak())
        story.append(SectionBanner(idx, s["title"], SECTION_BLURBS.get(idx,""), color, qrange))
        story.append(Spacer(1, 6*mm))

        for it in s["items"]:
            qnum += 1
            head = [
                QBadge(qnum, s["title"], color), Spacer(1, 1.6*mm),
                Paragraph(md_to_para(it["q"]), QSTYLE), Spacer(1, 2.4*mm),
                LabeledBox("Theory", Paragraph(md_to_para(it["theory"]), BODY_T), bg=THEORY_BG, accent=THEORY_AC),
            ]
            story.append(KeepTogether(head))
            story.append(Spacer(1, 2.4*mm))
            story.append(LabeledBox("Strong Answer", Paragraph(md_to_para(it["answer"]), BODY_A), bg=ANSWER_BG, accent=ANSWER_AC))
            story.append(Spacer(1, 2.4*mm))

            code_text = it.get("code","").strip()
            if code_text:
                code_lines = wrap_code(code_text)
                story.append(MonoBlock(code_lines, "CODE  ·  "+lang_label(it.get("lang","tsx")),
                    bg=CODE_BG, fg=CODE_FG, label_color=CODE_LABEL, comment_color=CODE_COMM))

            diag = it.get("diagram","").strip("\n")
            if diag.strip():
                story.append(Spacer(1, 2.4*mm))
                dlines = wrap_code(diag, max_chars=CODE_MAXCHARS)
                story.append(MonoBlock(dlines, "ARCHITECTURE / FLOW",
                    bg=DIAG_BG, fg=DIAG_FG, label_color=DIAG_LABEL, font_size=7.2, leading=9.4))

            story.append(Spacer(1, 4*mm))
            story.append(HRule(thick=0.6, color=HAIR))
            story.append(Spacer(1, 4*mm))

    return story, total_q


def main():
    print("Step 1: Extracting Q&A from existing PDF...")
    sections = extract_qa_from_pdf(SRC_PDF)
    total_extracted = sum(len(s["items"]) for s in sections)
    print(f"  Extracted {total_extracted} questions across {len(sections)} sections")

    print("\nStep 2: Replacing answers for Q26–Q50...")
    qnum = 0
    for section in sections:
        for item in section["items"]:
            qnum += 1
            if qnum in REPLACEMENT_ANSWERS:
                item["answer"] = REPLACEMENT_ANSWERS[qnum]
                print(f"  ✓ Q{qnum} answer replaced")

    print(f"\nStep 3: Building PDF...")
    story, total_q = build(sections)

    doc = BaseDocTemplate(OUT_PATH, pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B,
        title="100 React Native Interview Q&A — " + CANDIDATE, author=CANDIDATE)

    cover_frame = Frame(MARGIN_X, MARGIN_B, CONTENT_W, PAGE_H-MARGIN_B-8*mm,
                        id="cover", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    content_frame = Frame(MARGIN_X, MARGIN_B, CONTENT_W, PAGE_H-MARGIN_T-MARGIN_B-4*mm,
                          id="content", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=on_cover_page),
        PageTemplate(id="Content", frames=[content_frame], onPage=on_content_page),
    ])

    final = [NextPageTemplate("Content")]
    final.extend(story)
    doc.build(final)

    size = os.path.getsize(OUT_PATH)
    print(f"\n✅ Built {OUT_PATH}")
    print(f"   {total_q} questions, {size/1024:.0f} KB")


if __name__ == "__main__":
    main()
