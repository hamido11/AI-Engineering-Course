# -*- coding: utf-8 -*-
"""Build the course PDF:   sh fetch_fonts.sh && python make_course.py
Optional: REPO_URL=https://github.com/hamido11/AI-Engineering-Course python make_course.py   (stamps the link on cover/closing)
Requires wkhtmltopdf (0.12.6) on PATH."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build import MODULES, cover_page, toc_page, module_page, closing_page, assemble  # noqa: E402
import content, labs  # noqa: E402

ABSTRACTS = [
    "Why this discipline exists, and the system you'll assemble module by module.",
    "How next-token prediction becomes conversation &mdash; and what that implies for engineering.",
    "The cheapest, fastest lever for controlling model behaviour.",
    "Requests, streaming, retries, and cost: talking to a hosted model like an engineer.",
    "Meaning as coordinates: the substrate under semantic search and RAG.",
    "Approximate nearest neighbours: searching millions of vectors in milliseconds.",
    "Grounding generation in your data &mdash; retrieval and prompt discipline combined.",
    "The model proposes structured calls; your code executes them.",
    "One open protocol between models and the tools and data they use.",
    "Loops, not single calls: bounded autonomy toward a goal.",
    "Agent workflows as explicit graphs: controllable, resumable, observable.",
    "Numbers instead of vibes: measuring whether any of it actually works.",
    "Latency, cost, reliability, and safety once real users arrive.",
    "Versioning, tracing, and monitoring that keep the system healthy over time.",
]

def install_fonts():
    """Install fonts system-wide so wkhtmltopdf subsets them (keeps the PDF ~0.4 MB instead of ~17 MB)."""
    fonts = HERE / "fonts"
    if not list(fonts.glob("*.ttf")):
        sys.exit("fonts missing: run  sh fetch_fonts.sh  first")
    dest = Path.home() / ".fonts"
    dest.mkdir(exist_ok=True)
    for f in fonts.glob("*.ttf"):
        (dest / f.name).write_bytes(f.read_bytes())
    subprocess.run(["fc-cache", "-f", str(dest)], check=False, capture_output=True)


install_fonts()
pages = cover_page() + toc_page()
for i, (title, body_fn, abstract, lab_fn) in enumerate(zip(MODULES, content.BODIES, ABSTRACTS, labs.LABS)):
    pages += module_page(i, title, abstract, body_fn(), lab_fn())
pages += closing_page()

html_path, pdf_path = HERE / "course.html", HERE.parent / "AI-Engineering-Course.pdf"
html_path.write_text(assemble(pages), encoding="utf-8")
subprocess.run(["wkhtmltopdf", "--enable-local-file-access", "-L", "0", "-R", "0", "-T", "0", "-B", "0",
                "-q", str(html_path), str(pdf_path)], check=False)   # wkhtmltopdf warns on stderr; check the file instead
if not pdf_path.exists() or pdf_path.stat().st_size < 10_000:
    sys.exit("PDF build failed")
print("wrote", pdf_path)
