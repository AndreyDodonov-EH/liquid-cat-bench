# Liquid Cat Bench

https://andreydodonov-eh.github.io/liquid-cat-bench/

Prompt, verbatim:

```
Can you make me an animation of a cartoonish cat being "liquid"? I.e. going into a narrow
    tube like liquid and coming out
          ; not with current renderer; just an svg or something similar Format should be
    progably html so that you can use js etc. to deliver best results
```

- One attempt per model, reasoning effort high, no output cap.
- Via CLIProxyAPI (`/v1/chat/completions`, no tools); Grok, Muse Spark, Kimi, GLM via Cursor `agent --mode ask`.
- Claude requests carry the proxy's Claude Code system prompt; Cursor adds its own agent prompt (Cursor prices count output only).
- Price = list price × tokens, reasoning as output; rates in `prices.json` (2026-09-30).
- Pages are unmodified model output.

```
python3 run.py [model ...]   # needs CLIProxyAPI on :8317, Cursor agent CLI
python3 run.py --viewer      # rebuild index.html
```
