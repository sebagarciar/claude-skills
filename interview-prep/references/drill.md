# Drill

A mock, run in chat. The user answers out loud or in writing, gets scored, and the session is
logged so they can read back what they actually said. The brief already contains model answers.
The drill is not for reading those. It is for finding out what comes out under pressure.

## Before starting

Confirm three things: which stage is being simulated, how many questions, and whether they want
feedback after each answer or only at the end. Default to five questions with feedback after
each one.

Then commit to the role. Open as that interviewer would open, in their register. A recruiter
opens warm and logistical. A hiring manager opens with the deep dive. An executive opens with
one hard question.

## Running it

1. **Ask one question. Nothing else.** No preamble, no hints, no restating the brief.
2. **Wait for their full answer.** Do not fill silence, do not offer the beats.
3. **Follow up at least once on most answers**, the way a real interviewer does. "What was your
   role in that specifically?" "What would you have done if it had not worked?" "How did you
   land on that number?" The follow-up is where prepared answers usually break, so it is the
   most valuable part of the drill.
4. **Then score it.**

## Scoring

Short and blunt. They do not need encouragement, they need the fix.

- **Landed.** What worked, in one line.
- **Missed.** The specific weakness: no number, buried the decision, forty seconds of setup,
  answered a different question, no tension in the story, trailed off without closing.
- **Length.** Actual against the sixty to ninety second target. Over-running is the most common
  failure and the easiest to fix.
- **Fix.** One concrete change, not three.
- **Score out of 5**, with the bar being what this company would accept for this level.

Do not rewrite their answer for them unless they ask. They should fix it and try again.

## Logging

Write `interview/drills/<YYYY-MM-DD>-<stage>.md` during the session:

```markdown
# Drill: <Stage> · <Company> · <YYYY-MM-DD>

## Q1. <question as asked>
**the user's answer (verbatim):**
> ...

**Follow-up:** <...>
**Their response:**
> ...

**Score 3/5.** Landed: ... Missed: ... Fix: ...
```

Verbatim means verbatim. Do not clean it up. The point is that they can see the filler, the
run-on, and the missing number in their own words.

Close the file with:

- **Patterns across the session.** The same weakness appearing three times matters more than
  any single answer.
- **Two things to fix before the real thing.** Two, not eight.
- **Any story that came out well and is not yet in `story-bank.md`.** Offer to add it.

## Repeat drills

On a second drill for the same role, read the previous log first. Re-ask the two or three
questions they scored lowest on, and say whether they improved. Progress across drills is the
thing worth measuring.
