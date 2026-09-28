---
name: interview-prep
description: Research a company and turn that research into a stage-by-stage interview brief for Seba, with predicted questions, answers anchored to his real evidence, questions to ask them, and a live drill that logs the answers he actually gave. Use whenever Seba has an interview, recruiter screen or final round coming up, asks what a company is likely to ask him, wants to research a company he is interviewing with, or wants to practise or run a mock.
---

# Interview Prep

Research a company deeply, work out how it actually interviews, and turn both into
preparation Seba can rehearse. The output is never generic advice. Every question is
tied to something this company does, and every answer is tied to something Seba did.

## What this produces

1. `research.md` — the company, the business, the team, the process. Dated and sourced.
2. `prep.md` — the brief. Stage by stage: who, what they are testing, the questions, the
   answer beats, the lines worth landing, the questions Seba asks them, and his weak spots
   for this specific role with prepared responses.
3. `<company>-prep.html` — **the default final deliverable.** One navigable page with everything
   from `research.md` and `prep.md`, plus diagrams. The markdown files stay the source of truth;
   the HTML is what Seba reads before the call.
4. `<product>-audit.md` — when the company has a public product worth inspecting.
5. `mock-trial-day/` — practice data files, when the process includes a trial day, take-home or case.
6. `drills/<date>-<stage>.md` — a live mock. Seba's own answers, verbatim, with feedback.
7. `debrief.md` — what actually got asked, written after the real interview.

## Inputs

- **The job ad.** Usually already at `job_search/applications/<company>-<role>/job-description.md`.
- **`job_search/master-cv.md`.** The bullet bank. Facts, metrics, dates.
- **`job_search/story-bank.md`.** Situations, feedback, failures, lessons. The narrative material.
- **`job_search/applications/<company>-<role>/notes.md`.** If `tailor-cv` ran, this says which
  bullets were selected and which keywords were targeted. The interviewer is reading that CV.
  Prepare for the CV that was actually sent.
- **`context/about-me.md`** and **`context/writing_style.md`.** How Seba works and how he sounds.

Read all of them before writing anything. Assumptions are the enemy.

## Truth rules — non-negotiable

1. **Never invent a company fact.** Not a revenue figure, a product launch, a leadership name,
   a strategy, or a piece of news. Seba may repeat it in the room. A confident invented number
   is the single worst failure mode of this skill.
2. **Label every claim.** `[sourced]` with a link, or `[inferred]` with the reasoning. Interview
   process detail is usually crowd-reported and inconsistent: say so rather than presenting one
   blog post as the definitive process.
3. **Never invent Seba's experience.** Answers are assembled only from `master-cv.md` and
   `story-bank.md`. If the evidence is not there, the gap gets raised with Seba, not filled in.
4. **Do not soften a gap.** If he has no experience with something the role requires, the brief
   says so and prepares an honest answer, not a disguise.
5. **Date the research.** Company facts go stale. Every research file carries the date it was run.

## Workflow

### Phase 0 — Locate the role

Find or create `job_search/applications/<company>-<role>/`. If there is no `job-description.md`,
ask Seba for the ad before going further: without it the research has no target. If the folder
already exists from `tailor-cv`, read `notes.md` and the `.pdf.txt` so the prep matches the CV
that was sent.

Ask which stage is coming up and when. That decides depth: a recruiter screen tomorrow needs a
tight brief on one stage, a final round next week justifies the full map.

### Phase 1 — Research

Follow `references/research.md`. Two tracks, run together: what the company is, and how the
company interviews. Write `interview/research.md`.

Three things that are easy to skip and pay off most (details in the reference):
pull the company's full job board and read the other open roles; work out the one number that
makes the business click and answer the practical mechanics (who adopts, who pays, onboarding
effort) up front; and, if there is a public product, inspect it and write an audit, checking
side effects before ever suggesting Seba try it.

### Phase 2 — Gap check, then interrogate Seba

This is the phase that stops the skill being capped by what Seba has already written down.

1. From the ad and the research, list the competencies this role will actually probe. Six to ten.
2. Score each one against `story-bank.md` and `master-cv.md`: strong evidence, thin, or none.
3. Show Seba the scorecard. For every thin or empty competency, ask him a specific question.
   Not "tell me about a time you led". Ask what the interviewer will ask, in this company's
   language, about this competency.
4. Write his answers into `job_search/story-bank.md` in the format in
   `references/story-bank-format.md`. This bank compounds across every application.

Follow `references/elicitation.md` for how to ask so the answers are usable.

### Phase 3 — Build the brief

Follow `references/stages.md` for the stage playbooks and `references/question-banks.md` for
what to predict at each one. Write `interview/prep.md`.

Answer format is **beats plus key lines**, never a script:

- **Beats** — the four or five moves of the answer, one line each, in order.
- **Evidence** — the exact metric or fact, quoted from the bank so it is right.
- **Key lines** — two or three sentences worth saying close to verbatim. Normally the opening
  sentence and the sentence carrying the number.
- **Trap** — what would make this answer land badly, when it is not obvious.

Answers must be *speakable*. Sixty to ninety seconds spoken, which is roughly 150 to 220 words.
Short sentences. Data over adjectives. Read `context/writing_style.md` and write the way he talks,
not the way a cover letter reads.

### Phase 4 — Show it before going further

Per the root `CLAUDE.md` ("Plan first"), show Seba the brief and let him react before running any drill. He will correct
framings and kill answers that are not his. Those corrections are worth more than the draft.

### Phase 4b — Build the HTML guide (default, every time)

Once the brief exists, build `interview/<company>-prep.html` following `references/html-guide.md`
and send it with `SendUserFile` (display `render`). Do not wait to be asked: Seba chose HTML as the
default on 2026-09-28. It is a local file, not a published artifact, unless he asks to share it.

Whenever the markdown changes later (a follow-up question, a new finding, a correction), update
the HTML in the same turn, in the section where the reader would look for it, and add it to the
navigation. Follow-up questions Seba asks during prep are a sign the first draft missed something:
answer in chat, then fold the answer into the guide.

If the process includes a trial day, take-home or case, the guide includes a mock day built per
`references/stages.md`.

### Phase 5 — Drill

Only when Seba asks, or when he agrees after seeing the brief. Follow `references/drill.md`.
The drill logs his answers verbatim to `interview/drills/<date>-<stage>.md` so he can review
what he actually said, not what the brief suggested he say.

### Phase 6 — Debrief

After the real interview, ask what actually got asked, what landed, what did not. Write
`interview/debrief.md` and push anything new back into `story-bank.md`. The next round at this
company, and the next interview anywhere, both get sharper from it.

Offer this proactively when a session opens with an interview that has already happened.

## Output layout

```
job_search/applications/<company>-<role>/
  job-description.md          (from tailor-cv)
  notes.md                    (from tailor-cv)
  interview/
    research.md
    prep.md
    <company>-prep.html        (default final deliverable)
    <product>-audit.md         (if the company has a public product)
    mock-trial-day/            (if there is a trial day, take-home or case)
    drills/2026-09-15-hiring-manager.md
    debrief.md

If the folder does not exist yet (no `tailor-cv` run), create it and save the pasted ad as
`job-description.md`.
```

## Language

Default to the language the interview will be held in. Ask if it is not obvious from the ad or
the recruiter's messages. If the process is mixed, note which stage is in which language and
prepare the key lines in both, since a memorised line in the wrong language is worse than none.

## Scope control

A full research pass plus a five-stage map is a lot of document. Match the output to what is
actually coming up. One stage in two days means one stage in the brief, and a note that the rest
is available. Do not hand Seba forty pages the night before a thirty-minute recruiter call.
