# Liquid Cat Bench

One prompt, many models: each was asked for an HTML animation of a cartoon cat
flowing through a narrow tube like a liquid. The viewer shows every page with a
model dropdown, an optional side-by-side view, and a sortable table of time,
tokens and API price.

**Live viewer:** https://andreydodonov-eh.github.io/liquid-cat-bench/

## The prompt (verbatim, typos included)

```
Can you make me an animation of a cartoonish cat being "liquid"? I.e. going into a narrow
    tube like liquid and coming out
          ; not with current renderer; just an svg or something similar Format should be
    progably html so that you can use js etc. to deliver best results
```

## Method

- One attempt per model, `reasoning_effort: high`, no output cap (Claude gets its model
  maximum, since the API requires `max_tokens`).
- Most models: a single `/v1/chat/completions` call through a local
  CLIProxyAPI instance, with no system
  prompt and no tools.
- Grok, Muse Spark, Kimi and GLM: Cursor's `agent` CLI in read-only ask mode (no file writes,
  no shell), run from an empty folder so the model has to answer inline.
- The largest ```` ```html ```` block in the reply becomes `pages/<model>.html`. The full reply
  is in `raw/`, and timings and token usage are in `stats/`.
- API price = list price × tokens, with reasoning billed as output. Prices and their sources
  are in `prices.json` (looked up 2026-09-30).

## Caveats

- The proxy adds a Claude Code system prompt to Claude requests; OpenAI and Gemini requests
  get none.
- Cursor adds its own agent prompt of about 22k tokens, so Cursor-routed prices count output
  tokens only.
- The pages run unmodified. A broken page is part of the result (for example, claude-opus-5
  throws `Identifier 'BR' has already been declared`).
- One sample per model, so rankings are noisy.

## Re-running

```
python3 run.py                 # all models in MODELS
python3 run.py gpt-6.1-sol     # specific models
python3 run.py --viewer        # rebuild index.html from stats/ and prices.json
```

This needs CLIProxyAPI on `localhost:8317` (its API key is read from
`~/cli-proxy/config/config.yaml`), and the Cursor `agent` CLI for the Cursor-routed models.
