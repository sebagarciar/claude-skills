---
name: weekly-vault-review
description: >
  Weekly maintenance pass over this Obsidian vault (obsidian-main). Finds notes that are new or
  changed since the last run, fixes their category/frontmatter/naming to match the vault's
  conventions, and adds backlinks for people/companies/cases that are genuinely recurring —
  not passing one-line examples. Use this when Seba says "run the weekly review", "organize my
  notes", "clean up the vault", or on a recurring weekly cadence. Ends with a git commit so every
  run is reversible and diffable.
---

# Weekly vault review

This replays, as a repeatable procedure, the cleanup done in the session that set this vault up:
fixing misfiled categories, unifying naming, and adding backlinks — but scoped to whatever is new
since last time, not the whole vault.

**Read `CLAUDE.md` in the vault root first.** It's the source of truth for categories, templates,
tags, folder rules, and naming conventions. This skill does not duplicate that schema — if
`CLAUDE.md` and this file ever disagree, `CLAUDE.md` wins, and update this file to match.

## 1. Find what's new since last run

This vault is a git repo. Each run tags its commit `vault-review-YYYY-MM-DD`. To find the diff:

```
git log --tags --oneline -1                          # find the last review tag
git diff --name-only <last-tag> HEAD -- '*.md'        # changed files since then
git status --porcelain -- '*.md'                      # + anything uncommitted right now
```

If no `vault-review-*` tag exists yet (first run), fall back to notes with a `created` date in
the frontmatter within the last 7 days, unioned with files whose mtime is within the last 7 days.

Skip anything under `Extras/Templates/`, `Extras/Categories/`, `Extras/Archive/`, `Term 3/`, and
`Daily/` — those are structural/dashboard files, not content to review.

## 2. Conform each new/changed note to its category schema

For each note in scope:

- Check it has a `categories` property pointing at a real category (see the table in `CLAUDE.md`).
- Check the frontmatter matches that category's template in `Extras/Templates/` — same property
  names, same list-vs-text shape. Don't invent new property names; reuse what's in
  `.obsidian/types.json`.
- If a note's actual content doesn't match its assigned category (e.g. job-search content tagged
  `Classes`, the way 9 Revolut notes were before this vault's cleanup), recategorize it to match
  the closest existing category and template — reuse an already-established pattern in the vault
  (e.g. `Fever.md` is the reference shape for `Jobs`) rather than inventing a new one.
- If a note is reference material about something outside Seba's own writing (a book, etc.),
  it belongs in `Extras/References/`, not root.
- If a file clearly isn't vault content at all (a dropped project artifact, code output, unrelated
  scratch file — like `DESIGN.md.md` was), flag it and ask rather than deleting it outright.

## 3. Check naming conventions

- Class session notes: `ABBR - S##.md`, zero-padded to 2 digits, `ABBR - S##&##.md` for combined
  sessions, `ABBR - Exam Summary.md` for exam prep. If a new note uses a different pattern (e.g.
  reverts to `S# - Full Name.md`), rename it to match.
- Dates: `YYYY-MM-DD` everywhere.
- Don't create new top-level folders. If content doesn't fit an existing folder/category, leave it
  in root and ask rather than inventing a new place for it.

## 4. Add backlinks — the part that needs judgment, not just pattern-matching

This is where most of the actual thinking happens. The goal is backlinks that will be useful later
via Obsidian's backlink pane, not maximum link density. Calibrate using what was learned setting
this up:

**Link, in any new/changed note:**
- Named people who recur or matter beyond this one mention: professors/guest speakers named
  explicitly (not "the professor" with no name), recruiters, executives, interviewers.
- Companies/cases where the note has substantial dedicated analysis — a case the session or note
  is actually *about* (a paragraph or more, explicit "main case" / "central case" framing, a named
  case-study header) — not a company mentioned once as a passing illustrative example ("e.g. like
  Netflix does X"). When in doubt, ask: would clicking backlinks on this company from another note
  actually surface something useful? If it's just "X was cited as an example," no — skip it.
- CV/job-application entities: employers, schools, named contacts — these are always worth linking
  since job-search notes get revisited often.
- A named concept/value/framework that's already fully written out as its own section somewhere
  in the vault (e.g. Revolut's 5 values live in `Revolut Culture.md`) — link to that exact location
  with a header link (`[[Note#Header|Display Text]]`) so it resolves to real content immediately,
  instead of creating a new unresolved link to a note that doesn't exist yet.

**Don't link:**
- Companies/tools/frameworks used as one-line comparisons or analogies scattered through class
  notes (this vault's Term 3 notes have hundreds of these — Google, Amazon, Netflix, etc. named in
  passing across nearly every session). Linking all of them was tried and rejected as noise in the
  session that set this up.
- Generic unnamed references ("the professor," "a client," "a student").

**If the scope of what qualifies turns out to be much bigger than expected** (this happened once
already — a "just link companies" pass turned into "there are 100+ substantive mentions across 40
files") — stop, summarize the real scope in a few sentences, and ask how far to go, rather than
grinding through all of it or arbitrarily picking a subset.

## 5. Report and commit

- Give a short summary of what changed: files recategorized, renamed, linked — grouped by type,
  not a raw diff dump.
- Ask before anything that touches more than ~15 files in one category of change, or before
  deleting/moving anything that isn't obviously disposable.
- Commit with a descriptive message, then tag it:
  ```
  git add -A
  git commit -m "Weekly vault review: <short summary>"
  git tag "vault-review-$(date +%Y-%m-%d)"
  ```
