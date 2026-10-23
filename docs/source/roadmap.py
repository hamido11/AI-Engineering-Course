# -*- coding: utf-8 -*-
"""Renders assets/roadmap.png (1080x1350, LinkedIn 4:5) from the same module list as the PDF.
Run after make_course.py has installed the fonts:  python roadmap.py"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "assets" / "roadmap.png"

PHASES = [
    ("A", "FOUNDATIONS", "Talk to a model like an engineer", [
        ("01", "Introduction to AI Engineering", "What you're actually building", ""),
        ("02", "LLMs", "Tokens, context, temperature", ""),
        ("03", "Prompt Engineering", "Structure beats cleverness", ""),
        ("04", "OpenAI API", "Streaming, retries, cost", "")]),
    ("B", "KNOWLEDGE", "Make it know your data", [
        ("05", "Embeddings", "Meaning as coordinates", ""),
        ("06", "Vector Databases", "Search millions in milliseconds", ""),
        ("07", "RAG", "Answers grounded in your data", "FIRST REAL WIN")]),
    ("C", "ACTION", "Let it do things", [
        ("08", "Function Calling", "Model proposes, your code executes", ""),
        ("09", "MCP", "One protocol for tools", ""),
        ("10", "AI Agents", "Loops with stop conditions", ""),
        ("11", "LangGraph", "Resumable, testable workflows", "")]),
    ("D", "RELIABILITY", "Make it trustworthy", [
        ("12", "Evaluation", "Numbers instead of vibes", ""),
        ("13", "Production AI", "Guards, cache, fallback", ""),
        ("14", "MLOps", "Version, trace, monitor", "SHIPPABLE")]),
]

rows = []
for letter, name, tagline, mods in PHASES:
    rows.append(f'<div class="phase"><span class="pl">PHASE {letter} &middot; {name}</span>'
                f'<span class="pt">{tagline}</span></div>')
    for num, title, desc, badge in mods:
        b = f'<span class="badge">{badge}</span>' if badge else ""
        rows.append(f'<div class="row"><div class="n">{num}</div><div class="tx">'
                    f'<span class="t">{title}</span>{b}<div class="d">{desc}</div></div></div>')

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ width:1080px; height:1350px; background:#F6F4EE; font-family:'IBM Plex Serif',serif; color:#1B2430; position:relative; }}
.head {{ background:#10192B; padding:34px 56px 28px 56px; position:relative; }}
.eyebrow {{ font-family:'IBM Plex Mono'; font-size:16px; letter-spacing:5px; color:#B5502D; margin-bottom:14px; }}
.title {{ font-family:'Space Grotesk'; font-weight:700; font-size:46px; line-height:1.1; color:#F6F4EE; }}
.sub {{ font-style:italic; font-size:22px; color:#B9C4D6; margin-top:12px; }}
.c {{ position:absolute; width:26px; height:26px; border:4px solid #B5502D; }}
.c1 {{ top:14px; left:14px; border-right:none; border-bottom:none; }}
.c2 {{ bottom:14px; right:14px; border-left:none; border-top:none; }}
.list {{ position:relative; margin:16px 56px 0 56px; }}
.spine {{ position:absolute; left:27px; top:30px; bottom:20px; width:3px; background:#C9C2AE; }}
.phase {{ position:relative; margin:10px 0 6px 0; padding-left:84px; height:30px; }}
.pl {{ font-family:'IBM Plex Mono'; font-weight:600; font-size:15px; letter-spacing:3px; color:#B5502D; }}
.pt {{ font-style:italic; font-size:18px; color:#4B5563; margin-left:16px; }}
.row {{ position:relative; height:58px; }}
.n {{ position:absolute; left:0; top:2px; width:56px; height:50px; background:#fff; border:3px solid #2B5F8A; border-radius:6px;
  font-family:'IBM Plex Mono'; font-weight:600; font-size:22px; color:#B5502D; text-align:center; line-height:44px; }}
.tx {{ position:absolute; left:84px; top:0; right:0; }}
.t {{ font-family:'Space Grotesk'; font-weight:600; font-size:25px; }}
.d {{ font-size:17px; color:#4B5563; margin-top:1px; }}
.badge {{ font-family:'IBM Plex Mono'; font-weight:600; font-size:13px; letter-spacing:2px; color:#fff; background:#B5502D;
  padding:3px 9px; border-radius:3px; margin-left:14px; vertical-align:4px; }}
.foot {{ position:absolute; left:56px; right:56px; bottom:22px; border-top:2px solid #C9C2AE; padding-top:13px;
  font-family:'IBM Plex Mono'; font-size:15px; letter-spacing:2px; color:#4B5563; }}
.foot b {{ color:#B5502D; font-weight:600; }}
</style></head><body>
<div class="head"><div class="c c1"></div><div class="c c2"></div>
  <div class="eyebrow">START HERE &middot; FREE ON GITHUB</div>
  <div class="title">Where to start with AI<br/>as a software developer</div>
  <div class="sub">One path, 14 steps. Don't skip ahead &mdash; each one makes the next obvious.</div>
</div>
<div class="list"><div class="spine"></div>{''.join(rows)}</div>
<div class="foot"><b>14 MODULES</b> &middot; <b>14 LABS</b> &middot; PYTHON &middot; RUNS LOCALLY &middot; NO ML DEGREE NEEDED</div>
</body></html>"""

tmp = HERE / "roadmap.html"
tmp.write_text(html, encoding="utf-8")
OUT.parent.mkdir(exist_ok=True)
subprocess.run(["wkhtmltoimage", "--enable-local-file-access", "--width", "1080", "--height", "1350",
                "--quality", "90", str(tmp), str(OUT)], check=False, capture_output=True)
tmp.unlink()
try:                                    # flat colours: a 256-colour palette is visually identical and ~15x smaller
    from PIL import Image
    im = Image.open(OUT).convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(OUT, optimize=True)
except ImportError:
    print("(pillow not installed: skipping PNG optimisation)")
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
