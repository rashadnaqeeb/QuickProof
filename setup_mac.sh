#!/bin/bash
# QuickProof macOS setup. Run on the Mac from the QuickProof folder:
#   bash setup_mac.sh
# Safe to run again; every step skips what is already done.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$REPO/quickproof_mac.py"
VENV="$HOME/.local/share/quickproof/venv"
KEY_FILE="$HOME/.config/quickproof/api_key"
KARABINER="$HOME/.config/karabiner/karabiner.json"
PY="${PYTHON:-$(command -v python3)}"

echo "Step 1: Python environment"
if [ ! -x "$VENV/bin/python3" ]; then
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/python3" -m pip install --quiet --upgrade pip pyobjc-framework-ApplicationServices
"$VENV/bin/python3" -c "import ApplicationServices, Quartz, AppKit"
echo "  ready at $VENV"

echo "Step 2: API key"
if [ -s "$KEY_FILE" ]; then
  echo "  already saved in $KEY_FILE"
else
  mkdir -p "$(dirname "$KEY_FILE")"
  if [ -n "${OPENROUTER_API_KEY:-}" ]; then
    printf '%s\n' "$OPENROUTER_API_KEY" > "$KEY_FILE"
    echo "  saved from the OPENROUTER_API_KEY environment variable"
  else
    read -r -s -p "  Paste your OpenRouter API key and press Return: " key
    echo
    printf '%s\n' "$key" > "$KEY_FILE"
    echo "  saved to $KEY_FILE"
  fi
  chmod 600 "$KEY_FILE"
fi

echo "Step 3: Karabiner-Elements rule (fn + /)"
if [ ! -f "$KARABINER" ]; then
  echo "  Karabiner-Elements config not found at $KARABINER. Install Karabiner-Elements, open it once, then rerun." >&2
  exit 1
fi
"$VENV/bin/python3" - "$KARABINER" "$VENV/bin/python3" "$SCRIPT" <<'PYEOF'
import json, shutil, sys, time
path, python, script = sys.argv[1:4]
rule = {
    "description": "QuickProof: fn + / proofreads the focused text field",
    "manipulators": [{
        "type": "basic",
        "from": {"key_code": "slash", "modifiers": {"mandatory": ["fn"], "optional": ["caps_lock"]}},
        # nohup + & so Karabiner returns at once; a second press would otherwise kill a run in progress.
        "to": [{"shell_command": f"nohup '{python}' '{script}' >/dev/null 2>&1 &"}],
    }],
}
with open(path) as f:
    config = json.load(f)
profiles = config.get("profiles", [])
profile = next((p for p in profiles if p.get("selected")), profiles[0] if profiles else None)
if profile is None:
    sys.exit("  no Karabiner profile found")
rules = profile.setdefault("complex_modifications", {}).setdefault("rules", [])
before = len(rules)
rules[:] = [r for r in rules if not str(r.get("description", "")).startswith("QuickProof")]
rules.insert(0, rule)
backup = f"{path}.quickproof-backup-{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(path, backup)
with open(path, "w") as f:
    json.dump(config, f, indent=4)
    f.write("\n")
print(f"  {'replaced' if before != len(rules) - 1 else 'added'} rule in profile '{profile.get('name')}' (backup: {backup})")
PYEOF

echo "Step 4: API test"
"$VENV/bin/python3" "$SCRIPT" --test "helo  wrold, this is a test of quickproof on my mac."

cat <<EOF

Done. One permission still needs you:

1. Accessibility. Click into any text field and press fn + /. macOS will show a
   permission dialog naming the process that launched QuickProof (expected to be
   karabiner_console_user_server). Open System Settings, Privacy and Security,
   Accessibility, and turn it on. Then press fn + / again.

Log file: ~/Library/Logs/QuickProof.log
EOF
