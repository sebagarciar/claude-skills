#!/usr/bin/env python3
"""Report which ad keywords made it into the CV, and split the misses by cause.

Turns "read the draft and confirm the keywords survived" into an actual check
instead of a memory exercise. Runs against the draft (cv-content.json) before
the PDF exists, or against the built PDF's text layer afterwards.

With --bank, a missing keyword is sorted into one of two buckets, because the
two need opposite responses:

  * evidence in the bank  -> a selection decision. Reopen the selection or
                             justify the drop. Never a question for Seba.
  * no evidence anywhere  -> a question for Seba. He may have done it and the
                             bank may simply not know yet.

Usage:
    python3 check_keywords.py keywords.txt cv-content.json --bank job_search/master-cv.md
    python3 check_keywords.py keywords.txt output.pdf.txt
"""
import json
import re
import sys


def found(keyword, text):
    # Whole-word match, not substring: "AI" must not count "training" as a
    # hit. Lookarounds instead of \b so a keyword ending in a symbol, e.g.
    # "C++", still matches; internal punctuation ("cross-functional") is fine.
    pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
    return re.search(pattern, text) is not None


def normalize(text):
    # Collapse every run of whitespace to one space so a multi-word keyword
    # still matches when the PDF's text layer broke it across two lines.
    return re.sub(r"\s+", " ", text.lower())


def text_from_content(path):
    """Flatten cv-content.json into one searchable string.

    Walks the whole structure rather than naming fields, so a schema change
    cannot silently drop text from the check.
    """
    def walk(node):
        if isinstance(node, str):
            yield node
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)
        elif isinstance(node, dict):
            for value in node.values():
                yield from walk(value)

    return " ".join(walk(json.load(open(path))))


def load_target(path):
    if path.endswith(".json"):
        return text_from_content(path)
    return open(path).read()


def main():
    args = sys.argv[1:]
    bank_path = None
    if "--bank" in args:
        i = args.index("--bank")
        bank_path = args[i + 1]
        del args[i:i + 2]

    kw_path, target_path = args[0], args[1]
    keywords = [k.strip() for k in open(kw_path) if k.strip()]
    text = normalize(load_target(target_path))
    bank = normalize(open(bank_path).read()) if bank_path else None

    present = [k for k in keywords if found(k, text)]
    missing = [k for k in keywords if not found(k, text)]

    print(f"present ({len(present)}/{len(keywords)}):")
    for k in present:
        print(f"  + {k}")

    if bank is None:
        print(f"missing ({len(missing)}):")
        for k in missing:
            print(f"  - {k}")
        print("\n(no --bank given, so misses are not split by cause)")
        return

    in_bank = [k for k in missing if found(k, bank)]
    no_evidence = [k for k in missing if not found(k, bank)]

    print(f"\nmissing, evidence in the bank ({len(in_bank)}) "
          f"-- selection decision, not a question for Seba:")
    for k in in_bank:
        print(f"  ~ {k}")

    print(f"\nmissing, no evidence in the bank ({len(no_evidence)}) "
          f"-- ask Seba before building:")
    for k in no_evidence:
        print(f"  ? {k}")


if __name__ == "__main__":
    main()
