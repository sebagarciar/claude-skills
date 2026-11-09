---
name: find-jobs
description: Daily job scan for the user. Collects jobs posted in the last 24 hours in Madrid or remote in Spain (LinkedIn, job APIs, company job boards), ranks them against their master CV and past applications, and builds a one-page HTML report. Use when the user types /find-jobs, asks for today's new jobs, what was posted today, or to run the job scan. Also use when they react to a suggestion from the scan ("not this one", "more like this"), to record it in feedback.md.
---

# Find jobs

A script collects and filters. Claude ranks. A second script builds the page. All paths below
are relative to the repo root. Run the scripts from there.

```
job_search/.claude/skills/find-jobs/scripts/
  scan.py         collect + filter (collect), full ad text for a shortlist (details)
  sources.py      one function per source
  render.py       the HTML page, then marks the run as seen
  find_board.py   finds a company's job board for the watchlist
job_search/daily-scan/
  profile.md      what they are looking for: search terms, title exclusions, scoring brief
  watchlist.json  companies whose job boards are read directly
  feedback.md     their reactions to past suggestions
```

## Truth rules

1. Evidence comes from `job_search/master-cv.md` only. Cite bullet IDs (U1, C2, S3, M1...).
   Never credit them with something the bank does not show.
2. A must-have with no evidence in the bank is a gap. Say it in the card. Do not hide the job
   and do not soften the gap. Whether to apply is the user's call (`job_search/CLAUDE.md`).
3. Never apply, message a recruiter or open an application form. The scan only reads.

## Steps

### 1. Start the collect, then read the brief while it runs

```bash
python3 job_search/.claude/skills/find-jobs/scripts/scan.py collect > <scratchpad>/collect.out 2> <scratchpad>/collect.err
```

Run it in the background: it takes 5 to 10 minutes, almost all of it LinkedIn's rate limit.
Tell the user it has started and roughly how long it takes. While it runs, read
`daily-scan/profile.md`, `daily-scan/feedback.md` and `job_search/master-cv.md`, and skim the
headings of 10 recent `applications/*/job-description.md` files to calibrate what they applie to.

### 2. Read the collect output

- Company boards and the job APIs finish in under a minute. LinkedIn prints one progress line per
  search term.
- The window is 24 hours, or longer when the last run was more than a day ago (max 7 days).
  `--hours N` overrides it.
- stderr: per-source counts and errors, then the filter funnel and the run folder.
- stdout: one numbered line per candidate: `n  MAD|REM  source  company  title  [applied before: ...]`.

If a source shows an error, say so in one line in the final message. Do not stop the run.

### 3. Shortlist from the titles

From the numbered list, keep every job that could plausibly score 60 or more against
`profile.md`. Be inclusive here: when unsure, keep it. Reading a description is cheap, missing
a good job is not. Drop clear misses: sales quota roles, pure engineering, junior roles, admin,
roles in unrelated fields.

```bash
python3 job_search/.claude/skills/find-jobs/scripts/scan.py details <run_dir> <n> <n> <n> ...
```

This fetches the full ad text for the shortlisted LinkedIn jobs (about 1.5 s each, so 2 to 3
minutes for 50) and writes `<run_dir>/shortlist.json`. Read it in batches: print the start and
the end of each ad, where the requirements usually are, and open the full text when the
requirements were cut.

### 4. Score each shortlisted job

Score from 0 to 100 with this rubric. Add the parts.

| Part | Points | What earns them |
|---|---|---|
| Role fit | 0 to 35 | One of the target role families in `profile.md`, and the day-to-day matches what they did |
| Evidence | 0 to 30 | The must-haves are backed by bullets in the bank. Cite the IDs |
| Level | 0 to 15 | 4 to 8 years asked, manager scope. Junior or VP-level loses points |
| AI angle | 0 to 10 | AI is at the core of the role or the company |
| Context | 0 to 10 | Tech, scale-up, AI startup, or a real transformation at a large company |

Caps, applied after adding:
- A hard must-have with no evidence in the bank: max 70.
- A required language other than English or Spanish: max 40.
- The ad text shows it is not Madrid and not remote from Spain: max 20, gap "Not in Madrid".
  Check every `Spain remote` job: LinkedIn's remote filter often tags Barcelona hybrid roles.
  Search the ad for "Barcelona", "office", "híbrido", "presencial" before trusting the tag.
- A lesson in `feedback.md` that matches: follow it.

Every fact in `why` comes from the bank, dates included. A single job's dates are not
their whole career; "6 years" is their total experience, never one employer's.

**Same role already applied.** When `applied_before` lists folders, compare the role with each
folder (its name and the first heading of its `job-description.md`). Same role at the same
company: set `same_role_applied` to the folder name. A different role at the same company is a
normal job: score it, the page shows the "applied here before" tag on its own.

### 5. Write `<run_dir>/scores.json`

```json
{
  "summary": "Two sentences on today: how many strong matches and the one to look at first.",
  "scores": [
    {
      "n": 12,
      "score": 84,
      "why": ["Owns a $2M+ budget and a vertical's KPIs, like the role asks (M1, U1)", "..."],
      "gaps": ["Asks for 3+ years in B2B SaaS: no evidence in the bank"],
      "seniority": "Mid-senior, 5+ years",
      "language": "English",
      "same_role_applied": null,
      "note": "Optional one line: team, salary, deadline, anything worth knowing"
    }
  ],
  "title_triage": {"7": "Sales quota role", "31": "Engineering"}
}
```

- `why`: 2 to 4 short lines, each tied to the ad and to bullet IDs.
- `gaps`: 0 to 3 lines. Must-haves first.
- `title_triage` is optional: a 2 to 4 word reason for jobs dropped in step 3, when the list is
  short enough to give one.
- Plain English, short sentences, no em dashes (`context/writing_style.md`).

### 6. Build the page

```bash
python3 job_search/.claude/skills/find-jobs/scripts/render.py <run_dir>
open job_search/daily-scan/reports/<run_name>.html
```

Before `open`, read the top cards back in the HTML once: a wrong fact in a card is easy to miss
in JSON and obvious on the page.

`render.py` marks every job in the run as seen, so tomorrow's run only shows new ones. Run it
once per collect. If something went wrong before this step, nothing is marked and the next
run shows the same jobs again.

### 7. Report in the chat

Short. Then stop.
- One line: how many jobs were collected, kept and read in full, and the window.
- The top matches (score 80+, or the top 3 if none): score, title, company, one-line why.
- Source errors, if any, in one line.

## When the user reacts to a suggestion

"Not this one, too sales-heavy", "more like the Huspy one", "never show me consulting firms":
add one line to `daily-scan/feedback.md` under the right heading, in their words plus the job it
came from. If it is a title that is never a fit, add it to **Title exclusions** in `profile.md`
instead. If it is a new kind of role they want, add a search term.

## Maintaining the watchlist

Company job boards give exact publish times and catch jobs before LinkedIn. To add a company:

```bash
cd job_search/.claude/skills/find-jobs/scripts
python3 find_board.py "Company"                              # guesses the usual slugs
python3 find_board.py "Company=https://company.com/careers"  # reads the careers page instead
python3 find_board.py "Company" --add                        # writes the hit to watchlist.json
```

Workday sites (large corporates) cannot be guessed. Add them by hand:
`{"company": "HP", "board": "workday", "url": "https://hp.wd5.myworkdayjobs.com/ExternalCareerSite"}`.
The adapter searches that site for "Madrid" by default (`"search"` changes it).

## Keys for the job APIs

The aggregators turn on when their keys are in `job_search/.env` (gitignored). Without them the
page lists them as "not configured" and the run goes on.

```
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
JOOBLE_KEY=...
INFOJOBS_CLIENT_ID=...
INFOJOBS_CLIENT_SECRET=...
```

The user signs up themselves: developer.adzuna.com, jooble.org/api/about, developer.infojobs.net.
