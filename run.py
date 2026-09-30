#!/usr/bin/env python3
"""Liquid-cat bench: send one prompt to every model through cli-proxy, keep the HTML.

    python3 run.py [model ...]     # default: MODELS below
    python3 run.py --viewer        # only rebuild index.html

Single-shot /v1/chat/completions, no system prompt, no tools, reasoning_effort
high, no output cap, so every model gets exactly the same input (CURSOR_MODELS go
through Cursor's `agent` CLI in read-only ask mode instead). Writes raw/<model>.md,
pages/<model>.html and stats/<model>.json (one file per model, so concurrent runs
never clobber each other); then rebuilds index.html (the viewer) from every stats
file present.
"""
import json, re, subprocess, sys, tempfile, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = "http://localhost:8317/v1/chat/completions"
# No cap: Claude needs max_tokens (the proxy otherwise injects 32000), so send each
# model's own maximum; OpenAI and Gemini models get none.
MAX_TOKENS = {"claude-haiku-4-5-20251001": 64000}
CLAUDE_MAX_TOKENS = 128000
REASONING_EFFORT = "high"
TIMEOUT_S = 3600
# Token counts and prices stay in stats/ but are left out of the published viewer
# until the subscription-route usage numbers are verified.
PUBLISH_USAGE = False
USAGE_KEYS = {"prompt_tokens", "out_tokens", "total_tokens", "reasoning_tokens", "cost", "price"}

MODELS = [
    "claude-opus-5-5", "claude-fable-5-1", "claude-sonnet-5-5",
    "claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-5", "claude-opus-4-8",
    "gpt-6.1-sol", "gpt-6-sol", "gpt-6-astra", "gpt-6-luna",
    "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.5",
    "gemini-3.8-flash-high",
    "grok-4.7-high", "muse-spark-1.3-high", "kimi-k3-high", "glm-5.2-high",
]
# Not served by cli-proxy; run through Cursor's `agent` CLI under the same id.
CURSOR_MODELS = {"grok-4.7-high", "muse-spark-1.3-high", "kimi-k3-high", "glm-5.2-high"}

# Hand fixes applied to pages/<model>.html after extraction (raw/ stays untouched).
# Re-running a model overwrites its page, so re-apply or drop the entry.
PATCHES = {"claude-opus-5": "patched: second top-level `const BR` renamed (was a SyntaxError)"}

PROMPT = """Can you make me an animation of a cartoonish cat being "liquid"? I.e. going into a narrow
    tube like liquid and coming out
          ; not with current renderer; just an svg or something similar Format should be
    progably html so that you can use js etc. to deliver best results"""


def api_key():
    cfg = (Path.home() / "cli-proxy/config/config.yaml").read_text().splitlines()
    i = next(i for i, l in enumerate(cfg) if l.startswith("api-keys:"))
    return re.search(r'"([^"]+)"', cfg[i + 1]).group(1)


def extract_html(text):
    """Largest ```html fence; else a bare <!doctype>/<html> document; else None."""
    fences = re.findall(r"```(?:html|HTML)[^\n]*\n(.*?)```", text, re.S)
    if fences:
        return max(fences, key=len)
    m = re.search(r"(<!doctype html.*?</html>|<html.*?</html>)", text, re.S | re.I)
    return m.group(1) if m else None


def call_proxy(model, key):
    """-> (reply text, finish reason, usage) via cli-proxy."""
    payload = {"model": model, "reasoning_effort": REASONING_EFFORT,
               "messages": [{"role": "user", "content": PROMPT}]}
    if model.startswith("claude-"):
        payload["max_tokens"] = MAX_TOKENS.get(model, CLAUDE_MAX_TOKENS)
    req = urllib.request.Request(PROXY, json.dumps(payload).encode(),
                                 {"Authorization": f"Bearer {key}",
                                  "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        resp = json.load(r)
    choice, usage = resp["choices"][0], resp.get("usage", {})
    return choice["message"].get("content") or "", choice.get("finish_reason"), {
        "prompt_tokens": usage.get("prompt_tokens"),
        "out_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")}


def call_cursor(model):
    """-> (reply text, finish reason, usage) via Cursor's `agent` CLI.

    Read-only ask mode (no writes, no shell) from an empty scratch dir, so the
    model must answer inline like the proxy models. Effort is part of the model id.
    """
    with tempfile.TemporaryDirectory(prefix="cat-cursor-") as cwd:
        out = subprocess.run(["agent", "-p", PROMPT, "--model", model,
                              "--mode", "ask", "--trust", "--output-format", "json"],
                             cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S)
    resp = json.loads(out.stdout)
    if resp.get("is_error"):
        raise RuntimeError(out.stdout[:2000])
    usage = resp.get("usage", {})
    return resp.get("result") or "", resp.get("subtype"), {
        "prompt_tokens": usage.get("inputTokens"),
        "out_tokens": usage.get("outputTokens")}


def run(model, key):
    t0 = time.time()
    try:
        text, finish, usage = call_cursor(model) if model in CURSOR_MODELS else call_proxy(model, key)
    except Exception as e:  # keep going; the viewer shows the failure
        err = e.read().decode(errors="replace")[:2000] if hasattr(e, "read") else str(e)
        print(f"{model}: FAILED {err[:200]}", flush=True)
        return model, {"ok": False, "error": err, "seconds": round(time.time() - t0, 1)}
    secs = round(time.time() - t0, 1)
    (HERE / "raw").mkdir(exist_ok=True)
    (HERE / "raw" / f"{model}.md").write_text(text)
    html = extract_html(text)
    if html:
        (HERE / "pages").mkdir(exist_ok=True)
        (HERE / "pages" / f"{model}.html").write_text(html)
    stats = {"ok": bool(html), "effort": REASONING_EFFORT, "seconds": secs, "finish": finish,
             **usage, "html_bytes": len(html.encode()) if html else 0}
    if not html:
        stats["error"] = "no HTML document found in the reply"
    print(f"{model}: {secs}s, {stats['out_tokens']} tok, html {stats['html_bytes']} B, "
          f"finish={stats['finish']}", flush=True)
    return model, stats


def api_cost(model, stats, prices):
    """USD at list price: prompt + output tokens (reasoning is billed as output).

    Cursor-routed input is skipped: it is mostly Cursor's own agent prompt, which a
    direct API call would not send.
    """
    pr = prices.get(model) or {}
    if pr.get("out") is None or stats.get("out_tokens") is None:
        return None
    tok_in = 0 if model in CURSOR_MODELS else (stats.get("prompt_tokens") or 0)
    return round((tok_in * (pr.get("in") or 0) + stats["out_tokens"] * pr["out"]) / 1e6, 4)


def build_viewer():
    results = {f.stem: json.loads(f.read_text()) for f in (HERE / "stats").glob("*.json")}
    prices_path = HERE / "prices.json"
    prices = json.loads(prices_path.read_text()) if prices_path.exists() else {}
    tpl = (HERE / "viewer.template.html").read_text()
    order = [m for m in MODELS if m in results] + sorted(set(results) - set(MODELS))
    data = [{"model": m, **results[m], "route": "cursor" if m in CURSOR_MODELS else "proxy",
             "cost": api_cost(m, results[m], prices), "price": prices.get(m),
             "patch": PATCHES.get(m)} for m in order]
    if not PUBLISH_USAGE:
        data = [{k: v for k, v in r.items() if k not in USAGE_KEYS} for r in data]
    (HERE / "index.html").write_text(tpl.replace("/*RESULTS*/[]", json.dumps(data, indent=1)))


def main():
    if sys.argv[1:] != ["--viewer"]:
        models = sys.argv[1:] or MODELS
        key = api_key()
        (HERE / "stats").mkdir(exist_ok=True)
        with ThreadPoolExecutor(len(models)) as ex:
            for fut in as_completed([ex.submit(run, m, key) for m in models]):
                model, stats = fut.result()
                (HERE / "stats" / f"{model}.json").write_text(json.dumps(stats, indent=1))
    build_viewer()
    print(f"viewer: {HERE / 'index.html'}")


if __name__ == "__main__":
    main()
