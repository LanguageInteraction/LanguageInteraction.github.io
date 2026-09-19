"""A small BibTeX reader and writer. Standard library only.

Handles the subset a lab bibliography needs: @type{key, field = {value}}
entries with nested braces, quoted values, % comments, and the common LaTeX
accent escapes. Not a general LaTeX engine - if you write something exotic it
will come through as written.
"""

import re

# \'e -> é and friends, enough for author names in an HCI/NLP bibliography
ACCENTS = {
    "'a": "á", "'e": "é", "'i": "í", "'o": "ó", "'u": "ú", "'y": "ý", "'n": "ń",
    "'c": "ć", "'s": "ś", "'z": "ź", "'A": "Á", "'E": "É", "'I": "Í", "'O": "Ó",
    "'U": "Ú", "'C": "Ć",
    '"a': "ä", '"e': "ë", '"i': "ï", '"o': "ö", '"u': "ü", '"y': "ÿ",
    '"A': "Ä", '"E': "Ë", '"I': "Ï", '"O': "Ö", '"U': "Ü",
    "`a": "à", "`e": "è", "`i": "ì", "`o": "ò", "`u": "ù",
    "`A": "À", "`E": "È", "`O": "Ò",
    "^a": "â", "^e": "ê", "^i": "î", "^o": "ô", "^u": "û",
    "^A": "Â", "^E": "Ê", "^O": "Ô",
    "~a": "ã", "~n": "ñ", "~o": "õ", "~N": "Ñ",
    "ca": "ą", "cc": "ç", "ce": "ę", "cC": "Ç",
    "va": "ǎ", "vc": "č", "ve": "ě", "vs": "š", "vz": "ž",
    "vC": "Č", "vS": "Š", "vZ": "Ž",
    ".a": "ȧ", ".e": "ė", ".z": "ż",
    "=a": "ā", "=e": "ē", "=o": "ō", "=u": "ū",
    "ua": "ă", "ug": "ğ", "uu": "ŭ",
    "Ha": "a̋", "Ho": "ő", "Hu": "ű",
}

SPECIALS = {
    r"\ss": "ß", r"\aa": "å", r"\AA": "Å", r"\ae": "æ", r"\AE": "Æ",
    r"\oe": "œ", r"\OE": "Œ", r"\o": "ø", r"\O": "Ø", r"\l": "ł", r"\L": "Ł",
    r"\&": "&", r"\%": "%", r"\$": "$", r"\#": "#", r"\_": "_",
    r"\textendash": "–", r"\textemdash": "—", r"---": "—", r"--": "–",
}


def unlatex(text):
    """Turn the LaTeX escapes a bibliography actually contains into characters."""
    # \'{e} and \'e and {\'e}
    def accent(match):
        return ACCENTS.get(match.group(1) + match.group(2), match.group(0))

    text = re.sub(r"\\([`'^\"~=.])\{?([A-Za-z])\}?", accent, text)
    text = re.sub(r"\\([cvuH])\{([A-Za-z])\}", accent, text)
    for src, dst in SPECIALS.items():
        text = text.replace(src, dst)
    # {Protected Capitals} -> Protected Capitals
    text = re.sub(r"[{}]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse(source):
    """Return [{'key':…, 'type':…, 'fields': {…}, 'start':…, 'end':…}] in file
    order. The offsets let a caller splice an entry into the file without
    reformatting the rest of it."""
    entries = []
    i, n = 0, len(source)
    while i < n:
        at = source.find("@", i)
        if at == -1:
            break
        match = re.match(r"@(\w+)\s*\{\s*", source[at:])
        if not match:
            i = at + 1
            continue
        kind = match.group(1).lower()
        i = at + match.end()
        if kind in ("comment", "string", "preamble"):
            i = _skip_block(source, at)
            continue
        end_key = source.find(",", i)
        brace_end = _skip_block(source, at)
        if end_key == -1 or end_key > brace_end:
            i = brace_end
            continue
        key = source[i:end_key].strip()
        entries.append({"key": key, "type": kind, "start": at, "end": brace_end,
                        "fields": _parse_fields(source[end_key + 1:brace_end - 1])})
        i = brace_end
    return entries


def _skip_block(source, at):
    """Index just past the closing brace of the entry that starts at `at`."""
    depth, i = 0, source.find("{", at)
    if i == -1:
        return len(source)
    while i < len(source):
        ch = source[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(source)


def _parse_fields(body):
    fields, i, n = {}, 0, len(body)
    while i < n:
        match = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*").match(body, i)
        if not match:
            break
        name = match.group(1).lower()
        i = match.end()
        if i >= n:
            break
        if body[i] == "{":
            depth, start = 0, i
            while i < n:
                if body[i] == "\\":
                    i += 2
                    continue
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            value = body[start + 1:i]
            i += 1
        elif body[i] == '"':
            start = i + 1
            i += 1
            while i < n and body[i] != '"':
                i += 2 if body[i] == "\\" else 1
            value = body[start:i]
            i += 1
        else:
            start = i
            while i < n and body[i] not in ",\n":
                i += 1
            value = body[start:i]
        fields[name] = value.strip()
        comma = body.find(",", i)
        i = comma + 1 if comma != -1 else n
    return fields


def split_authors(field):
    """BibTeX author field -> ['Yijun Liu', 'Tal August', …] in reading order."""
    out = []
    for name in re.split(r"\s+and\s+", unlatex(field)):
        name = name.strip().rstrip(",")
        if not name:
            continue
        if name.lower() == "others":
            out.append("et al.")
        elif "," in name:                      # "Liu, Yijun" -> "Yijun Liu"
            last, _, first = name.partition(",")
            out.append(f"{first.strip()} {last.strip()}".strip())
        else:
            out.append(name)
    return out


FIELD_ORDER = [
    "title", "author", "authorline", "booktitle", "journal", "venue", "year",
    "month", "keywords", "badge", "award", "selected", "draft", "added", "doi", "arxiv",
    "pdf", "code", "video", "demo", "data", "slides", "poster", "talk", "blog",
    "website", "preview", "url", "note",
]


def format_entry(entry):
    """One entry, fields in a stable order so diffs stay readable."""
    fields = entry["fields"]
    names = [f for f in FIELD_ORDER if f in fields]
    names += sorted(f for f in fields if f not in FIELD_ORDER)
    width = max((len(f) for f in names), default=0)
    lines = [f"@{entry['type']}{{{entry['key']},"]
    for name in names:
        lines.append(f"  {name.ljust(width)} = {{{fields[name]}}},")
    lines.append("}")
    return "\n".join(lines)


def format_file(entries, header=""):
    return (header + "\n\n".join(format_entry(e) for e in entries) + "\n")


def insert(source, entry):
    """Splice `entry` into `source` before the first entry with an older year,
    touching nothing else in the file. Returns the new text."""
    year = int(re.sub(r"\D", "", entry["fields"].get("year", "0")) or 0)
    text = format_entry(entry)
    for existing in parse(source):
        other = int(re.sub(r"\D", "", existing["fields"].get("year", "0")) or 0)
        if other < year:
            return source[:existing["start"]] + text + "\n\n" + source[existing["start"]:]
    return source.rstrip("\n") + "\n\n" + text + "\n"
