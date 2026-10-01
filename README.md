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
- Via CLIProxyAPI (`/v1/chat/completions`, no tools); Muse Spark, Kimi, GLM via Cursor `agent --mode ask`.
- Claude requests carry the proxy's Claude Code system prompt; Cursor adds its own agent prompt.
- `(… agent)` entries: the model in its own CLI (`native.sh`: Codex, Cursor; grok-4.7 driven by hand in the same sandbox) with write access to an empty, isolated folder, so it can run and fix its page.
- Pages are unmodified model output, except claude-opus-5: a duplicate `const BR` renamed.

```
python3 run.py [model ...]   # needs CLIProxyAPI on :8317, Cursor agent CLI
./native.sh codex gpt-6-astra  # agent lane
python3 run.py --viewer      # rebuild index.html
```
