---
name: apply
description: One-step job application for the user. They paste a job ad URL (or text) and asks to apply; this skill runs the go/no-go check, builds the tailored CV through tailor-cv, drafts the form answers from the answer bank, logs the application in the tracker, and optionally fills the web form in Chrome, stopping before Submit. Use when the user says "apply to", "do this one", "apply to 1 and 3" after a find-jobs scan, or pastes a job link with the intent to apply. Not for interview prep (interview-prep) or for building only a CV (tailor-cv).
---

# Apply

Job ad in, application ready to send out. The user presses the last button.

## Files this skill uses

- `job_search/master-cv.md`: the only source of facts. Header holds the fixed contact data.
- `job_search/answer-bank.md`: standard answers, ASK items, and the rules for text answers.
- `job_search/tracker.md`: one row per application. Read it first, write to it last.
- `job_search/CLAUDE.md`: the folder rules. They all apply here.
- `.claude/skills/tailor-cv/SKILL.md` and `context/writing_style.md`.

Run scripts from the repo root (see the root `CLAUDE.md`).

## Hard rules

1. Never submit. The last click is the user's. Never click Submit, Send, Apply or Confirm.
2. Never create an account, enter a password, or solve a CAPTCHA. If the form needs one, stop
   and tell the user to do that step, then continue when they say so.
3. Never tick a consent or terms box without their yes in chat.
4. Never guess an ASK item from `answer-bank.md`. Ask once, then write the answer into the bank.
5. Never invent a fact. Every claim in an answer traces to `master-cv.md` or `story-bank.md`.
6. Never overwrite an existing application folder. `job_search/CLAUDE.md` rule applies.
7. The user's sensitive fields (ID number, date of birth, home address, gender) stay empty unless he
   gives the value in chat for that form.

## Flow

### 1. Intake

Get the ad (URL or pasted text). If it is a URL, read the page. Keep the apply link: it is where
step 7 goes. Then check `tracker.md` and `applications/` for the same company and role.

- Found: stop. Say what exists (date, status, files). Ask if they want a `-v2`. Do not go on.
- Not found: continue.

### 2. Go/no-go (two lines, before building anything)

Pull the must-haves from the ad. Check each one against `master-cv.md`.

- A must-have has no evidence: say so in two lines. It is their call. If they say no, log the row
  as `skipped` with the reason in the Notes column, write a short `notes.md`, and stop.
  Do not relitigate.
- Everything has evidence, or only nice-to-haves are missing: say "go" in one line and continue.

### 3. Build the CV

Run the `tailor-cv` skill in full, from its step 1. Keep its checkpoint where it shows the draft
and the ATS gaps before rendering. Do not skip it to save time. A CV that the user has not seen
does not go in a form.

Output goes to `applications/<company-slug>/` as the `tailor-cv` skill defines.

### 4. Draft the form answers

Find out what the form asks. Sources, in order:
1. The ad page and any apply page that loads without an account.
2. If the form is behind a login, ask the user to paste the questions or open the form in Chrome.

For each question:
- Standard facts (availability, permit, languages, contact): take them from `answer-bank.md`.
  If the field is an ASK item, ask the user now.
- Text questions: load `write-as-me`. Follow the question-type table in `answer-bank.md`. Respect
  the word or character limit exactly. Give the count.
- Answer in the form's language.

Write everything to `applications/<company-slug>/application-form-answers.md`. Under each answer,
list the facts used and where they come from. Mark it as a draft.

If the form has no text questions, skip the file.

### 5. Show the user, in one message

- Go/no-go result (one line).
- CV: path to the PDF, and the one or two lines that matter most.
- Form answers: the text answers, with counts.
- Open items: ASK fields, consent boxes, anything missing.

Wait for their edits or their yes. Apply their edits. Do not argue over style they decide.

### 6. Log it

Add one row at the top of the table in `tracker.md`: today's date, a link to the folder, the role,
status `built`, the ad link, follow-up empty. If a note is useful (skipped reason, source of the
lead), add it to the Role column in a few words.

When the user says they sent it, change the status to `submitted` and set the follow-up date to 7 days
later. Do that only on their word.

**Optional second tracker.** If the user also keeps a spreadsheet (Google Sheets), update it in
the same step as `tracker.md`, without being asked. Set the sheet id, tab and column map in
`job_search/CLAUDE.md`, and keep this step in sync with it.

- Read the last rows to find the end, then append one row. Never edit or delete other rows.
- A re-application gets a new row, with a note that the old row stays as it was.

### 7. Fill the form in Chrome (only if they ask for it, or says "fill it")

Use Claude in Chrome. The tools are deferred: load them first with one ToolSearch call:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__get_page_text`

Then:
1. Open the apply page in a new tab. If a login or account creation shows up, stop (rule 2).
2. Read the form. Match each field to a source: `answer-bank.md`, the drafted answers file, or
   the CV. A field with no source stays empty and goes in the open-items list.
3. Upload the CV PDF from `applications/<company-slug>/`.
4. Fill fields one by one with `form_input`. Never fill a field with a guess.
5. Stop before Submit. Take a screenshot. Report: what was filled, what was left empty and why,
   which boxes still need their tick.
6. Tell them: "Ready for you to review and press Submit."

If the page does not match what was read (the form changed, a field is missing), say so and
stop. Do not work around it.

## Several ads at once ("do 1 and 3")

Run steps 1 and 2 for each ad first and show all the go/no-go lines together. Then build the
approved ones one after another, each with its own checkpoint in step 3. Do not mix their
answers. Log each in the tracker as it finishes.

## What this skill does not do

- It does not search for jobs (`find-jobs`).
- It does not prepare interviews (`interview-prep`).
- It does not send email or LinkedIn messages. If a follow-up is due, it drafts text only.
- It reads private data (phone, email, answers). Keep `answer-bank.md` out of any public repo.
