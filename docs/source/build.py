# -*- coding: utf-8 -*-
"""Design system + page builders for the course PDF (HTML -> wkhtmltopdf)."""
import math
import os

# ---------- Design tokens ----------
PAPER = "#F6F4EE"
PAPER_DIM = "#ECE8DC"
INK = "#1B2430"
INK_SOFT = "#4B5563"
BLUEPRINT = "#2B5F8A"
BLUEPRINT_D = "#1F4A6E"
SIGNAL = "#B5502D"
LINE = "#C9C2AE"
NAVY = "#10192B"

EDITION = "Edition 01"
PREPARED = "October 2026"
REPO_URL = os.getenv("REPO_URL", "").strip()      # optional: stamped on cover/closing when set

MODULES = [
    "Introduction to AI Engineering", "LLMs", "Prompt Engineering", "OpenAI API",
    "Embeddings", "Vector Databases", "RAG", "Function Calling", "MCP",
    "AI Agents", "LangGraph", "Evaluation", "Production AI", "MLOps",
]
TOTAL = len(MODULES)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- SVG helpers ----------
def trace_rail(current_idx, width=680):
    """Signature motif: horizontal 14-node trace rail, current node lit."""
    n, pad, y = TOTAL, 14, 16
    step = (width - 2 * pad) / (n - 1)
    p = [f'<svg viewBox="0 0 {width} 32" width="{width}" height="32" class="rail">',
         f'<line x1="{pad}" y1="{y}" x2="{width - pad}" y2="{y}" stroke="{BLUEPRINT}" stroke-width="1.4" opacity="0.55"/>']
    for i in range(n):
        x = pad + step * i
        if i == current_idx:
            p.append(f'<circle cx="{x:.1f}" cy="{y}" r="6.4" fill="{SIGNAL}" stroke="{NAVY}" stroke-width="1"/>')
            p.append(f'<circle cx="{x:.1f}" cy="{y}" r="10.5" fill="none" stroke="{SIGNAL}" stroke-width="1" opacity="0.45"/>')
        elif i < current_idx:
            p.append(f'<circle cx="{x:.1f}" cy="{y}" r="3.6" fill="{BLUEPRINT}"/>')
        else:
            p.append(f'<circle cx="{x:.1f}" cy="{y}" r="3.2" fill="{PAPER}" stroke="{LINE}" stroke-width="1.2"/>')
    p.append("</svg>")
    return "\n".join(p)


def arrow_defs():
    return f'''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" fill="{BLUEPRINT}"/></marker></defs>'''


def flow_svg(steps, width=680, height=150, highlight_last=False):
    """Evenly spaced horizontal boxes connected by arrows."""
    n, margin, gap, box_h = len(steps), 26, 14, 62
    box_w = (width - 2 * margin - gap * (n - 1)) / n
    y = (height - box_h) / 2
    p = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="diagram">', arrow_defs()]
    for i, label in enumerate(steps):
        x = margin + i * (box_w + gap)
        last = i == n - 1 and highlight_last
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{box_w:.1f}" height="{box_h}" rx="5" '
                 f'fill="{"#FBF4EF" if last else "#FFFFFF"}" stroke="{SIGNAL if last else BLUEPRINT}" stroke-width="1.5"/>')
        lines = label.split("\n")
        ly = y + box_h / 2 - (len(lines) - 1) * 7 + 4
        for ln in lines:
            p.append(f'<text x="{x + box_w / 2:.1f}" y="{ly:.1f}" text-anchor="middle" class="node-label">{esc(ln)}</text>')
            ly += 14
        if i < n - 1:
            p.append(f'<line x1="{x + box_w:.1f}" y1="{y + box_h / 2:.1f}" x2="{x + box_w + gap - 2:.1f}" '
                     f'y2="{y + box_h / 2:.1f}" stroke="{BLUEPRINT}" stroke-width="1.6" marker-end="url(#arrow)"/>')
    p.append("</svg>")
    return "\n".join(p)


def loop_svg(steps, width=680, height=330):
    """Circular loop diagram for iterative processes."""
    n = len(steps)
    cx, cy, r = width / 2, height / 2, min(width, height) / 2 - 78
    pts = [(cx + r * math.cos(-math.pi / 2 + 2 * math.pi * i / n),
            cy + r * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
    bw, bh = 128, 52
    p = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="diagram">', arrow_defs()]
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        a = math.atan2(y2 - y1, x2 - x1)
        sx, sy = x1 + bw * 0.62 * math.cos(a), y1 + bw * 0.62 * math.sin(a)
        ex, ey = x2 - bw * 0.62 * math.cos(a), y2 - bw * 0.62 * math.sin(a)
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        nx, ny = -(ey - sy), (ex - sx)
        nm = math.hypot(nx, ny) or 1
        p.append(f'<path d="M{sx:.1f},{sy:.1f} Q{mx + nx / nm * 26:.1f},{my + ny / nm * 26:.1f} {ex:.1f},{ey:.1f}" '
                 f'fill="none" stroke="{BLUEPRINT}" stroke-width="1.6" marker-end="url(#arrow)"/>')
    for (x, y), label in zip(pts, steps):
        p.append(f'<rect x="{x - bw / 2:.1f}" y="{y - bh / 2:.1f}" width="{bw}" height="{bh}" rx="5" fill="#FFFFFF" '
                 f'stroke="{BLUEPRINT}" stroke-width="1.5"/>')
        lines = label.split("\n")
        ly = y - (len(lines) - 1) * 7 + 4
        for ln in lines:
            p.append(f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" class="node-label">{esc(ln)}</text>')
            ly += 14
    p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{SIGNAL}"/></svg>')
    return "\n".join(p)


# ---------- CSS ----------
CSS = f"""

/* Fonts are installed system-wide by make_course.py (fonts/*.ttf -> ~/.fonts). Using @font-face instead embeds
   full font files on every page and balloons the PDF from ~0.4 MB to ~17 MB. */
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:{PAPER}; }}
body {{ font-family:'IBM Plex Serif', serif; color:{INK}; font-size:10.6pt; line-height:1.55; }}

/* NOTE: wkhtmltopdf's WebKit mis-scales fixed mm/px widths (~77%); width:100% renders correctly. */
.page {{ width:100%; min-height:297mm; position:relative; padding:16mm 18mm 18mm 18mm;
  page-break-after:always; background:{PAPER}; }}
.page:last-child {{ page-break-after:auto; }}

.foot {{ position:absolute; left:18mm; right:18mm; bottom:9mm; display:flex; justify-content:space-between;
  align-items:baseline; font-family:'IBM Plex Mono'; font-size:7.4pt; letter-spacing:0.06em; color:{INK_SOFT};
  border-top:0.6pt solid {LINE}; padding-top:3mm; text-transform:uppercase; }}

/* cover: inset title plate (full-bleed backgrounds hit the same WebKit scaling bug) */
.cover-plate {{ background:{NAVY}; color:{PAPER}; padding:20mm 16mm; border-radius:3px; margin-top:34mm; }}
.plate-corner {{ position:relative; }}
.plate-corner::before, .plate-corner::after {{ content:''; position:absolute; width:7mm; height:7mm; border:1.6pt solid {SIGNAL}; }}
.plate-corner::before {{ top:-1.6pt; left:-1.6pt; border-right:none; border-bottom:none; }}
.plate-corner::after {{ bottom:-1.6pt; right:-1.6pt; border-left:none; border-top:none; }}
.cover-eyebrow {{ font-family:'IBM Plex Mono'; font-size:9.5pt; letter-spacing:0.22em; text-transform:uppercase; color:{SIGNAL}; margin-bottom:9mm; }}
.cover-title {{ font-family:'Space Grotesk'; font-weight:700; font-size:33pt; line-height:1.12; color:{PAPER}; margin-bottom:6mm; }}
.cover-sub {{ font-style:italic; font-size:12pt; color:#B9C4D6; margin-bottom:13mm; }}
.cover-rail-label {{ font-family:'IBM Plex Mono'; font-size:7.6pt; letter-spacing:0.12em; text-transform:uppercase; color:#7C90AC; margin-bottom:3mm; }}
.cover-footer {{ margin-top:16mm; display:table; width:100%; font-family:'IBM Plex Mono'; font-size:8pt; color:#7C90AC;
  letter-spacing:0.05em; border-top:0.6pt solid #33415C; padding-top:5mm; }}
.cover-footer .l, .cover-footer .r {{ display:table-cell; }}
.cover-footer .r {{ text-align:right; }}
.cover-footer .big {{ color:{PAPER}; font-family:'Space Grotesk'; font-size:11pt; }}
.cover-below {{ margin-top:12mm; font-family:'IBM Plex Mono'; font-size:8pt; color:{INK_SOFT}; letter-spacing:0.04em; }}
.sheet-kicker {{ font-family:'IBM Plex Mono'; font-size:8.5pt; letter-spacing:0.18em; text-transform:uppercase; color:{BLUEPRINT}; }}

/* TOC */
.toc-title {{ font-family:'Space Grotesk'; font-weight:700; font-size:22pt; margin:0 0 3mm 0; }}
.toc-kicker {{ font-family:'IBM Plex Mono'; font-size:8.5pt; letter-spacing:0.18em; text-transform:uppercase; color:{BLUEPRINT}; margin-bottom:8mm; }}
table.toc {{ width:100%; border-collapse:collapse; margin-top:4mm; }}
table.toc td {{ padding:4.4mm 0; border-bottom:0.6pt solid {LINE}; vertical-align:top; }}
td.toc-num {{ font-family:'IBM Plex Mono'; font-size:9pt; color:{SIGNAL}; width:15mm; padding-right:3mm; }}
td.toc-name {{ font-family:'Space Grotesk'; font-weight:600; font-size:11.5pt; width:62mm; }}
td.toc-desc {{ font-style:italic; font-size:9.6pt; color:{INK_SOFT}; }}

/* module header */
.mod-tag {{ font-family:'IBM Plex Mono'; font-size:8.6pt; letter-spacing:0.14em; color:{SIGNAL}; text-transform:uppercase; margin-bottom:5mm; }}
h1.mod-title {{ font-family:'Space Grotesk'; font-weight:700; font-size:24pt; margin:2mm 0 3mm 0; line-height:1.1; }}
p.mod-abstract {{ font-style:italic; font-size:11.5pt; color:{INK_SOFT}; border-left:2.4pt solid {BLUEPRINT};
  padding-left:5mm; margin:0 0 8mm 0; max-width:150mm; }}
.rail {{ margin-bottom:6mm; }}

/* body */
h2.sec {{ font-family:'Space Grotesk'; font-weight:600; font-size:12.5pt; color:{BLUEPRINT_D}; text-transform:uppercase;
  letter-spacing:0.05em; margin:8mm 0 3mm 0; padding-bottom:1.5mm; border-bottom:0.8pt solid {LINE}; }}
h3.sub {{ font-family:'Space Grotesk'; font-weight:600; font-size:10.8pt; margin:5mm 0 2mm 0; }}
p {{ margin:0 0 3mm 0; }}
ul, ol {{ margin:2mm 0 3mm 0; padding-left:5mm; }}
li {{ margin-bottom:1.6mm; }}
strong {{ font-weight:700; }}
code.inline {{ font-family:'IBM Plex Mono'; font-size:9.2pt; background:{PAPER_DIM}; padding:0.4mm 1.4mm; border-radius:2px; color:{BLUEPRINT_D}; }}

.spec {{ position:relative; margin:6mm 0; padding:5mm 6mm; background:#FFFFFF; border:0.8pt solid {BLUEPRINT}; border-radius:2px; }}
.spec::before, .spec::after {{ content:''; position:absolute; width:5.5mm; height:5.5mm; border:2pt solid {SIGNAL}; }}
.spec::before {{ top:-1.6pt; left:-1.6pt; border-right:none; border-bottom:none; }}
.spec::after {{ bottom:-1.6pt; right:-1.6pt; border-left:none; border-top:none; }}
.spec-label {{ font-family:'IBM Plex Mono'; font-size:7.8pt; letter-spacing:0.14em; text-transform:uppercase; color:{SIGNAL}; margin-bottom:2.4mm; display:block; }}
.spec ul {{ margin:0; padding-left:4.4mm; }}
.spec p:last-child {{ margin-bottom:0; }}

.code {{ background:{NAVY}; color:#DCE6F2; font-family:'IBM Plex Mono'; font-size:8.6pt; padding:4.5mm 5.5mm;
  border-radius:3px; margin:4mm 0 6mm 0; line-height:1.6; white-space:pre-wrap; word-break:break-word; }}
.code .k {{ color:{SIGNAL}; }} .code .s {{ color:#8FBF9F; }} .code .c {{ color:#6B7C93; font-style:italic; }}

.diagram-wrap {{ margin:5mm 0 6mm 0; text-align:center; }}
.diagram-wrap .cap {{ font-family:'IBM Plex Mono'; font-size:7.6pt; letter-spacing:0.06em; text-transform:uppercase; color:{INK_SOFT}; margin-top:2mm; }}
.node-label {{ font-family:'IBM Plex Mono'; font-size:8.4px; fill:{INK}; }}
"""


# ---------- page builders ----------
def cover_page():
    repo = f"<br/>{esc(REPO_URL)}" if REPO_URL else ""
    return f"""
<div class="page">
  <div class="sheet-kicker">Sheet 00 &middot; Cover</div>
  <div class="cover-plate plate-corner">
    <div class="cover-eyebrow">Free Course &middot; 14 Modules + Labs</div>
    <div class="cover-title">AI Engineering,<br/>Assembled in Order</div>
    <div class="cover-sub">A build-log course from first principles to production &mdash;<br/>
    each module is a component wired to the one before it.</div>
    <div class="cover-rail-label">The build, module 01 &rarr; 14</div>
    {trace_rail(-1, width=460)}
    <div class="cover-footer">
      <div class="l">{EDITION}<br/>Prepared {PREPARED}{repo}</div>
      <div class="r big">AI&nbsp;ENGINEERING /14</div>
    </div>
  </div>
  <div class="cover-below">Read in order &mdash; the trace rail at the top of every page marks your position in the build.</div>
  <div class="foot"><span>AI Engineering Course</span><span>{EDITION}</span></div>
</div>"""


TOC_DESC = [
    "Why this discipline exists, and where it sits between ML research and software engineering",
    "How large language models actually work, at the depth an engineer needs",
    "Directing model behaviour reliably through instructions, structure, and examples",
    "Talking to a hosted LLM programmatically: requests, parameters, streaming, cost",
    "Turning meaning into coordinates &mdash; the substrate underneath search and RAG",
    "Storing and searching millions of embeddings fast",
    "Grounding generation in real, current, retrievable knowledge",
    "Letting the model reach for code and APIs instead of only text",
    "A standard wire protocol between models and the tools/data they use",
    "Loops, not single calls: planning, acting, observing, and deciding what's next",
    "Building controllable, stateful multi-step agent workflows as a graph",
    "Knowing whether any of this actually works, with numbers instead of vibes",
    "Latency, cost, safety, and failure handling once real users show up",
    "Keeping models and pipelines reliable, versioned, and observable over time",
]


def toc_page():
    rows = "".join(f'<tr><td class="toc-num">{i:02d}</td><td class="toc-name">{esc(n)}</td>'
                   f'<td class="toc-desc">{d}</td></tr>'
                   for i, (n, d) in enumerate(zip(MODULES, TOC_DESC), start=1))
    return f"""
<div class="page">
  <div class="toc-kicker">Contents / Build Order</div>
  <div class="toc-title">Fourteen Modules, One Pipeline</div>
  <p style="max-width:150mm;color:{INK_SOFT};margin-bottom:2mm;">Each module builds on the last, and each ends with a
  hands-on lab that extends one running project. The rail at the top of every page marks your position &mdash;
  read in order the first time through.</p>
  <table class="toc">{rows}</table>
  <div class="foot"><span>AI Engineering Course</span><span>Contents</span></div>
</div>"""


def module_header(idx, title, abstract):
    return (f'<div class="mod-tag">MOD&middot;{idx + 1:02d} / {TOTAL:02d}</div>{trace_rail(idx)}'
            f'<h1 class="mod-title">{esc(title)}</h1><p class="mod-abstract">{abstract}</p>')


def spec(label, content_html):
    return f'<div class="spec"><span class="spec-label">{label}</span>{content_html}</div>'


def diagram(svg, caption):
    return f'<div class="diagram-wrap">{svg}<div class="cap">{esc(caption)}</div></div>'


def code(html_body):
    return f'<div class="code">{html_body}</div>'


def module_page(idx, title, abstract, body_html, extra_html=""):
    foot = (f'<div class="foot"><span>AI Engineering Course</span>'
            f'<span>{esc(title)} &middot; {idx + 1:02d}/{TOTAL:02d}</span></div>')
    out = f'<div class="page">{module_header(idx, title, abstract)}{body_html}{foot}</div>'
    if extra_html:
        cont = (f'<div class="mod-tag">MOD&middot;{idx + 1:02d} / {TOTAL:02d} &mdash; LAB</div>{trace_rail(idx)}')
        out += f'<div class="page">{cont}{extra_html}{foot}</div>'
    return out


def closing_page():
    repo = f"<br/>{esc(REPO_URL)}" if REPO_URL else ""
    return f"""
<div class="page">
  <div class="sheet-kicker">Sheet 15 &middot; End of Build</div>
  <div class="cover-plate plate-corner">
    <div class="cover-eyebrow">End of Build</div>
    <div class="cover-title" style="font-size:28pt;">You've Wired Up<br/>the Full Stack</div>
    <div class="cover-sub">From tokens to production monitoring &mdash; the same<br/>pipeline, now assembled end to end.</div>
    <div class="cover-rail-label">The build, complete</div>
    {trace_rail(TOTAL - 1, width=460)}
    <div class="cover-footer">
      <div class="l">Next: pick one module and build<br/>the smallest working version of it.{repo}</div>
      <div class="r big">14 / 14</div>
    </div>
  </div>
  <div class="foot"><span>AI Engineering Course</span><span>End of Build</span></div>
</div>"""


def assemble(pages_html):
    return ('<html><head><meta charset="utf-8"><style>' + CSS + "</style></head><body>"
            + pages_html + "</body></html>")
