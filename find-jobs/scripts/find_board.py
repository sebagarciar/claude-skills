"""Find which public job board a company uses, for the watchlist.

    python3 find_board.py "Company" ["Company=https://company.com/careers" ...] [--add]

Tries the usual slugs on Ashby, Greenhouse, Lever, Workable, SmartRecruiters, Personio,
Teamtailor and Recruitee. With "=url", reads the board links on that careers page instead. Prints each hit with its open jobs and how many are in Madrid or
remote in Spain. With --add, writes the best hit per company into daily-scan/watchlist.json.
Workday sites can't be guessed: add them by hand with their public URL.
"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import scan
import sources

sources.RETRIES = 1


LINKS = [  # job board links as they appear on a careers page
    ("ashby", r"jobs\.ashbyhq\.com/([\w.-]+)"),
    ("greenhouse", r"(?:boards|job-boards)(?:\.eu)?\.greenhouse\.io/(?:embed/job_board\?for=)?([\w.-]+)"),
    ("lever", r"jobs\.(?:eu\.)?lever\.co/([\w.-]+)"),
    ("workable", r"apply\.workable\.com/([\w.-]+)"),
    ("smartrecruiters", r"(?:jobs|careers)\.smartrecruiters\.com/([\w.-]+)"),
    ("personio", r"([\w-]+)\.jobs\.personio\.(?:de|com)"),
    ("teamtailor", r"([\w-]+)\.teamtailor\.com"),
    ("recruitee", r"([\w-]+)\.recruitee\.com"),
]


def slugs(company):
    # Never the first word alone: "Open Cosmos" as "open" finds some other company's board.
    n = scan.norm(company)
    base = n.replace(" ", "")
    out = [base, n.replace(" ", "-")]
    out += [base + s for s in ("ai", ".ai", "-ai", "hq", "-hq", "app", ".io", ".com")]
    return [s for s in dict.fromkeys(out) if len(s) > 1]


def from_page(url):
    """Board links found on a careers page, as (board, slug) pairs."""
    try:
        page = sources.fetch(url, retries=2)
    except Exception as e:
        print(f"  could not open {url}: {e}")
        return []
    found = []
    for board, pattern in LINKS:
        for slug in re.findall(pattern, page):
            if slug.lower() not in ("embed", "api", "www", "jobs", "careers"):
                found.append((board, slug))
    if "myworkdayjobs.com" in page:
        m = re.search(r"https://[\w.-]+\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?[\w-]+", page)
        if m:
            print(f"  Workday site: {m.group(0)} (add it by hand with board 'workday' and this url)")
    return list(dict.fromkeys(found))


def try_board(company, board, slug):
    c = {"company": company, "board": board, "slug": slug}
    try:
        jobs = sources.BOARDS[board](c)
    except Exception:
        return None
    if not jobs:
        return None
    local = sum(1 for j in jobs if scan.where(j))
    # A sample job, to spot a board that belongs to another company with the same name.
    sample = f"{jobs[0]['title'][:50]}, {jobs[0]['location'][:30]}"
    return {**c, "open_jobs": len(jobs), "madrid_or_spain_remote": local, "sample": sample}


BOARD_TYPES = ("ashby", "greenhouse", "lever", "workable", "smartrecruiters", "personio",
               "teamtailor", "recruitee")


def find(company, url=None):
    def probe(pairs):
        with ThreadPoolExecutor(max_workers=12) as pool:
            return [h for h in pool.map(lambda p: try_board(company, *p), pairs) if h]

    if url:
        hits = probe(from_page(url))
    else:
        # Plain slugs first; the variants (company-ai, companyhq...) only when nothing matched.
        names = slugs(company)
        hits = probe([(b, s) for s in names[:2] for b in BOARD_TYPES])
        if not hits:
            hits = probe([(b, s) for s in names[2:] for b in BOARD_TYPES])
    # Same company found under two slugs: keep the one with more jobs.
    return sorted(hits, key=lambda h: (h["madrid_or_spain_remote"], h["open_jobs"]), reverse=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--add"]
    if not args:
        print(__doc__)
        sys.exit(1)
    path = scan.SCAN / "watchlist.json"
    wl = scan.load(path, {"companies": []})
    known = {(c["company"].lower()) for c in wl["companies"]}
    for arg in args:
        # "Company=https://company.com/careers" reads the careers page instead of guessing slugs.
        company, _, url = arg.partition("=")
        hits = find(company, url or None)
        if not hits:
            print(f"{company}: no public board found", flush=True)
            continue
        best = hits[0]
        print(f"{company}: {best['board']}/{best['slug']}  {best['open_jobs']} open, "
              f"{best['madrid_or_spain_remote']} in Madrid or Spain remote. e.g. {best['sample']}"
              + (f"  (also: {', '.join(h['board'] + '/' + h['slug'] for h in hits[1:3])})" if len(hits) > 1 else ""), flush=True)
        if "--add" in sys.argv and company.lower() not in known:
            wl["companies"].append({"company": company, "board": best["board"], "slug": best["slug"]})
            known.add(company.lower())
    if "--add" in sys.argv:
        wl["companies"].sort(key=lambda c: c["company"].lower())
        path.write_text(json.dumps(wl, ensure_ascii=False, indent=1) + "\n")
        print(f"Watchlist now has {len(wl['companies'])} companies.")
