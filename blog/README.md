# How to Write a Blog Post

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

## Example Post

```markdown
---
layout: posts
title: "Understanding Jargon in Medical Texts"
date: 2026-04-01
author: Yijun Liu
---

In this post, we share findings from our recent study on how
readers interact with specialized terminology in medical papers.

## Background

Medical literature is notoriously difficult for non-experts...

## Our Approach

We designed an interactive tool that...

![System overview](/resources/blog/system-overview.png)

## Results

| Condition   | Comprehension | Time (min) |
|-------------|---------------|------------|
| Baseline    | 45%           | 12.3       |
| Our Tool    | 72%           | 8.1        |

## Conclusion

Our findings suggest that...
```

## File Naming Rules

- Use lowercase letters, numbers, and hyphens only
- The date prefix is **required** (`YYYY-MM-DD-`)
- The slug after the date becomes the URL path
  - `2026-04-01-my-post.md` becomes `/blog/2026/04/01/my-post.html`

