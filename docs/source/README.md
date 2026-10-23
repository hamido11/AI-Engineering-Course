# Rebuilding the PDF

The PDF is generated from `content.py` (modules), `labs.py` (lab pages) and `build.py` (design system).

```bash
sh fetch_fonts.sh        # one-time: downloads the open-licensed fonts
python make_course.py    # needs wkhtmltopdf 0.12.6 on PATH; writes ../AI-Engineering-Course.pdf
python roadmap.py        # regenerates ../../assets/roadmap.png

# optional: stamp your repo URL on the cover and closing page
REPO_URL=https://github.com/hamido11/AI-Engineering-Course python make_course.py
```

Known quirk: wkhtmltopdf's WebKit mis-scales fixed `mm`/`px` widths (~77%), so pages use `width:100%`.
`make_course.py` installs the fonts system-wide (not via `@font-face`), which keeps the PDF ~0.4 MB instead of ~17 MB.
