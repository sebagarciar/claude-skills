"""Build the day's HTML page from a run's candidates.json and Claude's scores.json.

    python3 render.py <run_dir>

Then marks every candidate as seen, so tomorrow's run only shows new jobs, and records the
time of this run, so a skipped day widens the next window.
"""

import html
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import scan

APPLY, LOOK = 80, 60


def esc(s):
    return html.escape(str(s or ""), quote=True)


def age(posted, ref):
    if not posted:
        return ""
    h = (ref - datetime.fromisoformat(posted)).total_seconds() / 3600
    if h < 1:
        return "less than 1 h ago"
    return f"{h:.0f} h ago" if h < 48 else f"{h / 24:.0f} days ago"


def card(j, s, ref):
    score = s.get("score")
    tone = "hi" if score is not None and score >= APPLY else "mid" if score is not None and score >= LOOK else "lo"
    meta = [f'<span class="where">{esc(j["where"])}</span>', esc(j["location"]),
            esc(age(j["posted_at"], ref))]
    if j["extra"].get("applicants"):
        meta.append(esc(j["extra"]["applicants"]))
    if s.get("seniority"):
        meta.append(esc(s["seniority"]))
    if s.get("language"):
        meta.append(esc(s["language"]))
    links = [f'<a href="{esc(j["url"])}" target="_blank" rel="noopener">{esc(j["source"])}</a>']
    links += [f'<a href="{esc(a["url"])}" target="_blank" rel="noopener">{esc(a["source"])}</a>'
              for a in j.get("also_on", [])]
    why = "".join(f"<li>{esc(w)}</li>" for w in s.get("why", []))
    gaps = "".join(f"<li>{esc(g)}</li>" for g in s.get("gaps", []))
    applied = (f'<p class="tag">Applied here before: {esc(", ".join(j["applied_before"]))}</p>'
               if j.get("applied_before") else "")
    cmd = f"/tailor-cv {j['url']}"
    return f"""
<article class="card">
  <div class="top">
    <div class="score {tone}" title="Fit score">{esc(score if score is not None else "?")}</div>
    <div class="head">
      <h3><a href="{esc(j["url"])}" target="_blank" rel="noopener">{esc(j["title"])}</a></h3>
      <p class="company">{esc(j["company"])}</p>
      <p class="meta">{" · ".join(m for m in meta if m)}</p>
    </div>
  </div>
  {applied}
  {f'<div class="cols"><div><h4>Why it fits</h4><ul>{why}</ul></div>' if why else '<div class="cols"><div></div>'}
  {f'<div><h4>Gaps</h4><ul class="gaps">{gaps}</ul></div></div>' if gaps else '</div>'}
  {f'<p class="note">{esc(s["note"])}</p>' if s.get("note") else ""}
  <div class="foot">
    <span class="links">Open on {" · ".join(links)}</span>
    <button class="copy" data-cmd="{esc(cmd)}">Copy /tailor-cv</button>
  </div>
</article>"""


def row(j, reason, ref):
    return (f'<li><a href="{esc(j["url"])}" target="_blank" rel="noopener">{esc(j["title"])}</a> '
            f'<span class="muted">{esc(j["company"])} · {esc(j["where"])} · {esc(age(j["posted_at"], ref))}'
            f'{" · " + esc(reason) if reason else ""}</span></li>')


def render(run_dir):
    run_dir = Path(run_dir)
    data = json.loads((run_dir / "candidates.json").read_text())
    scores_path = run_dir / "scores.json"
    scored = json.loads(scores_path.read_text()) if scores_path.exists() else {}
    by_n = {s["n"]: s for s in scored.get("scores", [])}
    triage = {int(k): v for k, v in scored.get("title_triage", {}).items()}
    ref = datetime.fromisoformat(data["collected_at"])
    jobs = data["jobs"]

    apply, look, low, applied, rest = [], [], [], [], []
    for j in jobs:
        s = by_n.get(j["n"])
        if s is None:
            rest.append(j)
        elif s.get("same_role_applied"):
            applied.append((j, s))
        elif s.get("score", 0) >= APPLY:
            apply.append((j, s))
        elif s.get("score", 0) >= LOOK:
            look.append((j, s))
        else:
            low.append((j, s))
    for group in (apply, look, low):
        group.sort(key=lambda p: -p[1].get("score", 0))

    def section(title, pairs, empty):
        body = "".join(card(j, s, ref) for j, s in pairs) or f'<p class="muted">{empty}</p>'
        return f'<section><h2>{title} <span class="count">{len(pairs)}</span></h2>{body}</section>'

    def folded(title, items):
        if not items:
            return ""
        return (f'<details><summary>{title} <span class="count">{len(items)}</span></summary>'
                f'<ul class="rows">{"".join(items)}</ul></details>')

    src_rows = []
    for name, r in data["sources"].items():
        status = "ok" if not r.get("error") else ("off" if r["error"] == "not configured" else "err")
        detail = r.get("error") or ""
        src_rows.append(f'<tr><td>{esc(name)}</td><td class="num">{r["found"]}</td>'
                        f'<td><span class="dot {status}"></span>{esc(detail)}</td></tr>')
    board_errors = data["sources"].get("company boards", {}).get("board_errors") or {}
    counts = data["counts"]
    funnel = " · ".join(f"{esc(k)}: {v}" for k, v in counts.items())
    date = ref.astimezone().strftime("%A %d %B %Y, %H:%M")
    summary = scored.get("summary", "")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job scan {ref.astimezone():%d %b}</title>
<style>
:root {{
  --bg: #f7f7f5; --surface: #ffffff; --text: #1d1d1b; --muted: #6b6b66; --line: #e4e4df;
  --accent: #1f5f8b; --hi: #1e7a46; --hi-bg: #e3f3e9; --mid: #8a6100; --mid-bg: #fbf1d9;
  --lo: #6b6b66; --lo-bg: #efefeb; --gap: #9a3b2e; --tag-bg: #eef3f8;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #161615; --surface: #1f1f1d; --text: #ecece8; --muted: #a2a29b; --line: #34342f;
    --accent: #7fb6dc; --hi: #7fd3a1; --hi-bg: #193826; --mid: #e8c06a; --mid-bg: #3a2f14;
    --lo: #a2a29b; --lo-bg: #2a2a27; --gap: #e79a8c; --tag-bg: #1d2a35;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text);
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
main {{ max-width: 920px; margin: 0 auto; padding: 24px 16px 64px; }}
header h1 {{ font-size: 22px; margin: 0 0 4px; }}
header p {{ margin: 0; color: var(--muted); }}
.summary {{ margin: 16px 0 8px; padding: 12px 14px; background: var(--surface);
  border: 1px solid var(--line); border-radius: 10px; }}
h2 {{ font-size: 17px; margin: 32px 0 12px; }}
.count {{ color: var(--muted); font-weight: 400; }}
.card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
  padding: 16px; margin-bottom: 12px; }}
.top {{ display: flex; gap: 14px; align-items: flex-start; }}
.score {{ flex: none; width: 48px; height: 48px; border-radius: 10px; display: grid;
  place-items: center; font-weight: 700; font-size: 18px; }}
.score.hi {{ background: var(--hi-bg); color: var(--hi); }}
.score.mid {{ background: var(--mid-bg); color: var(--mid); }}
.score.lo {{ background: var(--lo-bg); color: var(--lo); }}
.head {{ min-width: 0; }}
h3 {{ font-size: 16px; margin: 0; line-height: 1.3; }}
h3 a {{ color: var(--text); text-decoration: none; }}
h3 a:hover {{ color: var(--accent); }}
.company {{ margin: 2px 0 0; font-weight: 600; }}
.meta {{ margin: 2px 0 0; color: var(--muted); font-size: 13px; }}
.where {{ color: var(--accent); font-weight: 600; }}
.tag {{ margin: 10px 0 0; padding: 4px 8px; background: var(--tag-bg); border-radius: 6px;
  font-size: 13px; display: inline-block; }}
.cols {{ display: grid; grid-template-columns: 3fr 2fr; gap: 16px; margin-top: 10px; }}
h4 {{ margin: 0 0 4px; font-size: 12px; text-transform: uppercase; letter-spacing: .04em;
  color: var(--muted); }}
ul {{ margin: 0; padding-left: 18px; }}
li {{ margin: 2px 0; }}
.gaps li {{ color: var(--gap); }}
.note {{ margin: 8px 0 0; color: var(--muted); font-size: 13px; }}
.foot {{ display: flex; justify-content: space-between; align-items: center; gap: 12px;
  margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); font-size: 13px;
  flex-wrap: wrap; }}
a {{ color: var(--accent); }}
.copy {{ font: inherit; font-size: 13px; padding: 5px 10px; border-radius: 6px; cursor: pointer;
  border: 1px solid var(--line); background: var(--bg); color: var(--text); }}
.copy.done {{ color: var(--hi); border-color: var(--hi); }}
details {{ margin-top: 20px; background: var(--surface); border: 1px solid var(--line);
  border-radius: 10px; padding: 10px 14px; }}
summary {{ cursor: pointer; font-weight: 600; }}
.rows {{ margin-top: 8px; font-size: 14px; }}
.muted {{ color: var(--muted); }}
footer {{ margin-top: 40px; font-size: 13px; color: var(--muted); }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0; }}
td {{ padding: 4px 8px 4px 0; border-bottom: 1px solid var(--line); vertical-align: top; }}
td.num {{ text-align: right; width: 56px; padding-right: 16px; font-variant-numeric: tabular-nums; }}
.dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }}
.dot.ok {{ background: var(--hi); }} .dot.off {{ background: var(--lo); }} .dot.err {{ background: var(--gap); }}
@media (max-width: 640px) {{
  .cols {{ grid-template-columns: 1fr; }}
  .score {{ width: 40px; height: 40px; font-size: 16px; }}
}}
</style>
</head>
<body>
<main>
<header>
  <h1>New jobs in Madrid</h1>
  <p>{esc(date)} · posted in the last {data["hours"]} hours · {len(jobs)} new after filters, {len(by_n)} read in full</p>
</header>
{f'<p class="summary">{esc(summary)}</p>' if summary else ""}
{section("Apply today", apply, "Nothing above " + str(APPLY) + " today.")}
{section("Worth a look", look, "Nothing between " + str(LOOK) + " and " + str(APPLY - 1) + " today.")}
{folded("Read and set aside", [row(j, (s.get("gaps") or s.get("why") or [""])[0], ref) for j, s in low])}
{folded("Same role already applied to", [row(j, s.get("same_role_applied"), ref) for j, s in applied])}
{folded("Not shortlisted from the title", [row(j, triage.get(j["n"], ""), ref) for j in rest])}
<footer>
  <h2>Sources</h2>
  <table>{"".join(src_rows)}</table>
  {f'<p>Boards that failed: {esc(", ".join(f"{k} ({v})" for k, v in board_errors.items()))}</p>' if board_errors else ""}
  <p>{funnel}</p>
  {"".join(f"<p>{esc(l)}</p>" for l in data.get("log", []))}
</footer>
</main>
<script>
document.querySelectorAll('.copy').forEach(b => b.addEventListener('click', async () => {{
  try {{ await navigator.clipboard.writeText(b.dataset.cmd); }}
  catch (e) {{ window.prompt('Copy this:', b.dataset.cmd); return; }}
  b.textContent = 'Copied'; b.classList.add('done');
  setTimeout(() => {{ b.textContent = 'Copy /tailor-cv'; b.classList.remove('done'); }}, 1500);
}}));
</script>
</body>
</html>
"""
    reports = scan.SCAN / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    out = reports / f"{run_dir.name}.html"
    out.write_text(page)

    # Everything in this run counts as shown, scored or not: it won't come back tomorrow.
    scan.STATE.mkdir(parents=True, exist_ok=True)
    seen = scan.load(scan.STATE / "seen.json", {})
    today = datetime.now(timezone.utc).date().isoformat()
    for j in jobs:
        seen.setdefault(j["key"], today)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).date().isoformat()
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    (scan.STATE / "seen.json").write_text(json.dumps(seen, ensure_ascii=False, indent=0))
    (scan.STATE / "last_run.json").write_text(json.dumps({"collected_at": data["collected_at"]}))
    (run_dir / "report.done").write_text(out.name)

    print(f"Apply today: {len(apply)} · Worth a look: {len(look)} · Set aside: {len(low)} · "
          f"Already applied: {len(applied)} · Not shortlisted: {len(rest)}")
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1])
