---
name: wrap-up
description: Review the current session for lessons worth keeping and propose them to Seba one by one, writing only the ones he approves into MEMORY.md, context/writing_style.md or a folder's CLAUDE.md. Use only when Seba types /wrap-up or explicitly asks to wrap up, close out, or capture what was learned in this session. Never run it on your own at the end of a task.
---

# Wrap Up

Look back over the session and ask one question: did anything happen that should change how
Claude works next time? Usually the honest answer is "nothing", and that is a good outcome.
The rule files stay useful only if they stay short and sharp. A rule nobody needed is noise
that buries the rules that matter.

**Nothing is written without Seba's yes on that specific item.**

## Step 1: Load what already exists

Read before proposing anything, so nothing gets proposed twice:

- `MEMORY.md` (root), including the "Where each new lesson goes" routing section
- `context/writing_style.md`, Part 2
- the `CLAUDE.md` of every folder touched in this session

## Step 2: Find candidates

Go through the session and list what could be a lesson. Good sources, in order of value:

1. **Corrections.** Seba said something was wrong, redid it, or pushed back.
2. **Decisions.** Seba chose between options, and the choice isn't visible in the code or files.
3. **Surprises.** Something about a tool, file or project behaved differently than expected
   and cost time.

Not sources: what got built, what the steps were, how long it took, anything already
visible in the code, the files or git history.

## Step 3: Filter hard

Each candidate must pass all four tests. If a candidate fails any one, drop it silently.

1. **Would it change behavior?** Next time a similar task comes up, would Claude act
   differently because this is written down? If Claude would have done the right thing
   anyway, drop it.
2. **Is it new?** If an existing rule already says it, even in other words, drop it. If an
   existing rule almost says it, the proposal is to **sharpen** that rule, not add a new one.
3. **Will it happen again?** If it only applies to this one task, file or day, drop it.
4. **Does it fit in two lines?** The rule itself, not the story behind it. If it can't be
   stated that tightly, it isn't understood well enough yet. Drop it and mention it in one
   line as "possible, not yet clear" instead.

Propose **at most 3** items. If more pass, keep the ones with the biggest effect on future
behavior. Zero is a valid and common result.

## Step 4: Route each survivor

Use the routing in `MEMORY.md` → "Where each new lesson goes":

- How something written in Seba's name sounds or is framed → `context/writing_style.md`, Part 2
- A fact or decision that only matters inside one folder → that folder's `CLAUDE.md`
- Everything else → `MEMORY.md`, under the matching section heading

## Step 5: Propose

Show the list in chat. Nothing is written yet. For each item:

```
1. [new | sharpen | merge] → <destination file> § <section>
   Rule: <one or two lines, exactly as it would be written>
   Why: <the moment in this session that triggered it, one line>
```

For **sharpen** and **merge**, quote the current rule text so Seba sees before and after.

If nothing passed, say so in one line: "Nothing from this session worth adding." Do not pad
it with a summary of the session.

Then ask Seba to answer yes or no per item (he can also edit the wording).

## Step 6: Write only the yeses

- Write each approved item exactly as approved, in the destination's existing style.
  `MEMORY.md` rules are a bold one-line rule, then a short explanation, then "General rule:"
  where relevant. Match what's already there.
- For a sharpen or merge, edit the existing rule in place. Don't append a second version.
- No dates, session logs, "learned today" notes or changelog lines.
- Don't touch anything Seba didn't approve, including typos or formatting you notice
  along the way. Mention them instead.

Finish by listing what was written and where, one line per item.
