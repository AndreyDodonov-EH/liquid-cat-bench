#!/usr/bin/env bash
# Native-agent lane: run a model in its own CLI (codex | cursor) with write access to an
# empty folder, so it can create, run and fix the page itself.
#
#   ./native.sh codex  gpt-6-astra
#   ./native.sh cursor claude-opus-5-thinking-high
#   ./native.sh cursor grok-4.7-high -i   # interactive shell in the sandbox: drive the CLI yourself
#
# The CLI runs in a private mount namespace where projects, /tmp, transcripts, CLI chat
# histories and credentials are hidden behind empty tmpfs mounts; the only workspace it
# sees is /tmp/work (backed by native/<cli>/<model>/work). Logs land next to it.
set -euo pipefail

CLI=$1 MODEL=$2 INTERACTIVE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$HERE/native/$CLI/$MODEL
STAGE=$HOME/.cat-native/$CLI-$MODEL          # outside every hidden path until masked
PROMPT=$(python3 -c "import sys; sys.path.insert(0, '$HERE'); import run; print(run.PROMPT)")

rm -rf "$STAGE" && mkdir -p "$STAGE" "$OUT"
# Cursor gets a per-run copy of ~/.cursor without chats/projects/plans: its HTTP/2 agent
# connection fails ALPN inside a user namespace, so the copy forces HTTP/1, and Cursor
# rewrites its config by rename, which needs a real directory rather than a file mount.
CURSOR_HOME=$STAGE.cursor
rm -rf "$CURSOR_HOME"
rsync -a --exclude chats --exclude projects --exclude plans --exclude ai-tracking "$HOME/.cursor/" "$CURSOR_HOME/"
python3 -c "
import json; f = '$CURSOR_HOME/cli-config.json'; d = json.load(open(f))
d.setdefault('network', {})['useHttp1ForAgent'] = True
json.dump(d, open(f, 'w'))"

HIDE_DIRS=(
  "$HOME/_PROJECTS" "$HOME/roman" "$HOME/cli-proxy" "$HOME/.claude"
  "$HOME/.ssh" "$HOME/.aws" "$HOME/.azure" "$HOME/.gnupg" "$HOME/.docker"
  "$HOME/.vscode-server" "$HOME/.cursor-server" /mnt/c/Users   # Program Files stays: agents use Windows Chrome
  "$HOME/.codex/sessions" "$HOME/.codex/memories" "$HOME/.codex/shell_snapshots" "$HOME/.codex/generated_images"
  "$HOME/.cursor/chats" "$HOME/.cursor/projects" "$HOME/.cursor/plans" "$HOME/.cursor/ai-tracking"
)
HIDE_FILES=(
  "$HOME/.claude.json" "$HOME/.git-credentials" "$HOME/.bash_history"
  "$HOME/.codex/history.jsonl" "$HOME/.codex/session_index.jsonl"
)

case $CLI in
  codex)  RUN=(codex exec -m "$MODEL" -c model_reasoning_effort=high --sandbox workspace-write
               --skip-git-repo-check -C /tmp/work --json -o /tmp/work/.last-message.txt "$PROMPT") ;;
  cursor) RUN=(agent -p "$PROMPT" --model "$MODEL" --trust --force --sandbox enabled
               --output-format json) ;;
  probe)  RUN=(sh -c 'id -u; pwd; ls -A /tmp /tmp/work ~/_PROJECTS ~/.claude ~/.cursor/chats ~/.codex/sessions ~/.ssh ~/.cat-native; wc -c ~/.git-credentials ~/.claude.json ~/.codex/history.jsonl; ls ~/.codex/auth.json ~/.cursor/cli-config.json') ;;
  *) echo "unknown cli: $CLI" >&2; exit 2 ;;
esac
[ "$INTERACTIVE" = -i ] && RUN=(bash -i)

# Outer namespace (uid 0) sets up the mounts; inner one drops back to the real uid.
SETUP='
set -e
mount -t tmpfs none /tmp
mkdir /tmp/work
mount --bind "$STAGE" /tmp/work
mount --bind "$CURSOR_HOME" "$HOME/.cursor"
mount -t tmpfs none "$HOME/.cat-native"
for d in "${HIDE_DIRS[@]}"; do [ -d "$d" ] && mount -t tmpfs none "$d"; done
for f in "${HIDE_FILES[@]}"; do [ -f "$f" ] && mount --bind /dev/null "$f"; done
cd /tmp/work
exec unshare -U --map-user='"$(id -u)"' --map-group='"$(id -g)"' "${RUN[@]}"
'
export STAGE CURSOR_HOME
start=$(date +%s.%N)
set +e
if [ "$INTERACTIVE" = -i ]; then
  printf '\nSandbox: only /tmp/work (empty) and CLI logins are visible. Start the CLI, paste the\nprompt below, and `exit` when it is done; files left in /tmp/work become the result.\n\n%s\n\n' "$PROMPT"
  unshare -rm --propagation private bash -c "$(declare -p HIDE_DIRS HIDE_FILES RUN); $SETUP"
else
  unshare -rm --propagation private bash -c "$(declare -p HIDE_DIRS HIDE_FILES RUN); $SETUP" \
    >"$OUT/stdout.jsonl" 2>"$OUT/stderr.log"
fi
code=$?
set -e
secs=$(python3 -c "print(round($(date +%s.%N) - $start, 1))")

rm -rf "$OUT/work" && cp -r "$STAGE" "$OUT/work" && rm -rf "$STAGE" "$CURSOR_HOME"
echo "$CLI $MODEL: exit $code, ${secs}s, files: $(cd "$OUT/work" && find . -type f ! -name '.last-message.txt' | tr '\n' ' ')"
echo "{\"exit\": $code, \"seconds\": $secs}" > "$OUT/run.json"
