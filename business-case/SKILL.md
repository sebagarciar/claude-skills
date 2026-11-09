---
name: business-case
description: Workflow and rules for building a business case end to end, from a case brief to one answer deck plus one numbers model, then the review and the rehearsal. Use when the user gets a case assignment (a job interview case, an MBA case, a consulting-style case), asks to build, fix or review a business case, an ROI case, a board recommendation or a case deck. Not for interview question prep, which is the interview-prep skill.
---

# Business case

Built from a real interview case that cost about 150 sessions, 130 commits and three deck
versions. Most of the time went to rework that the steps below avoid.

The one idea behind every rule: **the user presents and defends the case live. Anything they cannot
explain in their own words is a liability, not content.**

## The flow

Each step ends with the user's approval. Do not start the next step before it.

### 1. Unpack the brief

- Turn the brief into a checklist: every question it asks, in its own words, plus the units
  it wants (EUR, %, days). Put it at the top of the brief file. Every later review scores the
  deck against this list.
- Write down the reader of each part. They can differ inside one case (in the original case: Parts 1 to 3
  speak to the hiring manager, Part 4 is the VP HR speaking to her CFO).
- If there is a transcript of the reviewer or the client, pull their exact words: how they
  describe the problem, the role, what they value. The deck reuses those words.
- Check the deadline rules (send the deck 24 hours before, length of the session) and work
  back from them. The send date is the freeze date.

### 2. The user writes the answers

- For each part, the user writes the answer in one to three sentences, in their own words. Claude
  challenges it, gives options and explains, but does not write the answer for them.
- Decision questions go one at a time, with a recommendation. Never send a batch of 15
  questions that gets answered "Yes, yes, yes". Rubber-stamped answers become rules they do
  not own.
- Keep a short decision log (what was decided and why). Never a rulebook that controls the
  slides. In the original case, `decisions.md` grew into one, blocked every change and was deleted.

### 3. Titles-only deck

- One line per slide: the title, written as the message. The user approves the sequence part by
  part before any design.
- Each part makes sense on its own. A part never uses a number calculated in a later part.
  A generic question (like "describe the role") gets a generic answer, with no countries, no
  numbers from later parts and no first person.
- Read the titles alone, in order. If they do not tell the story, fix this list, not the
  slides.

### 4. The model

- One spreadsheet. An Input tab holds every assumption, each with its source or "assumed".
  Calculation tabs point at it. No parallel scripts or second models.
- Anchor assumptions to public numbers where possible (official statistics, the company's own
  public claims with a haircut, such as 80% of what it claims).
- Build only the numbers the brief asks for, in its units. Extra machinery (tranches,
  floors, five kinds of multiple) is noise the reader must decode.
- the user must be able to explain every number on a slide, step by step. If they can't, they learn
  it before it goes on, or it comes off.

### 5. Build the deck

- One deck file and the spreadsheet are the only sources of truth. Everything else is scratch
  and gets deleted when its job is done.
- Follow `references/deck-rules.md`.
- One session at a time on the deck file. Work in the main checkout, not a worktree, so the user
  sees every change in their local file without asking for a merge and a pull.
- When the question is how a slide should look, show two to four options as an artifact and
  let them pick. Do not iterate blind on one version.

### 6. Review once, then freeze

- Run `references/review-checklist.md` after the first full draft, not the night before.
- After the deck is sent, freeze it. Change only what the user stumbles on when rehearsing out
  loud. If the live deck differs from the one sent, tell them what changed so they can mention it.

### 7. Rehearse and prepare the Q&A

- Go part by part. For each, list the challenges the reviewer is likely to raise, using the
  brief and the transcript, with a short answer for each.
- Any slide they ask "what does this mean?" about gets rewritten or cut before the session,
  not explained in the room.

## What makes the content strong

- **Answer the question asked, in its units.** If the brief asks for EUR and %, show one EUR
  figure and one %. The case's Part 4 had 5.2x, 418%, 1.7x, 3.9x and 2.6x at once.
- **Lead with what is proven, not with the biggest number.** Its headline rested two
  thirds on its weakest assumption. A CFO finds that in two minutes.
- **One confidence scale for the whole deck:** measured, assumed, projected. Never two or
  three labelling systems.
- **Every number traceable on screen.** Show the chain (264 = 1,200 x 40% x 55%). Mark each
  link of an operational-to-euro chain as measured or assumed.
- **Test every claim with "can this ever be false?"** "The savings cover the fee" is always
  true when the fee is a share of the savings. A claim that cannot fail proves nothing.
- **One timeline of events, built on day 1.** Every day number, week and month in the deck
  comes from it. The case mixed day 28 and 30, day 35 and "3 weeks", and quoted a result on day 8
  that could only exist later.
- **Write each part in its reader's voice.** A sponsor is not sold to. A board deck has no
  vendor jargon and frames risks as things the sponsor controls ("on track, with one open
  item", not "at risk").
- **Plain words over labels and codes.** Green and amber, "bankable", "floor", "gates": if
  the user had to ask what it meant, the reviewer will too.
- **Use the reviewer's own words.** There, the hiring manager's three missions of the role
  became the three boxes of the core slide.
- **Say the hard number first.** Concede it, then reframe it. Never hide it in a footer.

When the user corrects how this skill works, the lesson goes into this file or its references.
