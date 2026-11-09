"""Collect new jobs from every source, filter them, and write the run's candidates.json.

    python3 scan.py collect [--hours N]      collect + filter, prints a summary
    python3 scan.py details <run_dir> <id>…  fetch the full ad text for the shortlisted ids

Paths are fixed relative to this file, so it runs from any folder. Data lives in
job_search/daily-scan/: profile.md and watchlist.json are read, state/ remembers what was
already shown, runs/<date>/ holds each run.
"""

import json
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sources

JOB_SEARCH = Path(__file__).resolve().parents[4]
SCAN = JOB_SEARCH / "daily-scan"
STATE = SCAN / "state"
RUNS = SCAN / "runs"
APPLICATIONS = JOB_SEARCH / "applications"

MAX_HOURS = 24 * 7
MADRID = ["madrid", "alcobendas", "las rozas", "pozuelo", "majadahonda", "tres cantos", "getafe",
          "leganes", "alcala de henares", "boadilla", "san sebastian de los reyes", "mostoles",
          "fuenlabrada", "rivas", "torrejon", "coslada", "villaviciosa de odon", "alcorcon"]
SPAIN = ["spain", "espana", "spanien", "espagne"]
REMOTE = ["remote", "remoto", "teletrabajo", "work from home", "anywhere", "en remoto"]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()


def env():
    out, path = {}, JOB_SEARCH / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def profile_list(heading):
    """Bullet items under a '## heading' in profile.md."""
    body = (SCAN / "profile.md").read_text()
    m = re.search(rf"^## {heading}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return [l[2:].strip() for l in m.group(1).splitlines() if l.startswith("- ")] if m else []


# ---------------------------------------------------------------- filters

def where(j):
    """'Madrid', 'Spain remote' or None (out of scope)."""
    loc = norm(j["location"])
    if any(re.search(rf"\b{w}\b", loc) for w in MADRID):
        return "Madrid"
    in_spain = any(re.search(rf"\b{w}\b", loc) for w in SPAIN)
    if j["source"] == "linkedin" and j["remote"]:
        # LinkedIn's own remote filter, searched in Spain: the card shows a Spanish place or none.
        return "Spain remote" if in_spain or not loc else None
    if (j["remote"] or any(w in loc for w in REMOTE)) and in_spain:
        return "Spain remote"
    return None


def excluded(title, words):
    t = norm(title)
    return next((w for w in words if re.search(rf"\b{re.escape(norm(w))}\b", t)), None)


def dedupe_key(j):
    title = re.sub(r"\b(m f d|f m d|m f x|h m|m h|m w d|w m d|f m|m f)\b", " ", norm(j["title"]))
    company = re.sub(r"\b(sl|s l|sa|s a|slu|inc|ltd|gmbh|group|grupo|spain|espana|iberia)\b", " ", norm(j["company"]))
    return " ".join(company.split()) + " | " + " ".join(title.split())


def applied_index():
    """Folder name of every past application, for the 'applied here before' tag."""
    return sorted(p.name for p in APPLICATIONS.iterdir() if p.is_dir()) if APPLICATIONS.exists() else []


def applied_folders(company, folders):
    c = norm(company).replace(" ", "")
    if len(c) < 2:
        return []
    hits = []
    for f in folders:
        parts = f.split("-")
        if any("".join(parts[:k]) == c for k in range(1, min(4, len(parts)) + 1)):
            hits.append(f)
    return hits


# ---------------------------------------------------------------- state

def load(path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def window_hours(cli_hours):
    if cli_hours:
        return min(float(cli_hours), MAX_HOURS)
    last = load(STATE / "last_run.json", {}).get("collected_at")
    if not last:
        return 24
    gap = (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds() / 3600
    return min(max(24, gap + 1), MAX_HOURS)


# ---------------------------------------------------------------- collect

def collect(cli_hours=None):
    started = datetime.now(timezone.utc)
    hours = window_hours(cli_hours)
    since = started - timedelta(hours=hours)
    terms = profile_list("Search terms")
    exclusions = profile_list("Title exclusions")
    watchlist = load(SCAN / "watchlist.json", {"companies": []})["companies"]
    keys = env()
    log_lines = []
    log = lambda m: (log_lines.append(m), print("  " + m, file=sys.stderr))

    report = {}  # source -> {"found": n, "error": str|None, "seconds": s}
    raw = []

    def run(name, fn):
        t = time.time()
        try:
            got = fn()
            raw.extend(got)
            report[name] = {"found": len(got), "error": None}
        except KeyError as e:
            report[name] = {"found": 0, "error": str(e).strip("'")}
        except Exception as e:  # one broken source never stops the run
            report[name] = {"found": 0, "error": f"{type(e).__name__}: {e}"[:200]}
        report[name]["seconds"] = round(time.time() - t)
        print(f"{name}: {report[name]['found']} found"
              + (f" ({report[name]['error']})" if report[name]["error"] else ""), file=sys.stderr)

    print(f"Window: last {hours:.0f} hours. {len(terms)} search terms, "
          f"{len(watchlist)} companies on the watchlist.", file=sys.stderr)

    # Company boards are many small calls to different hosts: run them in parallel.
    def board(c):
        try:
            return c, sources.BOARDS[c["board"]](c), None
        except Exception as e:
            return c, [], f"{type(e).__name__}: {e}"[:150]

    t = time.time()
    with ThreadPoolExecutor(max_workers=8) as pool:
        board_results = list(pool.map(board, watchlist))
    board_jobs = [j for _, js, _ in board_results for j in js]
    board_errors = {c["company"]: err for c, _, err in board_results if err}
    raw.extend(board_jobs)
    report["company boards"] = {"found": len(board_jobs), "seconds": round(time.time() - t),
                                "error": (f"{len(board_errors)} of {len(watchlist)} boards failed"
                                          if board_errors else None),
                                "board_errors": board_errors}
    print(f"company boards: {len(board_jobs)} found across {len(watchlist)} companies"
          + (f", {len(board_errors)} failed" if board_errors else ""), file=sys.stderr)

    run("adzuna", lambda: sources.adzuna(terms, hours, keys, log))
    run("jooble", lambda: sources.jooble(terms, hours, keys, log))
    run("infojobs", lambda: sources.infojobs(terms, hours, keys, log))
    run("linkedin", lambda: sources.linkedin(terms, hours, log))

    # ------------------------------------------------ filter
    seen = load(STATE / "seen.json", {})
    folders = applied_index()
    counts = {"collected": len(raw), "too old": 0, "outside Madrid / Spain remote": 0,
              "title excluded": 0, "duplicate": 0, "already shown before": 0}
    kept = {}
    for j in raw:
        posted = sources.parse_date(j["posted_at"])
        # LinkedIn and the aggregators filter by date on their side; their own labels are rounded.
        if posted and posted < since - timedelta(hours=1 if j["source"] != "workday" else 24):
            counts["too old"] += 1
            continue
        if posted is None and j["source"] not in ("linkedin", "adzuna", "jooble", "infojobs"):
            counts["too old"] += 1
            continue
        place = where(j)
        if not place:
            counts["outside Madrid / Spain remote"] += 1
            continue
        hit = excluded(j["title"], exclusions)
        if hit:
            counts["title excluded"] += 1
            continue
        key = dedupe_key(j)
        if key in seen:
            counts["already shown before"] += 1
            continue
        if key in kept:
            counts["duplicate"] += 1
            other = kept[key]
            other["also_on"].append({"source": j["source"], "url": j["url"]})
            # Prefer the company's own board: exact date and full text.
            if other["source"] in ("linkedin", "adzuna", "jooble", "infojobs") and j["source"] in sources.BOARDS:
                j["also_on"] = other["also_on"] + [{"source": other["source"], "url": other["url"]}]
                j["also_on"] = [a for a in j["also_on"] if a["url"] != j["url"]]
                j.update(key=key, where=place, applied_before=other["applied_before"])
                kept[key] = j
            continue
        j.update(key=key, where=place, also_on=[], applied_before=applied_folders(j["company"], folders))
        kept[key] = j

    candidates = sorted(kept.values(), key=lambda j: j["posted_at"] or "", reverse=True)
    for i, j in enumerate(candidates, 1):
        j["n"] = i

    run_dir = RUNS / started.astimezone().strftime("%Y-%m-%d")
    k = 2
    while (run_dir / "candidates.json").exists() and (run_dir / "report.done").exists():
        run_dir = RUNS / f"{started.astimezone():%Y-%m-%d}-{k}"
        k += 1
    run_dir.mkdir(parents=True, exist_ok=True)
    out = {"collected_at": started.isoformat(timespec="seconds"), "hours": round(hours),
           "sources": report, "counts": counts, "log": log_lines, "jobs": candidates}
    (run_dir / "candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))

    print(f"\nKept {len(candidates)} of {len(raw)}. " +
          ", ".join(f"{k}: {v}" for k, v in counts.items() if k != "collected"), file=sys.stderr)
    print(f"Run folder: {run_dir}", file=sys.stderr)
    print_table(candidates)
    return run_dir


def print_table(jobs):
    """Compact list for triage: n, where, source, company, title, applied tag."""
    for j in jobs:
        tag = f"  [applied before: {', '.join(j['applied_before'])}]" if j["applied_before"] else ""
        place = "MAD" if j["where"] == "Madrid" else "REM"
        print(f"{j['n']:>4} {place} {j['source'][:8]:<8} {j['company'][:28]:<28} {j['title'][:90]}{tag}")


# ---------------------------------------------------------------- details

def details(run_dir, numbers):
    """Fetch the full ad text for the shortlisted jobs that don't have it yet."""
    path = Path(run_dir) / "candidates.json"
    data = json.loads(path.read_text())
    wanted = {int(n) for n in numbers}
    done = 0
    for j in data["jobs"]:
        if j["n"] not in wanted:
            continue
        j["shortlisted"] = True
        if j["source"] == "linkedin" and len(j["description"]) < 200:
            try:
                d = sources.linkedin_details(j["id"].split(":", 1)[1])
                j["description"] = d.pop("description")
                j["extra"].update(d)
                done += 1
            except Exception as e:
                j["extra"]["details_error"] = f"{type(e).__name__}: {e}"[:150]
            time.sleep(1.2)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    short = [j for j in data["jobs"] if j.get("shortlisted")]
    missing = [j["n"] for j in short if len(j["description"]) < 200]
    print(f"Shortlisted {len(short)}. Fetched {done} full ads."
          + (f" Still short or missing text: {missing}" if missing else ""), file=sys.stderr)
    (Path(run_dir) / "shortlist.json").write_text(json.dumps(
        [{k: j[k] for k in ("n", "id", "company", "title", "where", "location", "source", "posted_at",
                            "url", "applied_before", "description")} | {
            "seniority": j["extra"].get("seniority level"), "applicants": j["extra"].get("applicants"),
            "snippet_only": j["extra"].get("snippet_only", False)} for j in short],
        ensure_ascii=False, indent=1))
    print(f"Wrote {Path(run_dir) / 'shortlist.json'}", file=sys.stderr)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["collect"]:
        hours = args[args.index("--hours") + 1] if "--hours" in args else None
        collect(hours)
    elif args[:1] == ["details"] and len(args) >= 3:
        details(args[1], args[2:])
    else:
        print(__doc__)
        sys.exit(1)
