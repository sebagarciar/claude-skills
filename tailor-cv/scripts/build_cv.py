#!/usr/bin/env python3
"""Render a tailored CV from JSON to a one-page, ATS-readable PDF.

Replicates the format of Seba's original Google Docs CV:
US Letter 612x792pt, Arial family, 14pt name / 10pt body / 9pt secondary,
28pt side margins, full-width rules under section headings.

Usage:
    python3 build_cv.py content.json output.pdf [--max-compress 0.05]

Exit code 0 = one page. Exit code 1 = still overflows at max compression;
stderr reports the overflow in points and approximate lines so the caller
knows how much text to cut.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Measured from the original PDF: 612x792pt, content x from 28.05 to 584.0,
# first baseline block at y=10.8, last content ending near y=777.
PAGE = dict(top=11, side=28, bottom=14)

CSS = """
@page {{ size: letter; margin: {top}pt {side}pt {bottom}pt {side}pt; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
  font-family: Arial, Helvetica, sans-serif;
  font-size: {fs:.3f}pt;
  line-height: {lh:.3f};
  color: #000;
  -webkit-font-smoothing: antialiased;
}}
.name {{ font-size: {fs_name:.3f}pt; font-weight: bold; letter-spacing: .1pt; }}
.contact {{ font-size: {fs:.3f}pt; }}
.contact a {{ color: #1155cc; text-decoration: underline; }}
.rule {{ border-bottom: .75pt solid #000; margin-bottom: {gap_rule:.3f}pt; }}
.header-gap {{ height: {gap_rule:.3f}pt; }}
h2 {{
  font-size: {fs:.3f}pt; font-weight: bold;
  margin-top: {gap_sec:.3f}pt;
}}
.entry {{ margin-top: {gap_entry:.3f}pt; }}
.entry.first {{ margin-top: {gap_rule:.3f}pt; }}
.row {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12pt; }}
.row > .r {{ white-space: nowrap; }}
.org {{ font-weight: bold; text-transform: uppercase; }}
.loc {{ font-weight: bold; text-transform: uppercase; }}
.desc {{ font-size: {fs_small:.3f}pt; }}
.role {{ font-weight: bold; font-style: italic; }}
.dates {{ font-size: {fs:.3f}pt; }}
.edu-detail {{ font-style: italic; }}
p.summary {{ text-align: justify; }}
ul {{ list-style: none; margin: 0 0 0 {bullet_indent:.3f}pt; }}
/* The bullet is a real text node inside a fixed-width inline-block, NOT inline
   "•\xa0" text and NOT an absolutely-positioned ::before.

   Inline "•\xa0" was the first version: Chrome justifies by stretching
   whitespace, so that leading space grew by a different amount on every line
   and the gap after "•" visibly varied bullet to bullet.

   An absolute ::before fixed the gap but broke the PDF text layer, which is
   what an ATS reads: the marker is extracted in paint order, not flow order,
   so every bullet glyph detached and reappeared at the end of the PREVIOUS
   bullet, leaving the real bullets with no leading marker to segment on.

   A fixed-width inline-block gets both. Justification cannot stretch it
   because it is not whitespace, and there is deliberately no whitespace
   between the span and the text; the marker stays in flow, so it extracts in
   the right order. Keep the span and the text adjacent in the markup. */
li {{
  margin-top: {gap_bullet:.3f}pt; padding-left: {bullet_hang:.3f}pt;
  text-indent: -{bullet_hang:.3f}pt;
  text-align: justify;
}}
li .bul {{ display: inline-block; width: {bullet_hang:.3f}pt; text-indent: 0; }}
"""

INLINE = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<b>\1</b>"),
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), r"<i>\1</i>"),
]

# Chrome's line-breaker treats "-" as a break opportunity, which splits
# compounds like "cross-functional" across a justified line. Wrap them so
# the hyphen stays a normal, searchable character but can't be a break point.
HYPHEN_RE = re.compile(r"[^\W_]+(?:-[^\W_]+)+")


def rich(text):
    out = html.escape(str(text))
    out = HYPHEN_RE.sub(
        lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', out
    )
    for pat, rep in INLINE:
        out = pat.sub(rep, out)
    return out


def row(left, right, lclass="", rclass=""):
    r = f'<span class="r {rclass}">{rich(right)}</span>' if right else ""
    return f'<div class="row"><span class="{lclass}">{rich(left)}</span>{r}</div>'


def render_html(c, scale, title="cv"):
    fs = 10.0 * scale
    bullet_hang = 9.0 * scale
    css = CSS.format(
        fs=fs,
        fs_name=14.0 * scale,
        fs_small=9.0 * scale,
        lh=1.15 * (1 - (1 - scale) * 0.6),
        gap_rule=2.0 * scale,
        gap_sec=7.0 * scale,
        gap_entry=5.0 * scale,
        gap_bullet=1.2 * scale,
        bullet_indent=13.0 * scale,
        bullet_hang=bullet_hang,
        **PAGE,
    )
    b = [f"<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title><style>{css}</style>"]
    b.append(f'<div class="name">{rich(c["name"])}</div>')
    for line in c["contact"]:
        b.append(f'<div class="contact">{line}</div>')
    b.append('<div class="header-gap"></div>')

    for sec in c["sections"]:
        b.append(f'<h2>{rich(sec["heading"])}</h2><div class="rule"></div>')
        if sec["type"] == "paragraph":
            b.append(f'<p class="summary">{rich(sec["text"])}</p>')
        else:
            for i, e in enumerate(sec["entries"]):
                b.append(f'<div class="entry{" first" if i == 0 else ""}">')
                if e.get("org"):
                    b.append(row(e["org"], e.get("loc", ""), "org", "loc"))
                if e.get("desc"):
                    b.append(f'<div class="desc">{rich(e["desc"])}</div>')
                if e.get("role"):
                    b.append(row(e["role"], e.get("dates", ""), "role", "dates"))
                if e.get("detail"):
                    b.append(row(e["detail"], e.get("dates", ""), "edu-detail", "dates"))
                if e.get("bullets"):
                    b.append("<ul>")
                    for x in e["bullets"]:
                        b.append(f'<li><span class="bul">&#8226;</span>{rich(x)}</li>')
                    b.append("</ul>")
                b.append("</div>")
        if sec["type"] == "bullets":
            pass
    return "\n".join(b)


def page_count(pdf_bytes):
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf_bytes))


def overflow_points(out_pdf, scale):
    """How far content runs onto page 2, in points. Measured from the real
    text layer via pypdf: count non-empty lines on page 2 and price each at
    the current line-height. Falls back to an unmeasured guess (with a
    warning) if pypdf isn't installed."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("WARNING: pypdf not installed - overflow is an unmeasured "
              "guess. Install with `pip3 install pypdf` for a real number.",
              file=sys.stderr)
        return 12.0
    pages = PdfReader(out_pdf).pages
    if len(pages) < 2:
        return 0.0
    lines = [l for l in (pages[1].extract_text() or "").splitlines() if l.strip()]
    return len(lines) * 11.5 * scale


def print_pdf(html_text, out_pdf):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "cv.html")
        with open(src, "w") as f:
            f.write(html_text)
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
             "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}", src],
            capture_output=True, timeout=90,
        )
    if not os.path.exists(out_pdf):
        sys.exit("Chrome produced no PDF")
    return open(out_pdf, "rb").read()


def extract_text(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        print("WARNING: pypdf not installed - ATS text-layer check "
              "skipped. Install with `pip3 install pypdf`.", file=sys.stderr)
        return None
    return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    content_path, out_pdf = args[0], args[1]
    max_comp = 0.05
    for a in sys.argv[1:]:
        if a.startswith("--max-compress="):
            max_comp = float(a.split("=")[1])

    c = json.load(open(content_path))
    if not os.path.exists(CHROME):
        sys.exit(f"Chrome not found at {CHROME}")

    title = os.path.splitext(os.path.basename(out_pdf))[0]

    steps = [1.0]
    s = 1.0
    while s > 1 - max_comp + 1e-9:
        s = round(s - 0.01, 4)
        steps.append(max(s, 1 - max_comp))

    last = None
    for scale in steps:
        pdf = print_pdf(render_html(c, scale, title), out_pdf)
        pages = page_count(pdf)
        last = (scale, pages, pdf)
        if pages == 1:
            comp = f"{(1-scale)*100:.0f}% compression" if scale < 1 else "no compression"
            print(f"OK  1 page, {comp}, {len(pdf)} bytes -> {out_pdf}")
            txt = extract_text(out_pdf)
            if txt:
                words = len(txt.split())
                print(f"ATS text layer: {words} words extracted, machine-readable")
                side = open(out_pdf + ".txt", "w")
                side.write(txt)
                side.close()
            return 0

    scale, pages, pdf = last
    over = overflow_points(out_pdf, scale)
    lines = max(1, round(over / (11.5 * scale)))
    print(f"OVERFLOW  {pages} pages at max {max_comp*100:.0f}% compression. "
          f"Content exceeds one page by ~{over:.0f}pt (~{lines} line(s)). "
          f"Shorten or cut ~{lines} line(s) of text.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
