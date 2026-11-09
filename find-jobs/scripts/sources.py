"""One function per job source. Standard library only.

Every source returns a list of job dicts with the same keys (see `job()`), so scan.py can
filter and merge them without knowing where they came from. A source that fails raises; scan.py
catches it and reports the error, so one broken source never stops the run.
"""

import base64
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
NOW = datetime.now(timezone.utc)
RETRIES = 5  # find_board.py lowers it: a wrong guess should fail fast, not retry
STATS = {"requests": 0, "rate_limited": 0}


# ---------------------------------------------------------------- helpers

def fetch(url, data=None, headers=None, retries=None, timeout=25):
    """GET (or POST when data is given) with a polite retry on 429 and 5xx."""
    retries = retries or RETRIES
    hdrs = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9,es;q=0.8"}
    hdrs.update(headers or {})
    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()
        hdrs.setdefault("Content-Type", "application/json")
    for attempt in range(retries):
        STATS["requests"] += 1
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                STATS["rate_limited"] += e.code == 429
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise


def fetch_json(url, **kw):
    return json.loads(fetch(url, **kw))


def text(s):
    """HTML (possibly escaped twice) to plain text."""
    if not s:
        return ""
    s = html.unescape(html.unescape(s))
    s = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def parse_date(s):
    """ISO string, epoch milliseconds or RFC 822 date to an aware datetime (or None)."""
    if s in (None, ""):
        return None
    if isinstance(s, (int, float)):
        return datetime.fromtimestamp(s / 1000, timezone.utc)
    s = str(s).strip()
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, fmt)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def ago(label):
    """'3 hours ago', 'hace 2 días', 'Posted Yesterday' to a datetime (or None)."""
    l = label.lower()
    if "today" in l or "just now" in l or "hoy" in l:
        return NOW
    if "yesterday" in l or "ayer" in l:
        return NOW - timedelta(days=1)
    m = re.search(r"(\d+)\+?\s*(second|minute|hour|day|week|month|segundo|minuto|hora|d[ií]a|semana|mes)", l)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    secs = {"sec": 1, "seg": 1, "min": 60, "hou": 3600, "hor": 3600, "day": 86400, "dí": 86400,
            "di": 86400, "wee": 604800, "sem": 604800, "mon": 2592000, "mes": 2592000}
    for k, v in secs.items():
        if unit.startswith(k):
            return NOW - timedelta(seconds=n * v)
    return None


def iso(d):
    return d.astimezone(timezone.utc).isoformat(timespec="minutes") if d else None


def job(source, sid, company, title, location, url, posted=None, remote=None,
        description="", extra=None):
    return {
        "id": f"{source}:{sid}",
        "source": source,
        "company": (company or "").strip(),
        "title": " ".join((title or "").split()),
        "location": " ".join((location or "").split()),
        "remote": remote,
        "posted_at": iso(posted),
        "url": url,
        "description": description or "",
        "extra": extra or {},
    }


# ---------------------------------------------------------------- LinkedIn

LI_SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
LI_JOB = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"
LI_MADRID = "Madrid, Community of Madrid, Spain"


def _li_cards(page):
    out = []
    for chunk in page.split("<li>")[1:]:
        m = re.search(r"jobPosting:(\d+)", chunk)
        if not m:
            continue
        def grab(pattern):
            g = re.search(pattern, chunk, re.S)
            return html.unescape(" ".join(re.sub(r"<[^>]+>", " ", g.group(1)).split())) if g else ""
        out.append({
            "id": m.group(1),
            "title": grab(r'base-search-card__title">(.*?)</h3>'),
            "company": grab(r'base-search-card__subtitle">(.*?)</h4>'),
            "location": grab(r'job-search-card__location">(.*?)</span>'),
            "ago": grab(r"<time[^>]*>(.*?)</time>"),
            "date": (re.search(r'datetime="([^"]+)"', chunk) or [None, None])[1],
        })
    return out


def linkedin(terms, hours, log, madrid_pages=3, remote_pages=1, pause=1.5):
    """Logged-out LinkedIn job search: every term, in Madrid and as remote in Spain.

    LinkedIn ranks by relevance, so each term returns a slice of the same daily pool and the
    terms overlap. A term stops paging as soon as a page brings nothing new. Its rate limit,
    not the number of terms, is what makes this slow: the run logs both counts."""
    seconds = int(hours * 3600)
    before = dict(STATS)
    searches = [("Madrid", {"location": LI_MADRID}, madrid_pages, False),
                ("Spain remote", {"location": "Spain", "f_WT": "2"}, remote_pages, True)]
    jobs, seen = {}, set()
    for i, term in enumerate(terms, 1):
        print(f"  linkedin {i}/{len(terms)}: {term} ({len(jobs)} so far)", file=sys.stderr, flush=True)
        for label, params, pages, remote in searches:
            for p in range(pages):
                q = {"keywords": term, "f_TPR": f"r{seconds}", "start": p * 10, **params}
                try:
                    cards = _li_cards(fetch(LI_SEARCH + urllib.parse.urlencode(q)))
                except urllib.error.HTTPError as e:
                    log(f"linkedin: '{term}' {label} page {p + 1}: HTTP {e.code}")
                    break
                new = [c for c in cards if c["id"] not in seen]
                for c in new:
                    seen.add(c["id"])
                    posted = ago(c["ago"]) or parse_date(c["date"])
                    jobs[c["id"]] = job(
                        "linkedin", c["id"], c["company"], c["title"], c["location"],
                        f"https://www.linkedin.com/jobs/view/{c['id']}/", posted, remote,
                        extra={"search": f"{term} / {label}", "posted_label": c["ago"]})
                time.sleep(pause)
                if len(cards) < 10 or not new:
                    break
    log(f"linkedin: {STATS['requests'] - before['requests']} requests, "
        f"{STATS['rate_limited'] - before['rate_limited']} rate-limit waits")
    return list(jobs.values())


def linkedin_details(job_id):
    """Full ad text and LinkedIn's criteria for one job id (digits only)."""
    page = fetch(LI_JOB + job_id)
    desc = re.search(r'show-more-less-html__markup[^>]*>(.*?)</div>', page, re.S)
    crit = re.findall(r'job-criteria-subheader">\s*(.*?)\s*</h3>.*?job-criteria-text[^>]*>\s*(.*?)\s*</span>',
                      page, re.S)
    applicants = re.search(r'num-applicants__caption[^>]*>\s*(.*?)\s*<', page, re.S)
    out = {"description": text(desc.group(1)) if desc else ""}
    for k, v in crit:
        out[html.unescape(k).strip().lower()] = html.unescape(v).strip()
    if applicants:
        out["applicants"] = html.unescape(applicants.group(1)).strip()
    return out


# ---------------------------------------------------------------- aggregators (need a free key)

def adzuna(terms, hours, env, log, pages=2):
    if not (env.get("ADZUNA_APP_ID") and env.get("ADZUNA_APP_KEY")):
        raise KeyError("not configured")
    days = max(1, -(-int(hours) // 24))
    out = {}
    for term in terms:
        for page in range(1, pages + 1):
            q = {"app_id": env["ADZUNA_APP_ID"], "app_key": env["ADZUNA_APP_KEY"],
                 "what": term, "where": "Madrid", "max_days_old": days,
                 "results_per_page": 50, "sort_by": "date", "content-type": "application/json"}
            d = fetch_json(f"https://api.adzuna.com/v1/api/jobs/es/search/{page}?" + urllib.parse.urlencode(q))
            res = d.get("results", [])
            for r in res:
                loc = ", ".join(r.get("location", {}).get("area", [])[::-1]) or r.get("location", {}).get("display_name", "")
                out[r["id"]] = job("adzuna", r["id"], r.get("company", {}).get("display_name"),
                                   r.get("title"), loc, r.get("redirect_url"),
                                   parse_date(r.get("created")), None, text(r.get("description")),
                                   {"search": term, "snippet_only": True})
            if len(res) < 50:
                break
            time.sleep(0.5)
    return list(out.values())


def jooble(terms, hours, env, log):
    if not env.get("JOOBLE_KEY"):
        raise KeyError("not configured")
    since = (NOW - timedelta(hours=hours)).strftime("%Y-%m-%d")
    out = {}
    for term in terms:
        d = fetch_json(f"https://jooble.org/api/{env['JOOBLE_KEY']}",
                       data={"keywords": term, "location": "Madrid", "datecreatedfrom": since,
                             "ResultOnPage": 50})
        for r in d.get("jobs", []):
            out[r["id"]] = job("jooble", r["id"], r.get("company"), r.get("title"), r.get("location"),
                               r.get("link"), parse_date(r.get("updated")), None, text(r.get("snippet")),
                               {"search": term, "snippet_only": True, "via": r.get("source")})
        time.sleep(0.5)
    return list(out.values())


def infojobs(terms, hours, env, log):
    if not (env.get("INFOJOBS_CLIENT_ID") and env.get("INFOJOBS_CLIENT_SECRET")):
        raise KeyError("not configured")
    since = "_24_HOURS" if hours <= 24 else "_7_DAYS"
    auth = base64.b64encode(f"{env['INFOJOBS_CLIENT_ID']}:{env['INFOJOBS_CLIENT_SECRET']}".encode()).decode()
    out = {}
    for term in terms:
        q = {"q": term, "province": "madrid", "sinceDate": since, "maxResults": 50}
        d = fetch_json("https://api.infojobs.net/api/9/offer?" + urllib.parse.urlencode(q),
                       headers={"Authorization": f"Basic {auth}"})
        for r in d.get("items") or d.get("offers") or []:
            tele = (r.get("teleworking") or {}).get("value", "")
            loc = ", ".join(x for x in [r.get("city"), (r.get("province") or {}).get("value")] if x)
            out[r["id"]] = job("infojobs", r["id"], (r.get("author") or {}).get("name"), r.get("title"),
                               loc, r.get("link"), parse_date(r.get("published")),
                               "teletrabajo" in tele.lower() and "solo" in tele.lower() or None,
                               "", {"search": term, "snippet_only": True, "teleworking": tele})
        time.sleep(0.5)
    return list(out.values())


# ---------------------------------------------------------------- company job boards

def greenhouse(c):
    d = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{c['slug']}/jobs?content=true")
    out = []
    for r in d.get("jobs", []):
        locs = [r.get("location", {}).get("name", "")] + [o.get("location") or o.get("name", "") for o in r.get("offices", [])]
        out.append(job("greenhouse", r["id"], c["company"], r["title"], " | ".join(x for x in locs if x),
                       r.get("absolute_url"), parse_date(r.get("first_published") or r.get("updated_at")),
                       None, text(r.get("content"))))
    return out


def lever(c):
    host = "api.eu.lever.co" if c.get("eu") else "api.lever.co"
    d = fetch_json(f"https://{host}/v0/postings/{c['slug']}?mode=json")
    out = []
    for r in d:
        cat = r.get("categories", {})
        locs = [cat.get("location", "")] + cat.get("allLocations", [])
        out.append(job("lever", r["id"], c["company"], r["text"], " | ".join(dict.fromkeys(x for x in locs if x)),
                       r.get("hostedUrl"), parse_date(r.get("createdAt")),
                       r.get("workplaceType") == "remote" or None,
                       r.get("descriptionPlain", "") + "\n" + "\n".join(
                           f"{l.get('text')}: {text(l.get('content'))}" for l in r.get("lists", []))))
    return out


def ashby(c):
    d = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{c['slug']}")
    out = []
    for r in d.get("jobs", []):
        if r.get("isListed") is False:
            continue
        locs = [r.get("location", "")] + [s.get("location", "") for s in r.get("secondaryLocations", [])]
        out.append(job("ashby", r["id"], c["company"], r["title"], " | ".join(x for x in locs if x),
                       r.get("jobUrl"), parse_date(r.get("publishedAt")),
                       r.get("isRemote") or r.get("workplaceType") == "Remote" or None,
                       r.get("descriptionPlain", "")))
    return out


def workable(c):
    d = fetch_json(f"https://apply.workable.com/api/v1/widget/accounts/{c['slug']}?details=true")
    out = []
    for r in d.get("jobs", []):
        locs = [", ".join(x for x in [l.get("city"), l.get("region"), l.get("country")] if x)
                for l in r.get("locations", [])] or [", ".join(x for x in [r.get("city"), r.get("country")] if x)]
        out.append(job("workable", r.get("shortcode"), c["company"], r["title"], " | ".join(locs),
                       r.get("url") or r.get("shortlink"),
                       parse_date(r.get("published_on") or r.get("created_at")),
                       r.get("telecommuting") or None, text(r.get("description"))))
    return out


def smartrecruiters(c):
    out, offset = [], 0
    while True:
        d = fetch_json(f"https://api.smartrecruiters.com/v1/companies/{c['slug']}/postings?limit=100&offset={offset}")
        for r in d.get("content", []):
            loc = r.get("location", {})
            out.append(job("smartrecruiters", r["id"], c["company"], r["name"],
                           ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x),
                           f"https://jobs.smartrecruiters.com/{c['slug']}/{r['id']}",
                           parse_date(r.get("releasedDate")), loc.get("remote") or None))
        offset += 100
        if offset >= d.get("totalFound", 0) or offset >= 1000:
            return out


def personio(c):
    root = ET.fromstring(fetch(f"https://{c['slug']}.jobs.personio.de/xml"))
    out = []
    for p in root.findall("position"):
        g = lambda k: (p.findtext(k) or "").strip()
        offices = [g("office")] + [o.text or "" for o in p.findall("additionalOffices/office")]
        desc = "\n".join(f"{d.findtext('name')}: {text(d.findtext('value'))}"
                         for d in p.findall("jobDescriptions/jobDescription"))
        out.append(job("personio", g("id"), c["company"], g("name"), " | ".join(x for x in offices if x),
                       f"https://{c['slug']}.jobs.personio.de/job/{g('id')}", parse_date(g("createdAt")),
                       None, desc))
    return out


def teamtailor(c):
    host = c.get("host") or f"{c['slug']}.teamtailor.com"
    root = ET.fromstring(fetch(f"https://{host}/jobs.rss"))
    ns = {"tt": "https://teamtailor.com/locations"}
    out = []
    for it in root.iter("item"):
        locs = [", ".join(x.text or "" for x in l if x.text) for l in it.findall("tt:locations/tt:location", ns)]
        remote = (it.findtext("remoteStatus") or "").lower()
        out.append(job("teamtailor", it.findtext("guid") or it.findtext("link"), c["company"],
                       it.findtext("title"), " | ".join(locs), it.findtext("link"),
                       parse_date(it.findtext("pubDate")), remote in ("fully", "remote") or None,
                       text(it.findtext("description"))))
    return out


def recruitee(c):
    d = fetch_json(f"https://{c['slug']}.recruitee.com/api/offers/")
    out = []
    for r in d.get("offers", []):
        locs = [", ".join(x for x in [l.get("city"), l.get("country")] if x) for l in r.get("locations", [])]
        locs = locs or [r.get("location", "")]
        out.append(job("recruitee", r["id"], c["company"], r["title"], " | ".join(locs),
                       r.get("careers_url"), parse_date(r.get("published_at") or r.get("created_at")),
                       r.get("remote") or None, text(r.get("description")) + "\n" + text(r.get("requirements"))))
    return out


def workday(c):
    """c['url'] is the public site, e.g. https://hp.wd5.myworkdayjobs.com/ExternalCareerSite."""
    u = urllib.parse.urlparse(c["url"])
    tenant = u.netloc.split(".")[0]
    site = [p for p in u.path.split("/") if p and not re.fullmatch(r"[a-z]{2}-[A-Z]{2}", p)][0]
    api = f"https://{u.netloc}/wday/cxs/{tenant}/{site}"
    out = []
    for offset in range(0, 200, 20):
        d = fetch_json(api + "/jobs", data={"limit": 20, "offset": offset,
                                            "searchText": c.get("search", "Madrid"), "appliedFacets": {}})
        posts = d.get("jobPostings", [])
        for r in posts:
            posted = ago(r.get("postedOn", ""))
            loc, desc = r.get("locationsText", ""), ""
            # The list only says "2 Locations" and "Posted 3 Days Ago": recent ones get the detail
            # call, which has every location, the exact date and the ad text.
            if posted and posted > NOW - timedelta(days=8):
                try:
                    info = fetch_json(api + r["externalPath"]).get("jobPostingInfo", {})
                    loc = " | ".join([info.get("location", "")] + info.get("additionalLocations", []))
                    posted = parse_date(info.get("startDate")) or posted
                    desc = text(info.get("jobDescription"))
                except Exception:
                    pass
            out.append(job("workday", r.get("externalPath"), c["company"], r.get("title"), loc,
                           f"https://{u.netloc}/{site}{r.get('externalPath', '')}", posted, None, desc,
                           {"posted_label": r.get("postedOn")}))
        if len(posts) < 20:
            break
    return out


BOARDS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "workable": workable,
          "smartrecruiters": smartrecruiters, "personio": personio, "teamtailor": teamtailor,
          "recruitee": recruitee, "workday": workday}
