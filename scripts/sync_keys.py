r"""
Universal AI Key Synchronizer & Manager
Workspace: F:\Code by Akshat\Anshita\anshitamakeover aiarena\workspace-01a06312-9f47-7052-a276-d661b1051b1c

Features:
1. Master Secret Store: F:\Code by Akshat\.secrets.env
2. Sets Windows User Environment Variables (system-wide for all future processes).
3. Automatically propagates updated keys to all projects:
   - .env files (preserves comments and existing vars)
   - gemini_api_key.txt / openai_api_key.txt files
4. Live verification test against Google Gemini and OpenAI APIs.
5. Interactive Wizard and CLI modes.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Fix stdout encoding for Windows console (UTF-8)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = Path(r"F:\Code by Akshat")
MASTER_SECRETS = ROOT_DIR / ".secrets.env"

KNOWN_TARGET_DIRS = [
    WORKSPACE_DIR / "django",
    WORKSPACE_DIR / "anshita_project",
    ROOT_DIR / "learning tools" / "AIDocumentMergerCreator",
    ROOT_DIR / "learning tools" / "combined pdf",
    ROOT_DIR / "testgemini",
    ROOT_DIR / "testgemini" / "studyforge",
    ROOT_DIR / "testOpenAI",
    ROOT_DIR / "growwAgent",
    ROOT_DIR / "learnEarn",
    ROOT_DIR / "trading",
]


def load_master_secrets():
    """Load keys from master .secrets.env or fallback to environment / local project."""
    secrets = {}
    if MASTER_SECRETS.exists():
        for line in MASTER_SECRETS.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                secrets[k.strip()] = v.strip().strip('"\'')

    # Fallback to current workspace files
    if 'GEMINI_API_KEY' not in secrets:
        candidate = WORKSPACE_DIR / "django" / "gemini_api_key.txt"
        if not candidate.exists():
            candidate = WORKSPACE_DIR / "anshita_project" / "gemini_api_key.txt"
        if candidate.exists():
            val = candidate.read_text(encoding='utf-8', errors='ignore').strip()
            if val and val != "YOUR_GEMINI_API_KEY_HERE":
                secrets['GEMINI_API_KEY'] = val

    if 'OPENAI_API_KEY' not in secrets:
        candidate = WORKSPACE_DIR / "django" / "openai_api_key.txt"
        if not candidate.exists():
            candidate = WORKSPACE_DIR / "anshita_project" / "openai_api_key.txt"
        if candidate.exists():
            val = candidate.read_text(encoding='utf-8', errors='ignore').strip()
            if val and val != "YOUR_OPENAI_API_KEY_HERE":
                secrets['OPENAI_API_KEY'] = val

    if 'GEMINI_API_KEY' not in secrets and os.environ.get('GEMINI_API_KEY'):
        secrets['GEMINI_API_KEY'] = os.environ['GEMINI_API_KEY'].strip()
    if 'OPENAI_API_KEY' not in secrets and os.environ.get('OPENAI_API_KEY'):
        secrets['OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY'].strip()
    return secrets


def save_master_secrets(secrets):
    """Save keys to master .secrets.env."""
    lines = [
        "# Master AI Secrets Store — F:\\Code by Akshat\\.secrets.env",
        "# Generated & Managed by sync_keys.py",
        "",
    ]
    for k, v in secrets.items():
        if v:
            lines.append(f"{k}={v}")
    try:
        MASTER_SECRETS.write_text("\n".join(lines) + "\n", encoding='utf-8')
        print(f"  [✓] Saved master secrets: {MASTER_SECRETS}")
    except Exception as e:
        print(f"  [!] Note: Could not write to {MASTER_SECRETS} ({e})")


def set_windows_user_env(var_name, var_value):
    """Set persistent Windows User Environment Variable using PowerShell."""
    if not var_value:
        return
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            f"[System.Environment]::SetEnvironmentVariable('{var_name}', '{var_value}', 'User')"
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  [✓] Set Windows User Environment Variable: {var_name}")
    except Exception as e:
        print(f"  [!] Note: Could not set Windows User Environment Variable ({e})")


def update_env_file(filepath: Path, updates: dict):
    """Update keys in an existing or new .env file while preserving other vars and comments."""
    existing_lines = []
    if filepath.exists():
        existing_lines = filepath.read_text(encoding='utf-8', errors='ignore').splitlines()

    updated_keys = set()
    new_lines = []
    for line in existing_lines:
        line_clean = line.strip()
        if line_clean and not line_clean.startswith('#') and '=' in line_clean:
            k = line_clean.split('=', 1)[0].strip()
            if k in updates and updates[k]:
                new_lines.append(f"{k}={updates[k]}")
                updated_keys.add(k)
                continue
        new_lines.append(line)

    # Append any keys that weren't in the file yet
    for k, v in updates.items():
        if v and k not in updated_keys:
            new_lines.append(f"{k}={v}")

    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("\n".join(new_lines) + "\n", encoding='utf-8')
        print(f"  [✓] Updated: {filepath}")
    except Exception as e:
        print(f"  [!] Failed to update {filepath}: {e}")


def update_txt_file(filepath: Path, value: str):
    """Update a plain text key file."""
    if not value:
        return
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(value.strip() + "\n", encoding='utf-8')
        print(f"  [✓] Updated: {filepath}")
    except Exception as e:
        print(f"  [!] Failed to update {filepath}: {e}")


def test_gemini_key(key: str, model="gemini-2.5-flash"):
    """Quick live ping to Google Gemini API."""
    import urllib.request
    import json
    if not key:
        return False, "Key is empty"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = json.dumps({"contents": [{"parts": [{"text": "ping"}]}]}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                return True, f"Valid! (HTTP 200 via {model})"
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')[:120]
        return False, f"HTTP {e.code}: {body}"
    except Exception as e:
        return False, str(e)


def test_openai_key(key: str):
    """Quick live ping to OpenAI API."""
    import urllib.request
    if not key:
        return False, "Key is empty"
    url = "https://api.openai.com/v1/models"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                return True, "Valid! (HTTP 200)"
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')[:120]
        return False, f"HTTP {e.code}: {body}"
    except Exception as e:
        return False, str(e)


def sync_all(gemini_key=None, openai_key=None):
    """Synchronize keys across master store, Windows env, and all projects."""
    secrets = load_master_secrets()
    if gemini_key:
        secrets['GEMINI_API_KEY'] = gemini_key.strip()
    if openai_key:
        secrets['OPENAI_API_KEY'] = openai_key.strip()

    g_key = secrets.get('GEMINI_API_KEY', '')
    o_key = secrets.get('OPENAI_API_KEY', '')

    print("\n=======================================================")
    print("      UNIVERSAL AI KEY SYNCHRONIZER (AKSHAT)           ")
    print("=======================================================\n")

    # 1. Master secret file
    print("[1/4] Saving Master Secrets...")
    save_master_secrets(secrets)

    # 2. Windows User Environment Variables
    print("\n[2/4] Setting Windows System User Environment...")
    if g_key:
        set_windows_user_env("GEMINI_API_KEY", g_key)
        set_windows_user_env("GEMINI_MODEL", "gemini-2.5-flash")
    if o_key:
        set_windows_user_env("OPENAI_API_KEY", o_key)

    # 3. Propagate to all projects
    print("\n[3/4] Propagating Keys to Project Files...")
    env_updates = {}
    if g_key:
        env_updates['GEMINI_API_KEY'] = g_key
        env_updates['GEMINI_MODEL'] = 'gemini-2.5-flash'
    if o_key:
        env_updates['OPENAI_API_KEY'] = o_key

    for target_dir in KNOWN_TARGET_DIRS:
        if not target_dir.exists():
            continue

        # If project has or uses .env
        env_file = target_dir / ".env"
        if env_file.exists() or target_dir.name in ["django", "AIDocumentMergerCreator", "combined pdf"]:
            update_env_file(env_file, env_updates)

        # If project uses text files
        if target_dir.name in ["django", "anshita_project"]:
            if g_key:
                update_txt_file(target_dir / "gemini_api_key.txt", g_key)
            if o_key:
                update_txt_file(target_dir / "openai_api_key.txt", o_key)

    # 4. Live Verification Ping
    print("\n[4/4] Verifying Live API Connectivity...")
    if g_key:
        ok, msg = test_gemini_key(g_key)
        status = "✅ ACTIVE & VERIFIED" if ok else "❌ ERROR"
        print(f"  Gemini API: {status} ({msg})")
    else:
        print("  Gemini API: (No key set)")

    if o_key:
        ok, msg = test_openai_key(o_key)
        status = "✅ ACTIVE & VERIFIED" if ok else "❌ ERROR"
        print(f"  OpenAI API: {status} ({msg})")
    else:
        print("  OpenAI API: (No key set)")

    print("\n[✓] All projects synchronized successfully!\n")


def interactive_wizard():
    """Interactive console prompt to enter/update keys."""
    secrets = load_master_secrets()
    cur_g = secrets.get('GEMINI_API_KEY', '')
    cur_o = secrets.get('OPENAI_API_KEY', '')

    print("\n=======================================================")
    print("      UNIVERSAL AI KEY SYNCHRONIZER (AKSHAT)           ")
    print("=======================================================")
    print(f"Current Gemini Key : {cur_g[:8]}...{cur_g[-4:] if len(cur_g) > 12 else ''}" if cur_g else "Current Gemini Key : (None)")
    print(f"Current OpenAI Key : {cur_o[:8]}...{cur_o[-4:] if len(cur_o) > 12 else ''}" if cur_o else "Current OpenAI Key : (None)")
    print("-------------------------------------------------------")

    g_inp = input("Enter new GEMINI_API_KEY [Press Enter to keep current]: ").strip()
    o_inp = input("Enter new OPENAI_API_KEY [Press Enter to keep current]: ").strip()

    gemini_key = g_inp if g_inp else cur_g
    openai_key = o_inp if o_inp else cur_o

    sync_all(gemini_key=gemini_key, openai_key=openai_key)


def main():
    parser = argparse.ArgumentParser(description="Universal AI Key Synchronizer for all projects in F:\\Code by Akshat")
    parser.add_argument("--gemini", type=str, help="New Gemini API Key")
    parser.add_argument("--openai", type=str, help="New OpenAI API Key")
    parser.add_argument("--test", action="store_true", help="Test connectivity of currently stored keys")
    parser.add_argument("--sync", action="store_true", help="Sync currently stored keys without prompting")

    args = parser.parse_args()

    if args.test:
        secrets = load_master_secrets()
        g_key = secrets.get('GEMINI_API_KEY', '')
        o_key = secrets.get('OPENAI_API_KEY', '')
        print("\n--- AI KEY CONNECTIVITY HEALTH CHECK ---")
        if g_key:
            ok, msg = test_gemini_key(g_key)
            print(f"Google Gemini (Key: {g_key[:8]}...): {'✅ VERIFIED' if ok else '❌ FAILED'} -> {msg}")
        else:
            print("Google Gemini: No key configured")

        if o_key:
            ok, msg = test_openai_key(o_key)
            print(f"OpenAI        (Key: {o_key[:8]}...): {'✅ VERIFIED' if ok else '❌ FAILED'} -> {msg}")
        else:
            print("OpenAI: No key configured")
        return

    if args.gemini or args.openai or args.sync:
        sync_all(gemini_key=args.gemini, openai_key=args.openai)
    else:
        interactive_wizard()


if __name__ == "__main__":
    main()
