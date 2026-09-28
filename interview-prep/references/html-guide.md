# The HTML guide

The default final deliverable. One self-contained page Seba opens before the call and during
practice. If a previous guide exists in another application folder, reuse its structure and
CSS as the starting point instead of designing from zero, but give each company its own accent
colour and its own diagrams.

## Structure

Order follows how Seba uses it: the ten-minute version first, then the company, then him, then
proof and practice. Every section has a one-line "why this matters" under the heading.

1. **Start here.** The 60-second version and a checklist for before the call (tick boxes,
   remembered in the browser).
2. **The company.** How the business works (with a diagram), the worked number (with a chart),
   the practical mechanics (who adopts, who pays, onboarding effort), how they make money,
   funding and team, who the interviewer is (timeline of their career plus what it predicts).
3. **The role and him.** What the job really is, who am I (beats plus key lines), why this
   company (flagged as a draft if motivation is not confirmed), why him (evidence table with
   Strong / Medium / Gap tags), questions he may ask, weak spots, questions for them.
4. **Proof and practice.** Product audit, trial-day explainer, mock day, what is still needed
   from Seba.

## Rules

- **Navigation:** sticky sidebar on desktop, a jump menu on phone. Every section and every
  added subsection gets a link. Highlight the current section on scroll.
- **Sourced and Inferred tags** on every company fact, same as the markdown. A legend in the
  header. Facts not to repeat outside the room get a red callout.
- **Answers to likely questions are collapsible** (`<details>`): the question visible, beats
  and key lines inside. Key lines styled as quotes he can say.
- **Answer keys to practice tasks are collapsible** so he can't see them by accident.
- **Diagrams earn their place.** Draw one when a mechanism has moving parts: who talks to whom,
  a flow of money, a flywheel, a before/after. Inline SVG, coloured from the theme tokens, with
  a `<title>` and a caption saying what is sourced and what is inferred. Charts drawn to scale.
- **Plain English**, per the root `CLAUDE.md`: explain any term (ERP, AP/AR, e-invoicing) the
  first time. Short sentences, bullets, no emojis, no em dashes.
- **Light and dark theme**, readable at phone width, no external assets except Google Fonts.
- **Practice data** is shown in the page with a copy button and also saved as a file next to it.

## Delivery

Save next to `prep.md`, check once in the browser pane, then send it with `SendUserFile`
(display `render`). Do not publish it as an Artifact unless Seba asks: it contains his weak
spots and private prep.
