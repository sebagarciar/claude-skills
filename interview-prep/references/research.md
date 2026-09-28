# Research

Two tracks, run together. Track A is what the company is. Track B is how it interviews.
Both go into `interview/research.md`, dated, with every claim marked `[sourced]` or `[inferred]`.

## Track A — The company

Do not write a Wikipedia summary. Research towards the questions an interviewer will actually
ask, which means research towards the pressure the business is under right now.

### 1. How it makes money

The unit of value, who pays, and what the margin structure looks like. For a marketplace, both
sides and the take rate. For SaaS, the pricing model and who signs. For retail, the format mix.
Seba came from Uber and Simon Kucher: he can speak to pricing, take rates, incentives and unit
economics credibly, so this section pays for itself.

**Find the one number that makes the business click, and work it out.** A description of the
product is forgettable; a worked calculation is not. For example, a payments company that
sells early-payment discounts: 2% sounds small until you annualise it, and 2% for paying 20 days
early is about 37% a year, against 2 to 4% for cash in a bank. One line like that explains the
whole business better than any paragraph. Show the formula so Seba can redo it out loud, and mark it
`[inferred]` when the inputs are assumptions.

**Answer the practical mechanics before Seba has to ask.** On a two-sided product, his first
follow-ups were "do both companies need to hire the service?" and "how hard is it to onboard a
company?". Both should have been in the first draft. For every company, answer:

- **Who has to adopt it** for it to work. One side, both sides, a whole team, an IT department.
- **Who pays, and who gets it free.** Being on a platform is not the same as paying for it.
- **How hard it is to get a customer live.** Minutes, weeks or months, and who on the customer's
  side gets involved (IT, security, procurement). Job ads for integration engineers are evidence.
- **What a new customer gets on day one**, before any network effect or data exists.

If a mechanic cannot be found, say so and turn it into a question Seba asks in the room.

### 2. Where it is in its life

Growth stage, funding, profitability, headcount trend. A company burning cash asks different
questions from one defending share. Recent layoffs or a hiring freeze change the tone of the
whole process and should be flagged, not hidden.

### 3. What changed in the last twelve months

Results, launches, market exits, acquisitions, leadership changes, regulation, a public
strategy shift. This is the richest source of interview questions and of the questions Seba
asks back. Prioritise the last two quarters.

### 4. Competitors and the actual fight

Who they lose deals to and why. What their differentiator claims to be, and whether the
evidence supports it. Be willing to write the uncomfortable version.

### 5. The team he would join

The function, where it sits, who it reports to, what it owns. Look up the hiring manager and
likely interviewers on LinkedIn if named. Their background predicts their questions: an
ex-consultant asks structure, an ex-operator asks what you actually shipped.

### 6. Culture and values, read sceptically

Published values matter because interviewers are often scored against them (Amazon's are the
clearest example, but many companies run a lighter version). Find the rubric if one exists.
Separate the stated values from what employee reviews suggest is actually rewarded.

### 7. The role behind the ad

What problem is this hire solving? A new role means the function is being built. A backfill
means something broke or someone left. Read the ad for the pillars it is organised around and
map each one to a likely interview probe.

**Pull the company's own job board, not only the ad Seba pasted.** The version on the careers
page is often longer, and the extra lines (a trial day, the real scope, "all of this has
actually happened in this seat") are often the most useful ones. Most boards
have a public feed: Ashby (`https://api.ashbyhq.com/posting-api/job-board/<slug>`), Greenhouse
(`https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true`), Lever
(`https://api.lever.co/v0/postings/<slug>`).

**Read the other open roles as strategy signals.** They say what the company is building next,
often more candidly than the press. An ERP integration engineer ad tells you who the target
customers are; a first marketing hire's ad may admit the category has no demand yet. Signals like
these make the best questions Seba can ask.

If the interviewer currently holds the same role, ask whether this hire is a second seat or a
backfill. It changes what the job is.

### 8. The product itself

If the company has a public product, public code, an API, a free tier or a demo, inspect it.
This matters most when the role asks for hands-on, technical or AI skills, because "we'll ask you
to show us" is best answered with something about *their* product. Reading a company's public
repos and finding a real bug plus a design gap tied to their core thesis can be the strongest
single piece of prep for a call.

- Read, do not run. Clone into the scratchpad, never install into Seba's setup unprompted.
- **Check side effects before suggesting Seba try it.** Some products send real emails, create
  legal documents or charge money the moment you use them. If trying the product sends messages,
  charges money, needs a tax ID or creates a legal document, say so and do not suggest it.
- Write the findings to `interview/<product>-audit.md`: what is good first, then findings with
  why each matters to the business, then how to use it in the room (one finding, framed as
  "I noticed", after the positives, and "this is what I'd pick up in week one").

## Track B — The interview process

### What to look for

- The number and order of stages, and who runs each.
- Whether there is a case, a take-home, a presentation, or a live exercise, and how long.
- Whether behavioural questions are scored against a published framework.
- Typical total elapsed time.
- Actual questions people report being asked.

### Sourcing

Search the company name with terms like interview process, interview questions, hiring process,
onsite, case study, and the exact role title. Useful sources include the company's own careers
and engineering or people blogs, Glassdoor and Indeed interview sections, Blind, Reddit threads
in role-specific subreddits, Medium write-ups, and recruiter posts on LinkedIn.

### Reliability, and how to state it

Crowd-reported process data is noisy, often years old, and varies by country and team. Grade it:

- **Confirmed** — the company documents it, or the recruiter told Seba directly.
- **Consistent reports** — several independent accounts agree.
- **Single report** — one account, flagged as such.
- **Inferred** — no data. Say what the pattern is at comparable companies and why, and mark it
  clearly. An honest `[inferred]` is useful. A dressed-up guess is a liability.

Company facts need two extra labels beyond `[sourced]` and `[inferred]`:

- **Stated by the company, unannounced.** A fact that appears only in the job ad or a recruiter
  message, such as a funding round with no public trace anywhere. Seba can mention it to that
  company, never to anyone else.
- **Database estimate.** Dealroom, PitchBook and similar often show a valuation without saying
  whether it is pre-money, post-money or their own estimate. Say exactly what the label says, and
  tell Seba not to quote it.

Flag both in the brief under a "don't repeat outside the room" note.

If Seba has emails or messages from the recruiter, ask for them. A recruiter saying "next is a
45 minute call with the hiring manager and then a case" beats every blog post ever written.

## Write-up

`interview/research.md`, in this order:

1. **Date and role.** Research run on YYYY-MM-DD for `<role>` at `<company>`.
2. **The 60-second version.** What this company is and what it is fighting right now, in five
   lines. If Seba reads nothing else, he reads this.
3. **Business model and unit economics**, including the worked number.
4. **How it works in practice**: who adopts, who pays, onboarding effort, day-one value.
5. **Current situation and last twelve months.**
6. **Competitive position.**
7. **The team and the role**, including the full job-board ad and what the other open roles signal.
8. **Culture and evaluation criteria.**
9. **The product**, if inspected: one paragraph and a pointer to the audit file.
10. **The process**, stage by stage, with a reliability grade on each.
11. **Open questions** — what could not be found, and which of these the recruiter can answer.
12. **Sources** — links, with what each one supported.

Every factual line carries `[sourced]` or `[inferred]`. No exceptions.
