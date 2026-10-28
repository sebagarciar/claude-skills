# Prune: refresh the existing rules

Run this only when Seba types `/wrap-up prune` or asks to prune, refresh or clean up the
rules. It does not look for new lessons. It checks the rules already written down.

Why it matters: rule files help only while they stay short and written by a human. Every rule
that Claude would follow anyway, or that went stale, costs attention on every task and buries
the rules that matter.

**Nothing is changed without Seba's yes on that specific item.**

## Step 1: Pick the scope

One run covers `MEMORY.md` plus one more rule file. Ask Seba which one (built-in question
tool), recommending the largest folder `CLAUDE.md`. Options: a folder `CLAUDE.md`, the root
`CLAUDE.md`, or a file in `context/` (not `writing_style.md`, which has its own
structure; prune it only if Seba asks for it by name).

Read the routing section in `MEMORY.md` ("Where each new lesson goes") too, so any move follows it.

## Step 2: Give every rule a verdict

A rule is one bullet, one numbered item or one short paragraph that tells Claude what to do.
For each, run these tests in order and stop at the first that fails:

1. **Still true?** Check it against the files, folders, skills and git history. A rule that
   points to a file, tool or habit that no longer exists gets **update** or **delete**.
2. **Would Claude do it anyway?** If Claude would act the same with no rule, because the code,
   the files or plain common sense already show it, the verdict is **delete**.
3. **Said elsewhere?** If another rule says the same thing, even in other words, the verdict
   is **merge**: one rule stays, in the place the routing picks.
4. **In the right file?** If only one folder or one kind of task needs it, the verdict is
   **update**, moving it there.
5. **Fits in two lines?** The rule itself, not the story behind it. If not, the verdict is
   **update** with a shorter version. Keep the "case" pointer if the story lives in a folder file.

A rule that passes all five is **keep**.

## Step 3: Propose

Show the keeps first, as one short list (rule name only). Ask once: "Keep all of these?"
Seba can pull any of them out for a closer look.

Then the changes, **one at a time** with the built-in question tool, recommendation first:

```
[update | merge | delete] <file> § <section>
Now: <current text, quoted>
After: <new text, or "removed", or "merged into <file> § <section>">
Why: <the test it failed, one line>
```

Options: apply it (recommended), keep as is, or Seba's own wording. "Keep as is" is a fine
answer and needs no defense.

At most 8 changes per run. If more fail, propose the 8 with the biggest effect and list the
rest in one line for the next run.

## Step 4: Write only the yeses

- Edit each approved rule in place. For a merge, write the single combined rule and remove
  the other copy. For a move, add it at the destination and remove it from the source.
- If a removed rule was referenced elsewhere (a skill, another `CLAUDE.md`), fix the reference.
- No dates, session logs, "pruned on" notes or changelog lines, and no em dashes.
- Don't touch anything Seba didn't approve. Mention typos or loose ends instead.

Finish by listing what changed, one line per item.
