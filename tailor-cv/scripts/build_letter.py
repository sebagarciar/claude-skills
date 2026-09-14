#!/usr/bin/env python3
"""Render a cover letter from JSON to a one-page PDF.

Shares the CV's typography so the two documents read as a set:
US Letter 612x792pt, Arial, 10pt body, 14pt name, 28pt side margins.

Usage:
    python3 build_letter.py letter.json output.pdf [--max-compress 0.05]

Exit 0 = one page. Exit 1 = overflows at max compression.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
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
.header-gap {{ height: {gap_head:.3f}pt; }}
.meta {{ margin-bottom: {gap_para:.3f}pt; }}
.subject {{ font-weight: bold; margin-bottom: {gap_para:.3f}pt; }}
p {{ text-align: justify; margin-bottom: {gap_para:.3f}pt; }}
p.tight {{ text-align: left; margin-bottom: 0; }}
.sign {{ margin-top: {gap_para:.3f}pt; }}
"""

INLINE = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<b>\1</b>"),
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), r"<i>\1</i>"),
]

# Chrome's line-breaker treats "-" as a break opportunity, which splits
# compounds like "end-to-end" across a justified line. Wrap them so the
# hyphen stays a normal, searchable character but can't be a break point.
HYPHEN_RE = re.compile(r"[^\W_]+(?:-[^\W_]+)+")


def rich(text):
    out = html.escape(str(text))
    out = HYPHEN_RE.sub(
        lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', out
    )
    for pat, rep in INLINE:
        out = pat.sub(rep, out)
    return out


def render_html(c, scale, title="letter"):
    fs = 10.0 * scale
    css = CSS.format(
        fs=fs,
        fs_name=14.0 * scale,
        lh=1.25 * (1 - (1 - scale) * 0.6),
        gap_head=14.0 * scale,
        gap_para=9.0 * scale,
        **PAGE,
    )
    b = [f"<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title><style>{css}</style>"]
    b.append(f'<div class="name">{rich(c["name"])}</div>')
    for line in c["contact"]:
        b.append(f'<div class="contact">{line}</div>')
    b.append('<div class="header-gap"></div>')
    if c.get("meta"):
        b.append('<div class="meta">')
        for line in c["meta"]:
            b.append(f'<div>{rich(line)}</div>')
        b.append('</div>')
    if c.get("subject"):
        b.append(f'<div class="subject">{rich(c["subject"])}</div>')
    if c.get("greeting"):
        b.append(f'<p>{rich(c["greeting"])}</p>')
    for para in c["body"]:
        b.append(f'<p>{rich(para)}</p>')
    b.append('<div class="sign">')
    for line in c["signoff"]:
        b.append(f'<p class="tight">{rich(line)}</p>')
    b.append('</div>')
    return "\n".join(b)


def page_count(pdf_bytes):
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf_bytes))


def print_pdf(html_text, out_pdf):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "letter.html")
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
        print("WARNING: pypdf not installed - text-layer check skipped. "
              "Install with `pip3 install pypdf`.", file=sys.stderr)
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

    for scale in steps:
        pdf = print_pdf(render_html(c, scale, title), out_pdf)
        if page_count(pdf) == 1:
            comp = f"{(1-scale)*100:.0f}% compression" if scale < 1 else "no compression"
            print(f"OK  1 page, {comp}, {len(pdf)} bytes -> {out_pdf}")
            txt = extract_text(out_pdf)
            if txt:
                print(f"Text layer: {len(txt.split())} words extracted, machine-readable")
                with open(out_pdf + ".txt", "w") as f:
                    f.write(txt)
            return 0

    print(f"OVERFLOW  more than one page at max {max_comp*100:.0f}% compression. "
          f"Cut text.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
