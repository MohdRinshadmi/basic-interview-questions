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


# ──────────────── Replacement Answers Q51–Q100 ────────────────
REPLACEMENT_ANSWERS = {
    51: "Offline-first means the app continues to work even when there's no internet connection. Instead of depending on the network, it stores data locally first and syncs it with the server when the connection is available again. This improves the user experience because the app remains fast and responsive, and users don't lose their work due to poor connectivity. It's especially useful for apps like messaging, field service, delivery, or location tracking.",
    52: "I choose the storage solution based on the type and amount of data. For simple key-value data like user preferences, tokens, or app settings, I use AsyncStorage or MMKV. If performance is important, I prefer MMKV because it's much faster. For structured or large amounts of data, such as offline records, chat messages, or location history, I use SQLite because it supports tables, queries, indexes, and transactions.",
    53: "To use SQLite in React Native, I first open the database and create the required tables if they don't already exist. Then I perform CRUD operations using SQL queries. INSERT adds new records, SELECT reads data, UPDATE modifies existing records, and DELETE removes records. I always use parameterized queries to avoid SQL injection and use transactions when inserting or updating multiple records for better performance.",
    54: "I would use an outbox pattern where every offline action is first saved locally instead of being sent directly to the server. When the device comes back online, a background sync process reads the pending items one by one, sends them to the server, and marks them as completed or removes them from the queue. This makes the app reliable because users can continue working offline, no data is lost if the app closes, and failed requests can be retried automatically.",
    55: "The sync strategy depends on the type of data. For append-only data, like location history or chat messages, I simply sync new records because they don't overwrite existing data. For editable data, I usually use a Last-Write-Wins (LWW) strategy, where the latest update from the server is treated as the source of truth. For more critical data, I use versioning or timestamps so the server can detect conflicts and ask the client to fetch the latest data before updating. The goal is to keep the device and server consistent while preventing data loss.",
    56: "For background location tracking, I use a dedicated background geolocation library that works with native Android and iOS services. This allows the app to continue receiving location updates even when it's in the background. Whenever a new location is received, I save it immediately to local storage, such as SQLite, and then sync it with the server when the device has network connectivity. I also configure update intervals and distance filters to balance location accuracy with battery usage.",
    57: "Background tasks are controlled by the operating system, so an app can't assume it will always run in the background. On iOS, background execution is limited, and the system decides when background tasks can run. On Android, long-running background work, like continuous location tracking, typically requires a foreground service with a persistent notification. To work within these constraints, I save important data locally as soon as it's available and make background sync resumable. Whenever the app gets a chance to run—whether in the background or when it returns to the foreground—I sync any pending data with the server.",
    58: "When syncing fails because of a network issue, I don't retry immediately. Instead, I use exponential backoff, where the delay between retries increases after each failure. This reduces unnecessary requests and gives the network or server time to recover. I also add a small random delay, called jitter, so multiple devices don't retry at the same time. If the device is offline, I keep the data safely in local storage and retry when the network becomes available.",
    59: "I use @react-native-community/netinfo to monitor the device's network status. I subscribe to connectivity changes, and when the device comes back online, I automatically start syncing any pending data. I check both isConnected and isInternetReachable because being connected to Wi-Fi or mobile data doesn't always mean the internet is actually accessible. To avoid unnecessary sync attempts on unstable networks, I debounce or limit repeated sync triggers.",
    60: "To ensure data integrity, I make every offline record have a unique client-generated ID, such as a UUID. When the app syncs, the server uses that ID to identify duplicate requests. If the same request is received again, the server ignores it or updates the existing record instead of creating a duplicate. On the client, I only remove an item from the offline queue after the server confirms it was processed successfully. This ensures data isn't lost if the network fails during syncing.",
    61: "I choose the technology based on how real-time the feature needs to be and whether communication is one-way or two-way. HTTP Polling is good for data that changes occasionally, like refreshing a dashboard every minute. Long Polling is useful when the server should respond only when new data is available, reducing unnecessary requests. Server-Sent Events (SSE) are ideal when only the server needs to continuously push updates to the client, such as live notifications or stock prices. WebSockets are my choice for true real-time, two-way communication, like chat, typing indicators, video calls, multiplayer games, or collaborative editing.",
    62: "A WebSocket connection starts as a normal HTTP request. The client asks the server to upgrade the connection to WebSocket. If the server accepts, it responds with a 101 Switching Protocols status, and the connection stays open. After that, both the client and server can send messages to each other at any time without creating new HTTP requests. This full-duplex communication makes WebSockets ideal for real-time features like chat, live collaboration, typing indicators, and video calls.",
    63: "React Native has a built-in WebSocket API, so the setup is similar to the web. I create the WebSocket connection inside useEffect, listen for events like onopen, onmessage, onerror, and onclose, and store the socket in a useRef so it persists across re-renders. To send a message, I first check that the connection is open using readyState, then call send(). Finally, I close the socket in the useEffect cleanup function to avoid memory leaks or multiple active connections when the user leaves the screen.",
    64: "On mobile, network connections can drop frequently, so I always implement automatic reconnection. If the WebSocket disconnects, I reconnect using exponential backoff with a small random delay (jitter) to avoid overwhelming the server. I also use a heartbeat mechanism by periodically sending a ping and expecting a pong response. If no response is received within a certain time, I assume the connection is stale, close it, and let the reconnection logic establish a new connection. After reconnecting, I re-authenticate or re-subscribe to the required channels so the app continues working seamlessly.",
    65: "A CRDT (Conflict-free Replicated Data Type) is a data structure that allows multiple users to edit the same data at the same time, even while offline. When their changes are synchronized later, the CRDT automatically merges them without losing anyone's changes. It's commonly used in collaborative apps like shared documents, whiteboards, or note-taking apps. Instead of manually resolving conflicts, the CRDT ensures all users eventually see the same final state.",
    66: "Yjs is a CRDT library that makes real-time collaboration easy. The main object is a Y.Doc, which represents a shared document. Inside it, you use shared types like Y.Text, Y.Map, or Y.Array to store collaborative data. Whenever someone edits the data, Yjs creates a small update. These updates are sent to other users, and Yjs automatically merges them so everyone stays in sync. A provider is responsible for transporting those updates. For example, a WebSocket provider sends updates between clients through a server, allowing everyone in the same room to see changes in real time.",
    67: "For live presence and typing indicators, I keep that data separate from the actual document because it's temporary and doesn't need to be saved. I use Yjs Awareness to share each user's presence, such as their name, cursor position, or online status. For typing indicators, I send an isTyping status while the user is typing and clear it after a short delay using a debounce timer. If a user disconnects, Yjs automatically removes their presence information, so there are no stale typing indicators or ghost users.",
    68: "With Yjs, users can continue editing even when they're offline. Their changes are stored locally, so no work is lost. When the device reconnects, Yjs exchanges only the missing updates with the server and other clients. Because Yjs is based on CRDTs, it automatically merges offline and online changes without conflicts, ensuring every user eventually sees the same document.",
    69: "WebRTC is a technology that lets two devices communicate directly for real-time audio, video, or data. The connection starts with signaling, where the two devices exchange information like offers, answers, and ICE candidates through a server, usually using WebSockets. Once both devices have that information, they create an RTCPeerConnection. To establish the best network path, WebRTC first tries a STUN server to discover each device's public IP address. If a direct connection isn't possible because of NAT or firewalls, it falls back to a TURN server, which relays the media. After the peer connection is established, the voice data flows directly between the devices whenever possible, giving low latency and reducing server load.",
    70: "When you have multiple backend servers, each server only knows about the clients connected to it. If one user sends a real-time message, the other users might be connected to different servers. To solve this, all servers communicate through a shared messaging system like Redis Pub/Sub. When one server receives an event, it publishes it to Redis, and the other servers receive it and forward it to their connected clients. For very large systems that need message persistence and guaranteed delivery, I'd use a message broker like Kafka instead of Redis.",
    71: "LLM streaming means the AI sends its response one small piece (or token) at a time instead of waiting until the entire answer is generated. The client receives these tokens continuously and updates the UI in real time. I prefer streaming because it greatly improves the user experience. Users see the response almost immediately instead of waiting several seconds for the complete answer. It's especially useful for chat apps and AI assistants, where responsiveness is important.",
    72: "In React Native, I use Server-Sent Events (SSE) to receive the AI response as it's generated. I open the stream, listen for incoming messages, and append each chunk of text to the current assistant message so the response appears gradually, just like ChatGPT. To keep the UI smooth, I avoid updating React state for every token. Instead, I batch incoming tokens and update the UI at short intervals. I also handle errors, close the stream when it's finished, and allow the user to cancel the response if needed.",
    73: "I prefer on-device speech-to-text with Whisper because it's faster, more private, and works even without an internet connection. Since the audio is processed locally, the user's voice never leaves the device, which improves privacy and reduces network latency. The trade-off is that the model increases the app size and uses more CPU, so I choose a smaller, optimized model that provides a good balance between speed and accuracy.",
    74: "For text-to-speech, I use the device's native TTS engine to convert the AI's response into speech. As the AI generates its response, I queue complete sentences for playback instead of waiting for the entire response. This allows the assistant to start speaking almost immediately, making the conversation feel more natural. I also manage playback properly by stopping the current speech if the user interrupts or starts speaking again, ensuring a smooth voice interaction.",
    75: "Tool calling, also called function calling, allows an LLM to use external functions or APIs when it needs information it doesn't already know. Instead of guessing an answer, the model requests a tool with the required parameters. My application validates those parameters, executes the actual function or API call, sends the result back to the model, and then the model generates the final response using that real data.",
    76: "RAG (Retrieval-Augmented Generation) is a technique where an LLM retrieves relevant information from an external knowledge source before generating an answer. Instead of relying only on what the model learned during training, it uses real, up-to-date data to answer questions. It's useful because it reduces hallucinations, allows the AI to answer questions about private or company-specific documents, and keeps responses accurate without retraining the model.",
    77: "Embeddings are numerical representations of text that capture its meaning. Similar texts have similar embeddings. When a user asks a question, I convert it into an embedding and compare it with the stored document embeddings to find the most relevant content. For similarity search, I typically use cosine similarity because it measures how semantically close two embeddings are. I store the embeddings in a vector database such as PostgreSQL with pgvector. As the dataset grows, I use an HNSW index to make nearest-neighbor searches much faster while maintaining high accuracy.",
    78: "When working with LLMs, I focus on three things: a clear system prompt, relevant context, and token limits. The system prompt defines the assistant's role and behavior. Before sending a user question, I inject only the relevant context, such as retrieved documents or recent conversation, so the model has the information it needs. I also keep the prompt within the model's token limit by including only the most relevant context or summarizing older messages. This improves accuracy, reduces cost, and keeps responses fast.",
    79: "When using free-tier LLM APIs, I focus on reducing unnecessary API calls and keeping responses fast. I cache embeddings and repeated responses so I don't make the same request twice. I also keep prompts concise to reduce token usage and cost. For a better user experience, I use streaming so users see responses immediately. I also handle rate limits by retrying with exponential backoff, and if one provider is unavailable, I fall back to another provider whenever possible.",
    80: "Voice Activity Detection (VAD) detects when a user starts and stops speaking. Instead of recording continuously or requiring a button press, it automatically captures only the spoken audio. Once the user finishes speaking, the recorded audio is sent to Whisper for speech-to-text. The transcribed text is then sent to the LLM, which generates a response. Finally, the response is converted into speech using a TTS engine. If the user starts speaking again while the assistant is talking, I stop the current speech so the conversation feels natural.",
    81: "I design REST APIs around resources, not actions. For example, I use /users or /orders instead of URLs like /getUsers. The HTTP method defines the action: GET for reading, POST for creating, PUT or PATCH for updating, and DELETE for removing data. I also use appropriate HTTP status codes, such as 200 for success, 201 for creation, 400 for invalid requests, 401 for unauthorized access, 403 for forbidden access, 404 when a resource isn't found, and 500 for server errors. Keeping response formats and status codes consistent makes the frontend easier to build and maintain.",
    82: "Express middleware is a function that runs before a request reaches the route handler. It can inspect or modify the request, send a response, or pass control to the next middleware using next(). I use middleware for common tasks like parsing JSON, authentication, logging, validation, and error handling. This keeps my route handlers focused on business logic and makes the code more reusable and easier to maintain.",
    83: "In JWT authentication, an access token is a short-lived token that's sent with every API request to prove the user is authenticated. A refresh token is long-lived and is used only to request a new access token when the current one expires, so the user doesn't have to log in again. For security, I store the refresh token in secure storage, such as the Keychain on iOS or the Keystore on Android, and keep the access token in memory since it expires quickly.",
    84: "Refresh-token rotation means that every time a client uses a refresh token, the server invalidates it and issues a brand-new refresh token. This ensures that a refresh token can only be used once. Each refresh token belongs to a token family that represents a user's session. If an old refresh token is used again after it has already been rotated, the server knows that the token has likely been stolen or replayed. In that case, it revokes the entire token family, forcing the user to log in again and preventing an attacker from continuing to refresh access tokens.",
    85: "Passwords should never be stored in plain text. I hash them using a strong password hashing algorithm like bcrypt, which automatically adds a unique salt and is intentionally slow to make brute-force attacks difficult. I store only the hash in the database and verify passwords using bcrypt.compare() during login. For application secrets, such as JWT signing keys or database credentials, I never hardcode them in the source code. Instead, I store them securely in environment variables or a secrets manager, use different secrets for different environments, and rotate them periodically. I also keep access-token and refresh-token signing keys separate so compromising one doesn't automatically compromise the other.",
    86: "I choose PostgreSQL when the data is highly relational and consistency is important. It's ideal for applications like e-commerce, banking, or user management because it provides ACID transactions, foreign keys, joins, and powerful SQL queries. I choose MongoDB when the data is document-oriented or the schema changes frequently. It's a good fit for content management systems, logs, event data, or applications where each record is mostly self-contained. The choice depends on the data model, query patterns, and consistency requirements rather than which database is generally better.",
    87: "I always start by measuring before optimizing. I identify slow queries using query logs and EXPLAIN ANALYZE to understand whether the database is using indexes or performing full table scans. For the slowest queries, I added indexes that matched the application's filtering and sorting patterns, eliminated N+1 queries by replacing multiple database calls with joins or batched queries, and cached read-heavy data in Redis. After each change, I measured the performance again to verify the improvement. Together, these optimizations reduced API latency by about 35%.",
    88: "Redis is an in-memory data store that I use for caching, session storage, rate limiting, and other fast-access data. Its low latency makes it ideal for data that's read or updated frequently. For rate limiting in a distributed system, I store request counters in Redis instead of application memory. Since all application instances share the same Redis server, every request updates the same counter regardless of which server handles it. I use an atomic operation—often with a Lua script—to increment the counter and set its expiration in one step, ensuring the rate limit remains accurate even under high concurrency.",
    89: "When dealing with concurrent requests, my goal is to ensure data stays correct even if multiple clients act at the same time. I rely on atomic database operations, optimistic locking when appropriate, and idempotency for operations that may be retried. For example, instead of reading a value and then updating it in separate steps, I perform the check and update in a single SQL statement so the database guarantees correctness. For operations like payments or order creation, I use an idempotency key. If the same request is retried because of a network failure, the server returns the original result instead of performing the operation again. For distributed coordination, I use Redis-based locks only when a critical section cannot be safely handled by the database.",
    90: "I follow a defense-in-depth approach. First, I validate every request—body, path parameters, and query parameters—using a schema validation library like Zod before the request reaches the business logic. Invalid input is rejected immediately with a 400 Bad Request. For error handling, I use a centralized Express error-handling middleware that returns consistent error responses to the client while logging detailed errors on the server. I never expose stack traces or sensitive information in production. For API security, I enable security headers with Helmet, configure CORS with an allow-list of trusted origins, apply authentication and authorization where needed, rate-limit requests using Redis to prevent abuse, and validate pagination and request sizes to avoid resource exhaustion.",
    91: "The key principle is that the backend owns the payment process, not the mobile app. The React Native app sends the cart or product information to the backend, and the backend calculates the final amount and creates a payment order or PaymentIntent with the payment provider. It then returns only the information the client needs, such as a client secret or order ID, to open the native payment sheet. After the user completes the payment, I don't trust the client callback to mark the payment as successful. Instead, I wait for a server-side webhook from Stripe or Razorpay, verify the payment, and only then update the order status in the database. This prevents users from tampering with payment amounts or faking successful payments.",
    92: "A webhook is an HTTP callback sent directly from the payment provider to our backend whenever a payment event occurs. It's considered the source of truth because it comes from the payment provider—not the client application—and can be verified using a cryptographic signature. I never rely on the client callback to update payment status because the app could crash, lose network connectivity, or be tampered with after the payment completes. Instead, I verify the webhook's signature, confirm the payment details, and only then update the order or subscription in the database.",
    93: "Payment gateways can retry the same webhook multiple times if they don't receive a successful response, so webhook handlers must be idempotent. I use the gateway's unique event ID as an idempotency key and store it in a processed_events table with a unique constraint or primary key. When a webhook arrives, I first try to record its event ID. If it already exists, I know the event has been processed before, so I immediately return 200 OK without running the business logic again. I perform both the event recording and the business update inside a single database transaction, ensuring the webhook is either fully processed or not processed at all.",
    94: "I model subscriptions as a state machine, and I let server-side webhooks drive all state transitions. The client never decides the subscription status—it simply displays what the backend returns. During the trial and active states, the user has full access. If a renewal payment fails, the payment gateway changes the subscription to past_due. During this period, I usually keep access enabled while the gateway retries the payment (the dunning period), and I notify the user to update their payment method. If the retries still fail, the subscription moves to canceled. I don't revoke access immediately—I wait until the end of the current billing period so the user receives the service they've already paid for. One important lesson is to separate subscription status from access logic. For example, past_due doesn't necessarily mean the user should lose access immediately.",
    95: "App signing ensures that only trusted builds of my app can be published and updated. On Android, I use an upload key together with Play App Signing, where Google securely manages the app signing key and I use my upload key to sign releases. On iOS, I use Apple distribution certificates and provisioning profiles, and I automate certificate management with Fastlane Match so the team can share them securely. For store compliance, I make sure the app meets the latest platform requirements before release. That includes providing accurate privacy disclosures, requesting only the permissions the app actually needs, completing the App Store Privacy Nutrition Label and Google Play Data Safety form, targeting the required Android API level, and following both stores' review guidelines. Proper signing protects the app, while compliance ensures the release is approved.",
    96: "I automate releases with Fastlane so every build follows the same repeatable pipeline instead of relying on manual steps. My Fastlane lanes handle building, code signing, uploading to the App Store or Google Play, and triggering staged rollouts. For production releases, I don't deploy to 100% of users immediately. I start with a small rollout, typically 1–5%, and monitor crash-free sessions, error rates in Sentry, and key business metrics. If everything looks healthy, I gradually increase the rollout to 10%, 50%, and then 100%. If I detect an issue, I pause or halt the rollout before it affects the entire user base. Automating this process makes releases consistent, safer, and much easier to reproduce.",
    97: "I set up CI/CD using GitHub Actions with two main pipelines: a fast PR validation pipeline and a release pipeline. For pull requests, I run a lightweight workflow that installs dependencies, runs ESLint, TypeScript checks, and unit tests with Jest. This acts as a quality gate before merging. I also use caching for node_modules, Gradle, and CocoaPods to keep feedback fast—ideally within a few minutes. For releases, I trigger workflows on Git tags. The iOS build runs on a macOS GitHub runner because Xcode is required, and Android runs on Linux. Signing credentials are stored securely in GitHub Secrets and injected at build time, never committed to the repository. Finally, I integrate Fastlane into the pipeline so the same lanes used locally are executed in CI. Fastlane handles building, signing, and uploading to the App Store and Google Play, which ensures consistency and removes environment-specific release issues.",
    98: "I write tests using Jest and React Native Testing Library with a focus on testing user behavior rather than implementation details. Instead of accessing internal state or component methods, I query the UI the way a user would—using text, accessibility labels, and roles—and I trigger real user interactions like presses and input changes. I mock external dependencies such as network requests, APIs, and native modules to keep tests deterministic and fast. For asynchronous UI updates, I use findBy queries or waitFor to properly handle state changes after data loading. I also focus tests on critical business logic paths—like different subscription states or payment flows—so I cover scenarios where bugs would have real user impact, rather than trying to test every implementation detail.",
    99: "I use Detox for end-to-end testing of critical user journeys in a React Native app, such as onboarding, authentication, and payment flows. Unlike unit tests, Detox runs the actual app binary on a simulator or device and interacts with it like a real user would, using accessibility IDs to find elements and perform actions. A key advantage of Detox is that it is 'gray-box aware'—it understands when the app is busy with network requests, animations, or async work, so it automatically waits for the app to become idle instead of relying on manual delays, which reduces flakiness. I keep Detox tests focused on high-value flows like checkout or subscription purchase and run them in CI on a scheduled or nightly basis because they are slower and heavier than unit tests. Unit tests validate individual components and logic in isolation, while Detox validates the entire system from UI to backend integration.",
    100: "I set up Sentry at app startup with the correct release version and environment (development, staging, production). In CI, I upload source maps for JavaScript and dSYMs for iOS so that stack traces are properly symbolicated—otherwise crashes are unreadable minified code. When analyzing a crash, I start from the exception type and message, then look at the stack trace to identify whether it originates from our application code or a dependency. After that, I use breadcrumbs to understand the user's last actions leading up to the crash, such as navigation events, API calls, or UI interactions. I also check the release version, device model, and OS version to understand the scope of impact. During staged rollouts, I primarily monitor crash-free session rate per release. If I see a spike, I immediately pause or roll back the rollout. Breadcrumbs are often the most useful part because they help reproduce the exact user flow that caused the issue.",
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

    print("\nStep 2: Replacing answers for Q51–Q100...")
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
