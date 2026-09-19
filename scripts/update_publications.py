#!/usr/bin/env python3
"""Find lab papers that aren't on the publications page yet.

    python3 scripts/update_publications.py              # what's new?
    python3 scripts/update_publications.py --add        # ...and put it in the bib
    python3 scripts/update_publications.py --arxiv      # fill in missing arXiv links
    python3 scripts/update_publications.py --months     # fill in missing publication months
    python3 scripts/update_publications.py --dois       # fill in missing DOIs
    python3 scripts/update_publications.py --find NAME  # look up an author ID
    python3 scripts/update_publications.py --all        # every paper found
    python3 scripts/update_publications.py --since 2024 # only recent years

Why not Google Scholar: it has no API, its terms forbid scripted access, and it
blocks scripts by IP. This reads OpenAlex (openalex.org) instead, which is open,
documented, and covers CHI/UIST/CSCW/ACL/EMNLP.

A paper belongs on the site when at least one LiLab member is on it (Tal not
required) and it is from `first_year` in _config.yml onwards.

Without --add nothing is written; you just get the report. With --add, new
papers are written straight into _data/publications.bib marked `draft = {true}`,
which keeps them off the site until you have checked them. Review each one -
fix the venue, add the PDF and any code or video links - then delete its
`draft` line and run scripts/build_publications.py.

Standard library only - no pip install needed.
"""

import argparse
import datetime
import difflib
import time
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bibtex  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHORS_YML = os.path.join(REPO, "_data", "lab_authors.yml")
PEOPLE_YML = os.path.join(REPO, "_data", "people.yml")
PUBS_BIB = os.path.join(REPO, "_data", "publications.bib")
CONFIG = os.path.join(REPO, "_config.yml")
BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_publications.py")

API = "https://api.openalex.org"
WORK_FIELDS = (
    "id,doi,title,publication_year,publication_date,type,authorships,"
    "primary_location,best_oa_location,open_access,ids,is_retracted"
)


# --------------------------------------------------------------------------
# Tiny YAML reader. Handles exactly the shape of our _data files: a top-level
# mapping whose values are lists of "key: value" blocks. PyYAML is used when
# it happens to be installed, but it is not required.
# --------------------------------------------------------------------------

def load_yaml(path):
    """Read the block-style YAML in _data/. PyYAML is used when it happens to be
    installed; otherwise the small parser below handles the subset these files
    use - nested mappings and sequences, comments, quoted or plain scalars."""
    try:
        import yaml  # noqa
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        pass

    lines = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            text = raw.rstrip("\n")
            if not text.strip() or text.lstrip().startswith("#"):
                continue
            lines.append((len(text) - len(text.lstrip()), text.strip()))

    value, _ = _parse_block(lines, 0, lines[0][0] if lines else 0)
    return value if isinstance(value, dict) else {}


def _parse_block(lines, i, indent):
    if i < len(lines) and lines[i][1].startswith("- "):
        return _parse_seq(lines, i, indent)
    return _parse_map(lines, i, indent)


def _parse_map(lines, i, indent):
    out = {}
    while i < len(lines):
        depth, text = lines[i]
        if depth < indent or text.startswith("- "):
            break
        if depth > indent:              # stray deeper line; skip it
            i += 1
            continue
        if ":" not in text:
            i += 1
            continue
        key, rest = text.split(":", 1)
        key, rest = key.strip(), _strip_comment(rest).strip()
        if rest:
            out[key] = _scalar(rest)
            i += 1
            continue
        nxt = _next_line(lines, i + 1)
        if nxt is not None and (nxt[0] > indent or
                                (nxt[0] == indent and nxt[1].startswith("- "))):
            out[key], i = _parse_block(lines, i + 1, nxt[0])
        else:
            out[key] = []
            i += 1
    return out, i


def _parse_seq(lines, i, indent):
    out = []
    while i < len(lines):
        depth, text = lines[i]
        if depth != indent or not (text.startswith("- ") or text == "-"):
            break
        rest = _strip_comment(text[1:]).strip()
        if not rest:                                   # value on following lines
            nxt = _next_line(lines, i + 1)
            if nxt is not None and nxt[0] > indent:
                item, i = _parse_block(lines, i + 1, nxt[0])
                out.append(item)
            else:
                out.append(None)
                i += 1
            continue
        if ":" in rest and not rest.startswith(("\"", "'")):
            # "- key: value", possibly with more keys indented beneath it
            inner = indent + (len(text) - len(text.lstrip("- ")))
            head = [(inner, rest)] + lines[i + 1:]
            item, used = _parse_map(head, 0, inner)
            out.append(item)
            i += used
            continue
        out.append(_scalar(rest))
        i += 1
    return out, i


def _next_line(lines, i):
    return lines[i] if i < len(lines) else None


def _strip_comment(text):
    out, quote = [], None
    for ch in text:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and out and out[-1] in " \t":
            break
        out.append(ch)
    return "".join(out)


def _scalar(val):
    val = val.strip()
    if val in ("[]", "{}", "~", "null", ""):
        return []
    if val.startswith("[") and val.endswith("]"):
        return [_scalar(p) for p in val[1:-1].split(",") if p.strip()]
    if len(val) > 1 and val[0] in "\"'" and val[0] == val[-1]:
        body = val[1:-1]
        return body.replace('\\"', '"') if val[0] == '"' else body
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    if val in ("true", "false"):
        return val == "true"
    return val


# --------------------------------------------------------------------------
# OpenAlex
# --------------------------------------------------------------------------

def get(path, **params):
    url = API + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "LiLab-site-publication-check"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 429:
            sys.exit("OpenAlex rate limit reached (it allows a small number of\n"
                     "free calls per day per IP). Try again tomorrow, or get a free\n"
                     "key at openalex.org and set OPENALEX_API_KEY.")
        sys.exit(f"OpenAlex returned HTTP {err.code} for {url}")
    except urllib.error.URLError as err:
        sys.exit(f"Could not reach OpenAlex: {err.reason}")


def api_key_params():
    key = os.environ.get("OPENALEX_API_KEY")
    return {"api_key": key} if key else {}


def works_for(author_id):
    """Every work OpenAlex attributes to one author ID."""
    out, cursor = [], "*"
    while cursor:
        page = get("/works",
                   filter=f"author.id:{author_id}",
                   select=WORK_FIELDS,
                   **{"per-page": 200, "cursor": cursor},
                   **api_key_params())
        out.extend(page.get("results", []))
        cursor = (page.get("meta") or {}).get("next_cursor")
    return out


def find_author(name):
    page = get("/authors", search=name, **{"per-page": 8},
               select="id,display_name,works_count,last_known_institutions",
               **api_key_params())
    results = page.get("results", [])
    if not results:
        print(f"No OpenAlex author found for {name!r}.")
        return
    print(f"OpenAlex authors matching {name!r}:\n")
    for a in results:
        where = ", ".join(i.get("display_name", "")
                          for i in (a.get("last_known_institutions") or [])) or "-"
        print(f"  {a['id'].rsplit('/', 1)[-1]:<14} {a['display_name']:<28} "
              f"{a['works_count']:>4} works   {where[:60]}")
    print("\nOpen https://openalex.org/<ID> to see which one has the right papers,\n"
          "then add that ID to _data/lab_authors.yml.")


def fill_months(all_works, names, institutions, extra):
    """Add `month = {...}` from the catalogue's publication date, so papers sort
    by when they actually appeared rather than by where they sit in the file."""
    dated = {}
    for work in all_works:
        date = work.get("publication_date") or ""
        if len(date) >= 7 and work.get("title"):
            dated[normalise(work["title"])] = date

    with open(PUBS_BIB, encoding="utf-8") as fh:
        text = fh.read()
    entries = bibtex.parse(text)
    missing = [e for e in entries if not e["fields"].get("month")]
    hits = []
    for entry in missing:
        title = bibtex.unlatex(entry["fields"].get("title", ""))
        date = dated.get(normalise(title))
        if not date:
            best, score = None, 0.0
            for other, value in dated.items():
                ratio = difflib.SequenceMatcher(None, normalise(title), other).ratio()
                if ratio > score:
                    best, score = value, ratio
            date = best if score >= 0.9 else None
        if not date:
            continue
        year, month = date[:4], int(date[5:7])
        if year != re.sub(r"\D", "", entry["fields"].get("year", "")):
            continue               # catalogue disagrees about the year; leave it alone
        entry["fields"]["month"] = MONTH_NAMES[month - 1]
        hits.append(entry)
        print(f"  {date[:7]}  {title[:66]}")

    for entry in sorted(hits, key=lambda e: -e["start"]):
        text = text[:entry["start"]] + bibtex.format_entry(entry) + text[entry["end"]:]
    with open(PUBS_BIB, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"\n{len(hits)} month(s) added to {os.path.relpath(PUBS_BIB, REPO)}")
    return len(hits)


def catalogue_by_title(works, field):
    """{normalised title: value} for a field of the catalogue records. A paper
    usually appears twice - preprint and published - so for DOIs prefer the
    published one; 10.48550 is just the arXiv posting."""
    out = {}
    for work in works:
        title, value = work.get("title"), work.get(field)
        if not title or not value:
            continue
        key = normalise(title)
        if key in out and not str(out[key]).replace("https://doi.org/", "").startswith("10.48550"):
            continue
        out[key] = value
    return out


def match_value(title, table):
    """Exact, else the closest title above 0.9 - published titles drift."""
    key = normalise(title)
    if key in table:
        return table[key]
    best, score = None, 0.0
    for other, value in table.items():
        ratio = difflib.SequenceMatcher(None, key, other).ratio()
        if ratio > score:
            best, score = value, ratio
    return best if score >= 0.9 else None


def fill_dois(all_works):
    """Add `doi = {...}` to bib entries that have none, from the catalogue."""
    table = catalogue_by_title(all_works, "doi")
    with open(PUBS_BIB, encoding="utf-8") as fh:
        text = fh.read()
    entries = bibtex.parse(text)
    hits = []
    for entry in entries:
        if entry["fields"].get("doi"):
            continue
        title = bibtex.unlatex(entry["fields"].get("title", ""))
        doi = match_value(title, table)
        if not doi:
            continue
        doi = doi.replace("https://doi.org/", "")
        if doi.startswith("10.48550"):
            continue               # that is just the arXiv DOI
        entry["fields"]["doi"] = doi
        hits.append(entry)
        print(f"  {doi:34s} {title[:56]}")

    for entry in sorted(hits, key=lambda e: -e["start"]):
        text = text[:entry["start"]] + bibtex.format_entry(entry) + text[entry["end"]:]
    with open(PUBS_BIB, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"\n{len(hits)} DOI(s) added to {os.path.relpath(PUBS_BIB, REPO)}")
    return len(hits)


MONTH_NAMES = "jan feb mar apr may jun jul aug sep oct nov dec".split()


# --------------------------------------------------------------------------
# arXiv
# --------------------------------------------------------------------------

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS = {"a": "http://www.w3.org/2005/Atom"}


def arxiv_id_for(title):
    """The arXiv id for a paper, by title. Returns None unless what comes back
    really is the same paper - a near miss here would put someone else's
    preprint on the page."""
    query = urllib.parse.urlencode({
        "search_query": 'ti:"%s"' % title.replace('"', ""),
        "max_results": 5,
        "start": 0,
    })
    req = urllib.request.Request(f"{ARXIV_API}?{query}",
                                 headers={"User-Agent": "LiLab-site-publication-check"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            feed = ET.fromstring(resp.read())
    except Exception:
        return None

    want = normalise(title)
    for entry in feed.findall("a:entry", ARXIV_NS):
        found = (entry.findtext("a:title", "", ARXIV_NS) or "").strip()
        if difflib.SequenceMatcher(None, want, normalise(found)).ratio() < 0.95:
            continue
        m = re.search(r"arxiv\.org/abs/(.+?)(?:v\d+)?$",
                      entry.findtext("a:id", "", ARXIV_NS) or "")
        if m:
            return m.group(1)
    return None


def fill_arxiv():
    """Add `arxiv = {...}` to every bib entry that hasn't got one."""
    with open(PUBS_BIB, encoding="utf-8") as fh:
        text = fh.read()
    entries = bibtex.parse(text)
    missing = [e for e in entries if not e["fields"].get("arxiv")]
    print(f"{len(missing)} of {len(entries)} entries have no arXiv link; asking arXiv "
          f"(~{len(missing) * 3}s - it asks for a pause between queries)\n")

    hits = []
    for entry in missing:
        title = bibtex.unlatex(entry["fields"].get("title", ""))
        ident = arxiv_id_for(title)
        print(f"  {('found ' + ident) if ident else 'none':18s} {title[:62]}")
        if ident:
            entry["fields"]["arxiv"] = ident
            hits.append(entry)
        time.sleep(3)          # arXiv asks for one query every three seconds

    # splice back to front so earlier offsets stay valid
    for entry in sorted(hits, key=lambda e: -e["start"]):
        text = text[:entry["start"]] + bibtex.format_entry(entry) + text[entry["end"]:]

    with open(PUBS_BIB, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"\n{len(hits)} arXiv link(s) added to {os.path.relpath(PUBS_BIB, REPO)}")
    return len(hits)


# --------------------------------------------------------------------------
# Shaping a work into what the papers page shows
# --------------------------------------------------------------------------

def venue_of(work, aliases):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    # ACM records usually have source == null, with the venue only in raw_source_name
    name = src.get("display_name") or loc.get("raw_source_name") or ""
    low = name.lower()
    for alias in aliases:
        if alias.get("match", "").lower() in low:
            return alias.get("name", name)
    return name


def is_preprint(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    if src.get("type") == "repository":
        return True
    if work.get("type") == "preprint":
        return True
    if loc.get("is_published") is False and loc.get("version") == "submittedVersion":
        return True
    return "arxiv" in (venue_of(work, []) or "").lower()


def arxiv_url(work):
    doi = (work.get("doi") or "").lower()
    m = re.search(r"10\.48550/arxiv\.(.+)$", doi)
    if m:
        return "https://arxiv.org/abs/" + m.group(1)
    for loc in filter(None, [work.get("primary_location"), work.get("best_oa_location")]):
        url = loc.get("landing_page_url") or ""
        m = re.search(r"arxiv\.org/abs/([^\s?#]+)", url)
        if m:
            return "https://arxiv.org/abs/" + m.group(1)
    return None


def pdf_url(work):
    for loc in filter(None, [work.get("best_oa_location"), work.get("primary_location")]):
        if loc.get("pdf_url"):
            return loc["pdf_url"]
    return (work.get("open_access") or {}).get("oa_url")


def normalise(title):
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


def merge(works):
    """One entry per paper. Published versions win over their own preprints."""
    by_key = {}
    for w in works:
        if w.get("is_retracted") or not w.get("title"):
            continue
        key = normalise(w["title"])[:80]
        if not key:
            continue
        kept = by_key.get(key)
        if kept is None:
            by_key[key] = w
            continue
        # prefer the peer-reviewed record, then the later one
        if is_preprint(kept) and not is_preprint(w):
            by_key[key] = w
        elif is_preprint(kept) == is_preprint(w):
            if (w.get("publication_year") or 0) > (kept.get("publication_year") or 0):
                by_key[key] = w
    return list(by_key.values())


def lab_authors_on(work, names):
    """(name, institutions) for every author on `work` who is a lab member."""
    out = []
    for a in work.get("authorships") or []:
        name = ((a.get("author") or {}).get("display_name")
                or a.get("raw_author_name") or "")
        if name in names:
            out.append((name, [i.get("display_name", "")
                               for i in (a.get("institutions") or [])]))
    return out


def is_lab_paper(work, names, institutions, extra_by_person=None):
    """The rule: at least one LiLab member on the paper (Tal not required),
    from `first_year` onwards - the year filter is applied by the caller.

    The wrinkle is that OpenAlex merges different people who share a name; one
    "Yifan Song" record carries neutron-star physics alongside our Yifan's
    papers. So a name match alone is not enough: the lab member has to be on it
    under one of our institutions, or two lab members have to be on it
    together."""
    extra_by_person = extra_by_person or {}
    people = lab_authors_on(work, names)
    if len({n for n, _ in people}) >= 2:
        return True
    for person, insts in people:
        allowed = list(institutions) + list(extra_by_person.get(person, []))
        for inst in insts:
            if any(known.lower() in inst.lower() for known in allowed):
                return True
    return False


# --------------------------------------------------------------------------
# The existing page
# --------------------------------------------------------------------------

def listed_papers():
    """{normalised title: (title, type)} for everything already in the bib,
    drafts included - so re-running --add cannot add the same paper twice."""
    with open(PUBS_BIB, encoding="utf-8") as fh:
        entries = bibtex.parse(fh.read())
    out = {}
    for entry in entries:
        title = bibtex.unlatex(entry["fields"].get("title", ""))
        if not title:
            continue
        kind = "preprint" if "non-peer-review" in (entry["fields"].get("keywords") or "") \
            else "peer-reviewed"
        out[normalise(title)] = (title, kind)
    return out


def first_year():
    settings = load_yaml(CONFIG).get("publications") or {}
    return int(settings.get("first_year") or 0)


def match_on_page(title, entries):
    """Exact match, or the closest near-match. Published titles often differ a
    little from the arXiv title already on the page, so exact matching alone
    would report papers you have listed for years as brand new."""
    key = normalise(title)
    if key in entries:
        return entries[key], 1.0
    best, score = None, 0.0
    for other, entry in entries.items():
        ratio = difflib.SequenceMatcher(None, key, other).ratio()
        if ratio > score:
            best, score = entry, ratio
    return (best, score) if score >= 0.82 else (None, score)


def lab_names():
    names = set()
    people = load_yaml(PEOPLE_YML)
    for group in ("current", "alumni"):
        for person in people.get(group) or []:
            name = person.get("name")
            if name:
                names.add(re.sub(r"\s*\([^)]*\)", "", name).strip())
    for entry in load_yaml(AUTHORS_YML).get("authors") or []:
        if entry.get("name"):
            names.add(entry["name"])
    return names


def author_html(work, names):
    parts = []
    for a in work.get("authorships") or []:
        name = (a.get("author") or {}).get("display_name") or a.get("raw_author_name") or ""
        if not name:
            continue
        name = html.escape(name)
        parts.append(f"<strong>{name}</strong>" if name in names else name)
    return ", ".join(parts)


def bib_key(work, existing):
    """surnameYYYYfirstword, the usual shape, made unique."""
    authors = work.get("authorships") or []
    surname = "anon"
    if authors:
        name = ((authors[0].get("author") or {}).get("display_name")
                or authors[0].get("raw_author_name") or "")
        parts = [p for p in re.split(r"\s+", name) if p]
        if parts:
            surname = re.sub(r"[^A-Za-z]", "", parts[-1]).lower() or "anon"
    word = re.sub(r"[^A-Za-z]", "", (work.get("title") or "x").split()[0])[:10].lower()
    key = f"{surname}{work.get('publication_year') or ''}{word}"
    while key in existing:
        key += "a"
    existing.add(key)
    return key


def bib_authors(work):
    """OpenAlex gives 'Yijun Liu'; BibTeX wants 'Liu, Yijun'."""
    out = []
    for a in work.get("authorships") or []:
        name = ((a.get("author") or {}).get("display_name")
                or a.get("raw_author_name") or "").strip()
        if not name:
            continue
        parts = name.split()
        out.append(f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else name)
    return " and ".join(out)


def bib_entry(work, aliases, existing):
    """A new entry for _data/publications.bib, marked as a draft."""
    pre = is_preprint(work)
    fields = [
        ("title", work["title"]),
        ("author", bib_authors(work)),
        ("booktitle", (work.get("primary_location") or {}).get("raw_source_name")
                      or venue_of(work, [])),
        ("venue", venue_of(work, aliases) or "TODO"),
        ("year", str(work.get("publication_year") or "TODO")),
        ("month", MONTH_NAMES[int((work.get("publication_date") or "0000-00")[5:7]) - 1]
                  if (work.get("publication_date") or "")[5:7].isdigit()
                  and 1 <= int((work.get("publication_date") or "0000-00")[5:7]) <= 12 else ""),
        ("keywords", "non-peer-review" if pre else "peer-review"),
        ("draft", "true"),
        ("added", datetime.date.today().isoformat()),
    ]

    arxiv = arxiv_url(work)
    if arxiv:
        fields.append(("arxiv", arxiv.rsplit("/", 1)[-1]))
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    if doi and not doi.startswith("10.48550"):
        fields.append(("doi", doi))
    pdf = pdf_url(work)
    if pdf and ".pdf" in pdf.lower() and not arxiv:
        fields.append(("pdf", pdf))

    fields = {k: re.sub(r"\s+", " ", str(v)).strip() for k, v in fields if v}
    return {"key": bib_key(work, existing), "type": "inproceedings", "fields": fields}


def add_to_bib(works, aliases):
    """Splice each new paper into the bib, newest-first order preserved."""
    with open(PUBS_BIB, encoding="utf-8") as fh:
        text = fh.read()
    existing = {e["key"] for e in bibtex.parse(text)}
    added = []
    for work in works:
        entry = bib_entry(work, aliases, existing)
        text = bibtex.insert(text, entry)
        added.append(entry)
    with open(PUBS_BIB, "w", encoding="utf-8") as fh:
        fh.write(text)
    return added


def rebuild():
    result = subprocess.run([sys.executable, BUILD], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def pending_drafts():
    with open(PUBS_BIB, encoding="utf-8") as fh:
        return [e for e in bibtex.parse(fh.read())
                if (e["fields"].get("draft") or "").lower() in ("true", "yes", "1")]


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--find", metavar="NAME", help="look up an author's OpenAlex ID")
    ap.add_argument("--all", action="store_true", help="list every paper, not just new ones")
    ap.add_argument("--since", type=int, metavar="YEAR",
                    help="ignore papers before YEAR (default: first_year in publications.yml)")
    ap.add_argument("--loose", action="store_true",
                    help="skip the same-name filter and show everything on these author records")
    ap.add_argument("--add", action="store_true",
                    help="write the new papers into _data/publications.bib as drafts")
    ap.add_argument("--arxiv", action="store_true",
                    help="look up an arXiv link for every bib entry that lacks one")
    ap.add_argument("--months", action="store_true",
                    help="fill in the publication month of every bib entry that lacks one")
    ap.add_argument("--dois", action="store_true",
                    help="fill in the DOI of every bib entry that lacks one")
    args = ap.parse_args()

    if args.find:
        find_author(args.find)
        return

    if args.arxiv:
        if fill_arxiv():
            rebuild()
        return

    config = load_yaml(AUTHORS_YML)
    authors = config.get("authors") or []
    aliases = config.get("venue_aliases") or []
    institutions = [i.get("name", "") for i in (config.get("institutions") or [])] or \
                   ["University of Illinois Urbana-Champaign"]
    extra = {a["name"]: ([a["also_at"]] if isinstance(a.get("also_at"), str) else a.get("also_at") or [])
             for a in authors if a.get("name")}
    if not authors:
        sys.exit(f"No authors configured in {AUTHORS_YML}")

    works = []
    for entry in authors:
        ids = entry.get("openalex")
        ids = [ids] if isinstance(ids, str) else (ids or [])
        for author_id in ids:
            print(f"  fetching {entry.get('name', author_id)} ({author_id}) ...", file=sys.stderr)
            works.extend(works_for(author_id))

    names = lab_names()

    if args.months:
        if fill_months(works, names, institutions, extra):
            rebuild()
        return

    if args.dois:
        if fill_dois(works):
            rebuild()
        return

    fetched = len(works)
    if not args.loose:
        works = [w for w in works if is_lab_paper(w, names, institutions, extra)]

    papers = merge(works)
    since = args.since if args.since is not None else first_year()
    if since:
        papers = [w for w in papers if (w.get("publication_year") or 0) >= since]
    papers.sort(key=lambda w: (w.get("publication_year") or 0, w.get("title") or ""), reverse=True)

    listed = listed_papers()
    new, renamed, matched = [], [], []
    for w in papers:
        match, score = match_on_page(w["title"], listed)
        if match is None:
            new.append(w)
        elif score < 1.0:
            renamed.append((match, w))
        else:
            matched.append((match, w))

    print(f"\n{fetched} records on those author profiles -> {len(papers)} lab papers"
          f"{'' if args.loose else ', same-name matches dropped'}"
          f"{f', {since} onwards' if since else ''}.")
    print(f"{len(listed)} papers in _data/publications.bib. {len(new)} look new.\n")

    for w in (papers if args.all else new):
        tag = "preprint" if is_preprint(w) else "peer-reviewed"
        flag = "NEW " if w in new else "    "
        who = ", ".join(sorted({n for n, _ in lab_authors_on(w, names)})) or "?"
        print(f"{flag}{w.get('publication_year')}  [{tag:13s}] {w['title'][:70]}")
        print(f"                            {venue_of(w, aliases) or '(no venue)'}"
              f"  |  {who}")

    if renamed:
        print("\nListed already, but the published title differs - worth a look:")
        for (page_title, _), w in renamed:
            print(f"  listed:    {page_title[:76]}")
            print(f"  published: {w['title'][:76]}  ({venue_of(w, aliases)} {w.get('publication_year')})")

    moved = [(title, venue_of(w, aliases), w.get("publication_year"))
             for (title, kind), w in matched + renamed
             if kind == "preprint" and not is_preprint(w)]
    if moved:
        print("\nType is preprint in publications.yml, but the catalogue now has a venue:")
        for title, venue, year in moved:
            print(f"  - {title[:68]}\n      -> {venue} {year}")

    if new and args.add:
        added = add_to_bib(new, aliases)
        print(f"\nAdded {len(added)} entr{'y' if len(added) == 1 else 'ies'} "
              f"to {os.path.relpath(PUBS_BIB, REPO)} as drafts:")
        for entry in added:
            print(f"  {entry['key']:28s} {entry['fields']['title'][:58]}")
        print()
        rebuild()
        print("\nEach one needs a look before it reaches the site:")
        print("  - check the venue; catalogue names are long")
        print("  - workshop papers arrive as keywords = {peer-review}; switch them to")
        print("    non-peer-review and add badge = {Workshop} if they belong with the preprints")
        print("  - add pdf = {...} once the paper is in resources/paper/pdf/,")
        print("    plus code / video / demo / data / slides / blog while you are there")
        print("  - then delete the `draft = {true}` line and re-run build_publications.py")
    elif new:
        print(f"\nRun again with --add to write these into "
              f"{os.path.relpath(PUBS_BIB, REPO)} as drafts.")
    else:
        print("\nNothing new to add.")

    waiting = pending_drafts()
    if waiting:
        print(f"\n{len(waiting)} draft entr{'y' if len(waiting) == 1 else 'ies'} "
              f"still waiting on review in {os.path.relpath(PUBS_BIB, REPO)}:")
        for entry in waiting:
            print(f"  {entry['key']:28s} "
                  f"added {entry['fields'].get('added', '?')}  "
                  f"{entry['fields'].get('title', '')[:48]}")

if __name__ == "__main__":
    main()
