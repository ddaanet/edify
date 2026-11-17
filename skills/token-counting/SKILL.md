---
name: token-counting
description: Count the tokens of files with the Anthropic API. Use when a file or prompt size must be measured in tokens, not bytes, with `edify-count-tokens`. Not a model round-trip.
---

# Token counting

`edify-count-tokens` counts input tokens with the `count_tokens` endpoint, which
is the only exact count for Claude 3 and later. Offline BPE tokenizers only
approximate. Never measure tokens by a `claude -p` usage round-trip: it pays for
a generation per file.

For a small artifact of 1 to 5 KiB, report bytes instead. It answers "is this
material enough to care?" as well and needs no key or network.

## Run it

`edify-count-tokens` is on PATH:

```bash
edify-count-tokens --model opus --json FILE...
```

- `--model` takes `haiku`, `sonnet` (the default), `opus` or a full model ID. An
  alias resolves to the newest matching model through the models API.
- `--json` prints `{"model", "files": [{"path", "count"}], "total"}`; without it
  the output is a `Using model: <id>` line, then one `path: N tokens` line per
  file, then `Total: N tokens` when more than one file is given.
- Each count includes a constant overhead of about 7 tokens for the request
  frame. Haiku and opus counts agree.
- The key comes from `ANTHROPIC_API_KEY`, else `[anthropic] api_key` in
  `~/.config/edify/config.toml`; the config file needs Python 3.11 or later, and
  older Python errors and names `ANTHROPIC_API_KEY`. Without a key the command
  exits 1 and names both places.
- `ANTHROPIC_BASE_URL` overrides the endpoint base. Nothing is cached.
