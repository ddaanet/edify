---
name: markdown
description: Fix structural defects in agent-written markdown files. Use after producing or editing a .md file that has keyword lists with no bullets, triple backticks or fence markers in running text, or backtick spans with edge spaces. Not for prose style.
---

# Markdown fixer

Agent-produced markdown carries a few recurring structural defects that a
formatter leaves alone. `edify-markdown` rewrites them in place.

It fixes:

- Runs of lines opening with the same emoji, `[TAG]` or `NOTE:` prefix, which
  become bullets.
- Triple backticks and fence markers inside running text, which are escaped with
  double backticks.
- Inline code with leading or trailing spaces, which is quoted so the space
  shows: `` `"a "` ``.
- `` ```markdown `` blocks that contain inner fences, which get four-backtick
  outer fences.
- `**Label:**` runs, numbered-list spacing, lettered sub-items and dunder names
  in headings.

Fenced code and YAML front matter are left alone, except `markdown` blocks.

## Run it

`edify-markdown` is on PATH. Pass the file paths on stdin, one per line:

```bash
printf '%s\n' path/one.md path/two.md | edify-markdown
```

It prints the path of each file it rewrote and nothing for a file already clean.
A path that is not a `.md` file or does not exist is reported on stderr, the
other paths are still processed, and the exit status is 1. Re-read a rewritten
file before building on its old text.
