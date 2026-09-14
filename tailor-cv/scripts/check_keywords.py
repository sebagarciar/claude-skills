#!/usr/bin/env python3
"""Report which ad keywords made it into the built PDF's text layer.

Turns "read the .pdf.txt and confirm the keywords survived" into an actual
check instead of a memory exercise.

Usage:
    python3 check_keywords.py keywords.txt output.pdf.txt
"""
import re
import sys


def found(keyword, text):
    # Whole-word match, not substring: "AI" must not count "training" as a
    # hit. Lookarounds instead of \b so a keyword ending in a symbol, e.g.
    # "C++", still matches; internal punctuation ("cross-functional") is fine.
    pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
    return re.search(pattern, text) is not None


def main():
    kw_path, txt_path = sys.argv[1], sys.argv[2]
    keywords = [k.strip() for k in open(kw_path) if k.strip()]
    text = open(txt_path).read().lower()

    present = [k for k in keywords if found(k, text)]
    missing = [k for k in keywords if not found(k, text)]

    print(f"present ({len(present)}/{len(keywords)}):")
    for k in present:
        print(f"  + {k}")
    print(f"missing ({len(missing)}):")
    for k in missing:
        print(f"  - {k}")


if __name__ == "__main__":
    main()
