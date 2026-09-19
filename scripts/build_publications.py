#!/usr/bin/env python3
"""Turn _data/publications.bib into _data/publications.yml.

    python3 scripts/build_publications.py           # rebuild the data file
    python3 scripts/build_publications.py --check   # is it up to date?

The bib is what you edit. The YAML is generated from it and committed, because
GitHub Pages builds the site with a fixed plugin list that cannot read BibTeX.
Jekyll turns the YAML into HTML through _includes/publication.html, so the
markup lives in one template rather than being pasted per paper.

Standard library only - no pip install needed.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bibtex  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(REPO, "_data", "publications.bib")
YML = os.path.join(REPO, "_data", "publications.yml")
PDF_DIR = "/resources/paper/pdf/"

# Buttons appear in this order, whichever of them the entry has.
LINK_FIELDS = [
    ("pdf", "PDF"), ("arxiv", "arXiv"), ("doi", "DOI"), ("code", "Code"),
    ("video", "Video"), ("demo", "Demo"), ("data", "Data"), ("slides", "Slides"),
    ("poster", "Poster"), ("talk", "Talk"), ("blog", "Blog"), ("website", "Website"),
]

MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), start=1)}


def entry_month(fields):
    """1-12, or 0 when we cannot tell. Papers without a month keep their file
    order within the year, below anything we can date."""
    raw = (fields.get("month") or "").strip().lower()[:3]
    if raw in MONTHS:
        return MONTHS[raw]
    if raw.isdigit() and 1 <= int(raw) <= 12:
        return int(raw)
    # An arXiv id starts YYMM. That dates a preprint exactly - but on a
    # published paper it dates the preprint, not the publication, so it would
    # sort a CHI paper by when it was posted rather than when it appeared.
    if "non-peer-review" in (fields.get("keywords") or ""):
        m = re.match(r"^(\d{2})(\d{2})\.", (fields.get("arxiv") or "").strip())
        if m and 1 <= int(m.group(2)) <= 12 and \
                str(2000 + int(m.group(1))) == re.sub(r"\D", "", fields.get("year", "")):
            return int(m.group(2))
    return 0


HEADER = """# GENERATED FILE - do not edit by hand. Your changes will be overwritten.
#
# Written by scripts/build_publications.py from _data/publications.bib.
# Add or change a paper in the .bib, then run:
#
#     python3 scripts/build_publications.py
#
# Both files are committed: the bib is the source, this is what Jekyll reads.
# Entries marked `draft = {true}` in the bib are left out until you drop that
# line. An `arxiv` link is only shown on preprints - once a paper is published
# the page links the published version. Settings live in _config.yml.

"""


def link_url(field, value):
    """Bare filenames and arXiv ids expand; anything else is used as written."""
    if value.startswith(("http://", "https://", "/")):
        return value
    if field == "pdf":
        return PDF_DIR + value
    if field == "arxiv":
        return "https://arxiv.org/abs/" + value
    if field == "doi":
        return "https://doi.org/" + value.removeprefix("doi:")
    return value


def yaml_value(text):
    """Quote a scalar unless plain style is unambiguous."""
    text = re.sub(r"\s+", " ", str(text)).strip()
    if not text:
        return '""'
    risky = text[0] in "-?:,[]{}#&*!|>'\"%@`" or ": " in text or " #" in text \
        or text.endswith(":") or text in ("true", "false", "null", "~")
    if risky:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def entry_to_paper(entry):
    f = entry["fields"]
    title = bibtex.unlatex(f.get("title", "")).strip()
    if not title:
        raise ValueError(f"{entry['key']}: no title")

    authors = f.get("authorline") or ", ".join(bibtex.split_authors(f.get("author", "")))
    venue = bibtex.unlatex(f.get("venue") or f.get("booktitle") or f.get("journal") or "")
    year = re.sub(r"\D", "", f.get("year", ""))
    if not year:
        raise ValueError(f"{entry['key']}: no year")

    peer = (f.get("keywords") or "peer-review").lower()
    kind = "preprint" if "non-peer-review" in peer else "peer-reviewed"

    paper = {
        "title": title,
        "authors": bibtex.unlatex(authors),
        "venue": venue,
        "year": year,
        "type": kind,
    }
    if f.get("badge"):
        paper["badge"] = bibtex.unlatex(f["badge"])
    if f.get("award"):
        paper["award"] = bibtex.unlatex(f["award"])
    if (f.get("selected") or "").lower() in ("true", "yes", "1"):
        paper["selected"] = True

    links = []
    for field, label in LINK_FIELDS:
        if not f.get(field):
            continue
        # once a paper is published, link the published version, not the
        # preprint - the arxiv id stays in the bib either way. The exception is
        # a paper that is accepted but has no pdf or doi yet: an entry with no
        # links at all helps nobody.
        if field == "arxiv" and kind == "peer-reviewed" and (f.get("pdf") or f.get("doi")):
            continue
        links.append((label, link_url(field, f[field].strip())))
    paper["links"] = links
    paper["key"] = entry["key"]
    paper["month"] = entry_month(f)
    return paper


def is_draft(entry):
    return (entry["fields"].get("draft") or "").strip().lower() in ("true", "yes", "1")


def render(papers):
    out = [HEADER, "papers:\n"]
    for p in papers:
        out.append(f"  - title: {yaml_value(p['title'])}\n")
        out.append(f"    authors: {yaml_value(p['authors'])}\n")
        out.append(f"    venue: {yaml_value(p['venue'])}\n")
        out.append(f"    year: {p['year']}\n")
        out.append(f"    type: {p['type']}\n")
        for extra in ("badge", "award"):
            if p.get(extra):
                out.append(f"    {extra}: {yaml_value(p[extra])}\n")
        if p.get("selected"):
            out.append("    selected: true\n")
        out.append(f"    key: {yaml_value(p['key'])}\n")
        if p["links"]:
            out.append("    links:\n")
            for label, url in p["links"]:
                out.append(f"      - label: {yaml_value(label)}\n")
                out.append(f"        url: {yaml_value(url)}\n")
        out.append("\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the YAML does not match the bib (for CI or a pre-commit hook)")
    args = ap.parse_args()

    with open(BIB, encoding="utf-8") as fh:
        entries = bibtex.parse(fh.read())
    if not entries:
        sys.exit(f"No entries found in {BIB}")

    drafts = [e for e in entries if is_draft(e)]
    entries = [e for e in entries if not is_draft(e)]

    papers, seen = [], {}
    for entry in entries:
        try:
            paper = entry_to_paper(entry)
        except ValueError as err:
            sys.exit(f"Bad entry - {err}")
        if entry["key"] in seen:
            sys.exit(f"Duplicate key: {entry['key']}")
        seen[entry["key"]] = True
        papers.append(paper)

    # newest first by year then month; ties keep the bib's own order, so
    # reordering the file still shows through
    papers.sort(key=lambda p: (-int(p["year"]), -p["month"]))

    text = render(papers)

    if args.check:
        current = open(YML, encoding="utf-8").read() if os.path.exists(YML) else ""
        if current != text:
            sys.exit(f"{os.path.relpath(YML, REPO)} is out of date - "
                     f"run: python3 scripts/build_publications.py")
        print(f"up to date ({len(papers)} papers)")
        return

    with open(YML, "w", encoding="utf-8") as fh:
        fh.write(text)

    preprints = sum(1 for p in papers if p["type"] == "preprint")
    print(f"{os.path.relpath(YML, REPO)}: {len(papers)} papers "
          f"({len(papers) - preprints} peer-reviewed, {preprints} preprint), "
          f"{sum(len(p['links']) for p in papers)} links")
    if drafts:
        print(f"\n{len(drafts)} draft entr{'y' if len(drafts) == 1 else 'ies'} "
              f"held back from the site - check them, then delete their "
              f"`draft = {{true}}` line:")
        for entry in drafts:
            print(f"  {entry['key']:28s} {entry['fields'].get('title', '')[:60]}")


if __name__ == "__main__":
    main()
