---
name: tailor-cv
description: Tailor Seba's CV to a specific job ad and produce a one-page, ATS-optimized PDF ready to attach to an application. Use whenever Seba pastes a job description, shares a job posting URL, or asks for a CV, resume, or CV version for a role or company.
---

# Tailor CV

Turn a job ad into a one-page PDF that matches the format of Seba's original CV and is
optimized for Applicant Tracking Systems.

## Inputs

- **The job ad.** Pasted text, a file, or a URL.
- **`job_search/master-cv.md`.** The bullet bank. The only source of facts. Read it every time.
- **`context/writing_style.md`.** Short sentences, data over adjectives, no weasel words.

## Truth rules — non-negotiable

1. Never invent a metric, employer, title, date or tool. Selection, ordering and rephrasing only.
2. A keyword only enters the CV if a bullet in the bank already provides the evidence.
3. Rephrasing may mirror the ad's vocabulary. It may not change what happened.
4. Shortening a bullet must never drop its metric.
5. Header, education, dates and languages are fixed. They are never tailored.

## Workflow

### 1. Read the ad and extract requirements

Pull out, in the ad's own words: hard skills, tools, domain terms, seniority signals, and the
pillars the role is organized around. Note the ad's language.

### 2. Score the bank

Score every bullet in `master-cv.md` against those requirements. Rank within each role.

### 3. Select and rephrase

Pick the strongest bullets per role. Rewrite them to mirror the ad's vocabulary, inside the truth
rules. Rewrite the Professional Summary for the target role. Reorder the Technical Skills line so
the tools the ad names come first.

Typical capacity at zero compression is 13 bullets plus a 3-line summary. Aim to fill the page.
An under-filled page wastes the strongest asset Seba has, which is evidence.

### 4. Show the draft before rendering

Per `CLAUDE.md`, show Seba the selected and rephrased bullets before producing the PDF. Say which
bullets were dropped and why.

### 5. Build

Write `cv-content.json` (schema below), then:

```bash
python3 .claude/skills/tailor-cv/scripts/build_cv.py <dir>/cv-content.json "<dir>/Sebastian Garcia Romero - <Company>.pdf" --max-compress=0
```

`--max-compress=0` first, so you find out honestly whether it fits.

### 6. The fit ladder

Apply in this order. Never skip a rung.

1. **Shorten wording.** The script reports overflow in points and lines. A bullet under roughly
   110 characters occupies one line at 10pt across the 556pt text column. A bullet at 115 to 140
   characters is spilling a nearly empty second line: trim that one first, it is the cheapest full
   line on the page.
2. **Compress typography.** Re-run without `--max-compress=0` to allow up to 5%. This scales font
   size, leading and gaps together, so proportions hold.
3. **Cut the lowest-scoring bullet.** Only when 1 and 2 are exhausted.

### 7. Verify and report

The script asserts one page and extracts the text layer back out of the PDF with `pypdf`, which is
what an ATS does. It writes that text beside the PDF as `.pdf.txt`. Read it and confirm the
keywords survived.

Write `notes.md` in the application folder: bullets selected, bullets dropped, rephrasings made,
which fit-ladder rungs fired, and keyword coverage against the ad.

## Output layout

```
job_search/applications/<company>-<role>/
  job-description.md
  cv-content.json
  preview.html
  notes.md
  Sebastian Garcia Romero - <Company>.pdf
  Sebastian Garcia Romero - <Company>.pdf.txt
```

Filename is always `Sebastian Garcia Romero - <Company>.pdf`. Recruiters see the filename.

## Language

Default to the language of the job ad. Tell Seba which one you chose and offer the other version.
For a Spanish ad at an international company the call is genuinely close, so state the tradeoff
rather than deciding silently.

## Format is locked

The template replicates the original Google Docs export, verified against it: US Letter
612x792pt, Arial regular / bold / italic / bold-italic, 14pt name, 10pt body, 9pt company
descriptors, 28pt side margins, full-width rules under section headings only, dates
right-aligned. No rule under the header block: the original had one, Seba had it removed.
Do not change typography to solve a fit problem. That is what the compression rung is for.

## ATS constraints already handled by the template

Single column, no tables, no text boxes, no headers or footers, no images or icons, real embedded
text, standard section headings, consistent date format. Do not add anything that breaks these.

## `cv-content.json` schema

```json
{
  "name": "SEBASTIAN GARCIA ROMERO",
  "contact": ["line 1 (raw HTML allowed, for mailto and linkedin links)", "EU Work Permit"],
  "sections": [
    {"heading": "Professional Summary", "type": "paragraph", "text": "..."},
    {"heading": "Education", "type": "entries", "entries": [
      {"org": "...", "loc": "...", "detail": "italic line", "dates": "right-aligned",
       "bullets": ["..."]}
    ]},
    {"heading": "Professional Experience", "type": "entries", "entries": [
      {"org": "...", "loc": "...", "desc": "9pt company descriptor",
       "role": "bold italic", "dates": "right-aligned", "bullets": ["..."]}
    ]}
  ]
}
```

Entry fields are all optional. Omit `org` for a second role at the same employer, as with the
Uber Courier & Marketplace Coordinator entry. `**bold**` and `*italic*` work inside any text.

## Preview

To eyeball the page before or after building:

```python
import sys, json
sys.path.insert(0, '.claude/skills/tailor-cv/scripts')
import build_cv
c = json.load(open('<dir>/cv-content.json'))
h = build_cv.render_html(c, 1.0).replace('<!doctype html><meta charset=utf-8>', '')
frame = ("<!doctype html><meta charset=utf-8><style>html,body{background:#8a8a8a;margin:0;"
         "height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden}"
         ".s{zoom:.56}.page{width:612pt;height:792pt;background:#fff;padding:11pt 28pt 14pt 28pt;"
         "box-shadow:0 0 14px #0007;overflow:hidden}</style><div class=s><div class=page>")
open('<dir>/preview.html', 'w').write(frame + h + "</div></div>")
```

Then open that file with the browser preview tool and screenshot it.

## Requirements

Google Chrome at `/Applications/Google Chrome.app`. `pypdf` for the text-layer check, optional.
No pandoc, LaTeX or poppler needed.
