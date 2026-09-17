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

Write these requirements to `<dir>/keywords.txt`, one per line, in the ad's own wording. This
file is checked twice: against the draft in step 4, and against the built PDF in step 8 — a
promise you can verify beats a promise you remember.

Only a requirement that can be **evidenced** belongs in that file: a tool, a skill, a method, a
domain, a credential, a scale or a seniority signal. The ad's culture-speak — "ruthlessly",
"founder mindset", "bar raiser", "operators" — is tone, not a requirement. It belongs in the voice
of the Professional Summary, never in a checklist. The test is step 5: if you would never ask Seba
"do you have this?", it does not go in `keywords.txt`. Letting tone in there inflates the miss
count with lines nobody can act on and buries the real gaps.

### 2. Score the bank

Score every bullet in `master-cv.md` against those requirements. Rank within each role.

If a **must-have** from the ad has no evidence anywhere in the bank, stop and say so in two lines
before building anything. That is a go/no-go on the application and it is Seba's call, not a
tailoring problem. See `MEMORY.md`. It is a different check from the ATS gaps in step 5 — the
distinction is spelled out there.

### 3. Select and rephrase

Pick the strongest bullets per role. Rewrite them to mirror the ad's vocabulary, inside the truth
rules. Rewrite the Professional Summary for the target role. Reorder the Technical Skills line so
the tools the ad names come first.

Name the target role once in the Professional Summary, only where it is honest — title match is
one of the heaviest ATS ranking signals and a recruiter's first read. This changes the voice of
the summary, so read it back before committing to it.

Typical capacity at zero compression is 13 bullets plus a 3-line summary. Aim to fill the page.
An under-filled page wastes the strongest asset Seba has, which is evidence.

### 4. Check ATS coverage on the draft

Run the coverage check before showing Seba anything, against the draft rather than the PDF. That
is the whole point: a gap has to surface while the CV is still editable and while he can still
answer it.

Write the draft to `<dir>/cv-content.json` first (schema below), then:

```bash
python3 .claude/skills/tailor-cv/scripts/check_keywords.py <dir>/keywords.txt <dir>/cv-content.json --bank job_search/master-cv.md
```

`--bank` splits the misses in two, because the two need opposite responses:

- **Evidence in the bank, missing from the draft.** A selection decision, and it is yours. Either
  reopen the selection or be ready to say why that bullet lost. Never hand this list to Seba as a
  question — the answer is already in the bank.
- **No evidence in the bank.** This is the list he sees in step 5. The bank may simply not know
  about it yet.

### 5. Show the draft and the ATS gaps before rendering

Per `CLAUDE.md`, show Seba the selected and rephrased bullets before producing the PDF. Say which
bullets were dropped and why.

Then, underneath the draft, show the no-evidence list from step 4 under a heading that says what
it is and what it is for:

```
ATS gaps — the ad asks for these and the bank has no evidence
  - Salesforce
  - partner enablement
  - B2B SaaS
Do you have any of these? Tell me what you actually did and I will add it.
```

Rules for this section:

- Only the no-evidence list goes here. A keyword the bank already covers is your problem to fix,
  not his to answer.
- Ask flat. No guessing on his behalf, no "you probably touched this at Uber" — that invents the
  evidence and reduces him to confirming it.
- Do not re-ask a gap he has already answered earlier in the same application.
- If a gap is not something a person can have *done* or *used*, it is not a question — it means
  step 1 let tone into `keywords.txt`. Fix the file and re-run step 4. Do not paper over it by
  quietly dropping the line from the list you show him.
- An empty list earns one line: "no ATS gaps, every requirement has evidence." That is a result,
  not silence.

**What he answers goes into `master-cv.md` first, never straight into the CV.** Truth rule 2 says
a keyword only enters the CV if a bullet in the bank provides the evidence, and an answer in chat
is not a bullet in the bank. Write the new bullet into the bank in the bank's own format, show it
to him, then re-score and pull it into the CV. Two payoffs: the truth rule holds, and the next ad
asking for the same thing already finds it.

If he says there is no evidence for a gap, that is closed. Record it in `notes.md` and do not
raise it again for this application.

#### ATS gaps are not the must-have pre-flight

Two different checks, at two different moments, with two different stakes.

- **Must-have pre-flight** (step 2): a hard requirement has no evidence anywhere in the bank. Go
  or no-go on the whole application, raised before any CV exists, so Seba can decide whether the
  effort is worth spending.
- **ATS gaps** (this step): the application is already worth making. These are keywords worth one
  question each, never a reason to reopen the decision to apply.

Do not merge them. Treating every ATS gap as doubt about the application turns a useful check into
nagging.

### 6. Build

`cv-content.json` already exists from step 4. Fold in whatever step 5 changed, then:

```bash
python3 .claude/skills/tailor-cv/scripts/build_cv.py <dir>/cv-content.json "<dir>/Sebastian Garcia Romero - <Company>.pdf" --max-compress=0
```

`--max-compress=0` first, so you find out honestly whether it fits.

### 7. The fit ladder

Apply in this order. Never skip a rung.

1. **Shorten wording.** Check the overflow the script reports first, see below. A bullet under
   roughly 110 characters occupies one line at 10pt across the 556pt text column. A bullet at 115
   to 140 characters is spilling a nearly empty second line: trim that one first, it is the
   cheapest full line on the page.
2. **Compress typography.** Re-run without `--max-compress=0` to allow up to 5%. This scales font
   size, leading and gaps together, so proportions hold.
3. **Cut the lowest-scoring bullet.** Only when 1 and 2 are exhausted.

#### Measuring overflow precisely

`overflow_points()` counts the real text lines on page 2 via `pypdf` and prices them at the
current line-height, so the reported overflow is a genuine measurement, not a guess — it needs
`pypdf` installed, and falls back to an unmeasured "~12pt (~1 line)" with a warning if it isn't.
It is still an approximation (uniform line-height, not exact point position), so for a close call
— deciding whether one more trim clears the page, or pricing a specific change before committing
to it — measure the real height in the browser instead. Render the content at auto height and
read it:

```python
import re, sys, json
sys.path.insert(0, '.claude/skills/tailor-cv/scripts')
import build_cv
c = json.load(open('<dir>/cv-content.json'))
h = re.sub(r'^.*?<style>', '<style>', build_cv.render_html(c, 1.0), count=1)
open('<dir>/measure.html', 'w').write(
    "<!doctype html><meta charset=utf-8><style>html,body{margin:0}"
    ".page{width:612pt;background:#fff;padding:11pt 28pt 14pt 28pt}</style>"
    "<div class=page id=pg>" + h + "</div>")
```

Open it with the browser preview tool and run:

```js
const PT = 96/72, pg = document.getElementById('pg');
const hPt = pg.getBoundingClientRect().height / PT;
JSON.stringify({heightPt: Math.round(hPt*10)/10, overflowPt: Math.round((hPt-792)*10)/10})
```

Anything at or under 792pt fits. Trim until `overflowPt` is negative, then build. Delete
`measure.html` afterwards, it is not part of the output layout. The same trick prices a change
before you commit to it: render the variant, measure it, then decide. That is how the n8n CV
settled whether the contact line could carry both the personal site and GitHub. It could not,
the line wrapped and cost 12pt.

### 8. Verify and report

The script asserts one page and extracts the text layer back out of the PDF with `pypdf`, which is
what an ATS does. It writes that text beside the PDF as `.pdf.txt`.

Run the coverage check a second time, now against the extracted text layer:

```bash
python3 .claude/skills/tailor-cv/scripts/check_keywords.py <dir>/keywords.txt "<dir>/Sebastian Garcia Romero - <Company>.pdf.txt" --bank job_search/master-cv.md
```

This is not a repeat of step 4. Step 4 checked what was selected; this checks what survived
rendering and the fit ladder. Rung 3 cuts a bullet, and a cut bullet takes its keywords with it,
so a keyword that was present in the draft can be missing from the PDF. Any keyword that moved
between the two runs is something you caused and must account for.

A miss is not automatically a bug — the bank may genuinely have no evidence for it, and Seba may
have confirmed as much in step 5 — but it must be a decision, not an oversight.

Write `notes.md` in the application folder: bullets selected, bullets dropped, rephrasings made,
which fit-ladder rungs fired, the present/missing keyword list from `check_keywords.py`, the ATS
gaps put to Seba in step 5, and what he answered — including the gaps he confirmed he has no
evidence for, so a later run does not ask again.

## Output layout

```
job_search/applications/<company>-<role>/
  job-description.md
  keywords.txt
  cv-content.json
  preview.html
  notes.md
  Sebastian Garcia Romero - <Company>.pdf
  Sebastian Garcia Romero - <Company>.pdf.txt
```

Filename is always `Sebastian Garcia Romero - <Company>.pdf`. Recruiters see the filename. If the
company name contains `&` or another character some upload forms mangle, use a filesystem-safe
variant in the filename (e.g. "Click and Boat") — the real name still appears inside the CV and
letter content, this only affects the filename on disk.

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

`org` is the company name only. An industry or size descriptor, e.g. "(Technology, $50bn)",
goes in `desc` (the 9pt line), never appended in parentheses to `org` — a simpler ATS parser can
store the whole ambiguous string as the employer name.

Contact-line link text never carries a trailing slash: `sebasgarcia.dev`, not `sebasgarcia.dev/`.

## Preview

To eyeball the page before or after building:

```python
import re, sys, json
sys.path.insert(0, '.claude/skills/tailor-cv/scripts')
import build_cv
c = json.load(open('<dir>/cv-content.json'))
h = re.sub(r'^.*?<style>', '<style>', build_cv.render_html(c, 1.0), count=1)
frame = ("<!doctype html><meta charset=utf-8><style>html,body{background:#8a8a8a;margin:0;"
         "height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden}"
         ".s{zoom:.56}.page{width:612pt;height:792pt;background:#fff;padding:11pt 28pt 14pt 28pt;"
         "box-shadow:0 0 14px #0007;overflow:hidden}</style><div class=s><div class=page>")
open('<dir>/preview.html', 'w').write(frame + h + "</div></div>")
```

Then open that file with the browser preview tool and screenshot it.

## Requirements

Google Chrome at `/Applications/Google Chrome.app`. `pypdf` is optional but strongly recommended:
without it, both the ATS text-layer check and the overflow measurement degrade to an unmeasured
guess, printed as a warning rather than failing silently. No pandoc, LaTeX or poppler needed.
