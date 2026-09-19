# How to Write a Blog Post


[Tal's Instruction](https://docs.google.com/document/d/1Aa6In4ik2uLkJBJK6tdBGmlnifhx_wmji9dKCd_K-gE/edit?usp=sharing)

## Quick Start

1. Create a new file in `_posts/` with the naming format:
   ```
   YYYY-MM-DD-your-post-title.md
   ```
   Example: `2026-04-01-my-new-post.md`

2. Add the required front matter at the top of the file:
   ```yaml
   ---
   layout: posts
   title: "Your Post Title Here"
   date: 2026-04-01
   author: Your Name
   ---
   ```

3. Write your content in Markdown below the front matter.

4. Commit and push to `main`. GitHub Pages will build and deploy automatically.

## Front Matter Fields

| Field    | Required | Description                          |
|----------|----------|--------------------------------------|
| `layout` | Yes      | Must be `posts`                      |
| `title`  | Yes      | The title displayed on the blog      |
| `date`   | Yes      | Publication date (`YYYY-MM-DD`)      |
| `author` | No       | Author name (shown under the title)  |

## Writing in Markdown

### Headings

```markdown
## Section Heading
### Subsection Heading
```

### Text Formatting

```markdown
**bold text**
*italic text*
[link text](https://example.com)
```

### Images

Place images in `resources/blog/` and reference them:
```markdown
![Alt text](/resources/blog/my-image.png)
```

### Code Blocks

````markdown
```python
def hello():
    print("Hello, world!")
```
````

### Tables

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### Block Quotes

```markdown
> This is a quote.
```

## File Naming Rules

- Use lowercase letters, numbers, and hyphens only
- The date prefix is **required** (`YYYY-MM-DD-`)
- The slug after the date becomes the URL path
  - `2026-04-01-my-post.md` becomes `/blog/2026/04/01/my-post.html`


---

# Adding or Moving a Lab Member

Everyone on the site comes from one file: [`_data/people.yml`](_data/people.yml).
The homepage shows the `current:` list; [`/people/`](people/index.html) shows
`current:` plus `alumni:`.

**Someone joins** — add an entry to `current:`:

```yaml
  - name: Jane Doe
    role: PhD Student
    url: https://janedoe.example.com/                      # optional
    photo: /resources/people/profile_pics/jane_clear.png   # optional
    pub_name: J. Doe        # optional, if papers list a different name
```

Drop the photo in `resources/people/profile_pics/`. Without a `photo:` they get
a circle with their initials, so a missing headshot never breaks the layout.

**Someone graduates or leaves** — move their entry from `current:` to `alumni:`
and add where they went:

```yaml
  - name: Jane Doe
    role: PhD Student
    years: 2024 - 2026
    now: Research Scientist, Example Lab
    now_url: https://example.com/team/jane  # optional
```

The Alumni section only appears once that list has someone in it. Alumni stay
bolded in author lists on the publications page.

# Adding a Paper

Papers live in [`_data/publications.bib`](_data/publications.bib) — ordinary
BibTeX, so you can paste the entry ACM or arXiv hands you. After editing it, run:

```bash
python3 scripts/build_publications.py
```

That regenerates `_data/publications.yml`, which is what Jekyll actually renders
(GitHub Pages can't read BibTeX at build time, so the YAML is a generated file
that gets committed alongside the bib). Commit both. The HTML itself comes from
[`_includes/publication.html`](_includes/publication.html) — one template, so a
change to how papers look happens in one place rather than per paper.

`python3 scripts/build_publications.py --check` exits non-zero if the YAML is
stale, if you ever want it in CI or a pre-commit hook.

An entry with `draft = {true}` is skipped — it stays in the bib but off the
site. That is how papers found automatically arrive; delete the line to
publish one. Settings (`homepage_count`, `first_year`) live in `_config.yml`.

```bibtex
@inproceedings{doe2027some,
  title     = {Some Paper About Something},
  author    = {Doe, Jane and August, Tal},
  booktitle = {Proceedings of the CHI Conference on Human Factors in Computing Systems},
  venue     = {CHI},
  year      = {2027},
  keywords  = {peer-review},
  pdf       = {Doe2027Some.pdf},
  arxiv     = {2701.01234},
  code      = {https://github.com/LanguageInteraction/some-paper},
  video     = {https://youtu.be/xxxxxxxx},
}
```

Standard BibTeX fields work as usual. These are the ones the site reads:

| Field | What it does |
|-------|--------------|
| `venue` | the short name shown on the page — CHI, ACL, ACM TOCHI. Falls back to `booktitle`/`journal` |
| `month` | `jan`…`dec`, sorts papers within a year. Use the month the venue met, so a conference's papers stay together. Preprints are dated from their arXiv id; `--months` fills the rest in from the catalogue |
| `keywords` | `peer-review` or `non-peer-review`. Non-peer-review gets the pill and goes under the Preprints tab |
| `badge` | replaces the "Preprint" pill, e.g. `Workshop` |
| `award` | adds an award pill, e.g. `Best Paper Honorable Mention` |
| `authorline` | overrides the printed author line — for the 30-author papers where the page shows "et al." |
| `selected` | `true` marks it, for pinning to the homepage later |

Link fields each become a button, in this order: `pdf`, `arxiv`, `doi`, `code`,
`video`, `demo`, `data`, `slides`, `poster`, `talk`, `blog`, `website`. A bare
filename in `pdf` means `resources/paper/pdf/<name>`; a bare id in `arxiv` means
`arxiv.org/abs/<id>`; anything starting with `http` or `/` is used as written.
`blog` is handy for pointing at the lab post about the paper.

The arXiv button is hidden once a paper is peer-reviewed and has a `pdf` or
`doi` to link instead — the page should send people to the published version.
Keep the `arxiv` field anyway; it stays useful for citations, and it is still
shown on a paper that is accepted but has no published link yet.

Don't bold lab members yourself — that happens automatically from
`_data/people.yml`, including alumni.

**What belongs here:** a paper with at least one LiLab member on it (Tal not
required), from `first_year` onwards — that's the top of `publications.yml`.

# Checking for New Publications

Google Scholar has no API and blocks scripts, so there is no way to link your
Scholar profile and have the site update itself. Instead there is a script that
reads [OpenAlex](https://openalex.org) — an open catalogue that covers CHI,
UIST, CSCW, ACL and EMNLP — and finds papers that aren't listed yet:

```bash
python3 scripts/update_publications.py          # just tell me what's missing
python3 scripts/update_publications.py --add    # ...and put it in the bib
```

The report says which lab member is on each paper, flags entries whose
published title has drifted from the arXiv one you listed, and points out
preprints that now have a real venue.

With `--add`, new papers are written straight into `_data/publications.bib`
marked `draft = {true}` and the YAML is rebuilt. Drafts stay off the site, so
adding is safe — nothing appears until you have looked at it. For each one:

1. Shorten `venue` if the catalogue name is long.
2. Workshop papers arrive as `keywords = {peer-review}` — the catalogue can't
   tell a workshop from a conference. Switch to `non-peer-review` and add
   `badge = {Workshop}` if it belongs with the preprints.
3. Put the paper in `resources/paper/pdf/` and add `pdf = {…}`, plus any
   `code` / `video` / `demo` / `data` / `slides` / `blog` links.
4. Delete the `draft = {true}` and `added = {…}` lines.
5. `python3 scripts/build_publications.py`

Every run ends by listing the drafts still waiting, so nothing gets forgotten.
Re-running `--add` never duplicates: it compares against the whole bib, drafts
included.

Needs Python 3 and nothing else. Useful options:

| Command | What it does |
|---------|--------------|
| `--arxiv` | find an arXiv link for every bib entry missing one |
| `--months` | fill in the publication month of every bib entry missing one |
| `--find "Jane Doe"` | look up someone's OpenAlex author ID |
| `--all` | list every paper found, not just the new ones |
| `--since 2024` | ignore anything older |
| `--loose` | turn off the same-name filter (see below) |

Who it searches for lives in [`_data/lab_authors.yml`](_data/lab_authors.yml),
along with the short venue names it maps long catalogue titles onto. Every lab
paper so far has Tal on it, so his ID alone finds nearly everything; add a
student's ID to also catch papers they publish without him. OpenAlex mixes up
people who share a name — one "Yifan Song" record carries neutron-star physics —
so the script keeps a paper only when a lab member on it is listed at Illinois,
or when two lab members are on it together.
