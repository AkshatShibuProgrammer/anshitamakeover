r"""
Key Health & Account Attribution Checker
Scans F:\Code by Akshat for all AI & API keys, tests validity, and retrieves associated accounts.
"""

import os
import sys
import json
import glob
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# UTF-8 stdout on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(r"F:\Code by Akshat")


def mask_key(k: str) -> str:
    if len(k) <= 8:
        return "***"
    return k[:6] + "..." + k[-4:]


def check_gemini_key(key: str):
    """Test Gemini key and query models to find account/project details."""
    result = {
        'service': 'Google Gemini',
        'key_masked': mask_key(key),
        'working': False,
        'account_info': {},
        'status_detail': ''
    }
    # 1. Test models list endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KeyAuditor/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = [m.get('name', '').replace('models/', '') for m in data.get('models', [])]
            result['working'] = True
            result['status_detail'] = f"Active & Working! Has access to {len(models)} models."
            result['account_info']['available_models'] = models[:5]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        try:
            err_json = json.loads(err_body)
            msg = err_json.get('error', {}).get('message', err_body[:150])
            status = err_json.get('error', {}).get('status', str(e.code))
            result['status_detail'] = f"Failed (HTTP {e.code} {status}): {msg}"
            if 'details' in err_json.get('error', {}):
                result['account_info']['error_details'] = err_json['error']['details']
        except Exception:
            result['status_detail'] = f"HTTP {e.code}: {err_body[:150]}"
        return result
    except Exception as e:
        result['status_detail'] = f"Network/Connection error: {str(e)}"
        return result

    # 2. Test actual generation on models
    test_models = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-3-flash-preview']
    for tm in test_models:
        gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/{tm}:generateContent?key={key}"
        gen_payload = json.dumps({"contents": [{"parts": [{"text": "hi"}]}]}).encode('utf-8')
        try:
            gen_req = urllib.request.Request(gen_url, data=gen_payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(gen_req, timeout=10) as resp:
                if resp.status == 200:
                    result['account_info']['inference_test'] = f'Success ({tm} responded 200 OK)'
                    break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                result['account_info']['inference_test'] = f'Rate limited / Quota reached ({tm}: HTTP 429)'
            continue
        except Exception:
            continue

    return result


def check_openai_key(key: str):
    """Test OpenAI key and inspect organization / account headers."""
    result = {
        'service': 'OpenAI',
        'key_masked': mask_key(key),
        'working': False,
        'account_info': {},
        'status_detail': ''
    }
    url = "https://api.openai.com/v1/models"
    req = urllib.request.Request(url, headers={'Authorization': f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            headers = dict(resp.headers)
            data = json.loads(resp.read().decode('utf-8'))
            models = [m.get('id') for m in data.get('data', [])]
            result['working'] = True
            result['status_detail'] = f"Active & Working! ({len(models)} models accessible)"
            result['account_info']['org_id'] = headers.get('openai-organization', 'Unknown')
            result['account_info']['project_id'] = headers.get('openai-project', 'Default')
    except urllib.error.HTTPError as e:
        headers = dict(e.headers)
        err_body = e.read().decode('utf-8', errors='ignore')
        try:
            err_json = json.loads(err_body)
            msg = err_json.get('error', {}).get('message', err_body[:150])
            code = err_json.get('error', {}).get('code', str(e.code))
            result['status_detail'] = f"HTTP {e.code} ({code}): {msg}"
        except Exception:
            result['status_detail'] = f"HTTP {e.code}: {err_body[:150]}"
        if 'openai-organization' in headers:
            result['account_info']['org_id'] = headers['openai-organization']
    except Exception as e:
        result['status_detail'] = f"Error: {str(e)}"

    return result


def check_serpapi_key(key: str):
    """Query SerpAPI account endpoint for email, plan, and searches left."""
    result = {
        'service': 'SerpAPI',
        'key_masked': mask_key(key),
        'working': False,
        'account_info': {},
        'status_detail': ''
    }
    url = f"https://serpapi.com/account?api_key={key}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KeyAuditor/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result['working'] = True
            result['status_detail'] = 'Active & Working!'
            result['account_info']['account_email'] = data.get('account_email', 'N/A')
            result['account_info']['plan'] = data.get('plan_name', 'N/A')
            result['account_info']['searches_per_month'] = data.get('searches_per_month', 0)
            result['account_info']['plan_searches_left'] = data.get('plan_searches_left', 0)
            result['account_info']['total_searches_left'] = data.get('total_searches_left', 0)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        result['status_detail'] = f"HTTP {e.code}: {err_body[:120]}"
    except Exception as e:
        result['status_detail'] = f"Error: {str(e)}"
    return result


def check_google_cse(api_key: str, cse_id: str):
    """Test Google Custom Search API key and CSE."""
    result = {
        'service': 'Google Custom Search (CSE)',
        'key_masked': mask_key(api_key),
        'working': False,
        'account_info': {'cse_id': cse_id},
        'status_detail': ''
    }
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q=test"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KeyAuditor/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result['working'] = True
            total = data.get('searchInformation', {}).get('totalResults', 'Unknown')
            result['status_detail'] = f"Active & Working! (Query returned {total} results)"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        try:
            err_json = json.loads(err_body)
            msg = err_json.get('error', {}).get('message', err_body[:120])
            result['status_detail'] = f"HTTP {e.code}: {msg}"
        except Exception:
            result['status_detail'] = f"HTTP {e.code}: {err_body[:120]}"
    except Exception as e:
        result['status_detail'] = f"Error: {str(e)}"
    return result


def check_service_account_file(filepath: Path):
    """Inspect a Google Service Account or OAuth Credentials JSON file."""
    result = {
        'service': 'Google Service Account / OAuth JSON',
        'file': str(filepath),
        'working': False,
        'account_info': {},
        'status_detail': ''
    }
    try:
        data = json.loads(filepath.read_text(encoding='utf-8', errors='ignore'))
        result['working'] = True
        result['account_info']['type'] = data.get('type', data.get('installed', {}).get('client_type', 'oauth'))
        result['account_info']['project_id'] = data.get('project_id', data.get('installed', {}).get('project_id', 'N/A'))
        result['account_info']['client_email'] = data.get('client_email', 'N/A')
        result['account_info']['client_id'] = data.get('client_id', data.get('installed', {}).get('client_id', 'N/A'))
        result['status_detail'] = f"Valid JSON Credentials ({result['account_info']['type']})"
    except Exception as e:
        result['status_detail'] = f"Failed to parse JSON: {e}"
    return result


def main():
    print("================================================================================")
    print("           COMPREHENSIVE AI & API KEY AUDIT ACROSS ALL PROJECTS                 ")
    print("================================================================================\n")

    # Collect all keys
    found_keys = {}  # { (service, value): [locations] }
    cse_pairs = []   # (api_key, cse_id, location)
    credential_files = []

    # 1. Scan .env files
    for env_path in glob.glob(r"F:\Code by Akshat\**\.env*", recursive=True):
        if any(x in env_path for x in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
            continue
        if not os.path.isfile(env_path):
            continue
        current_cse_key = ''
        current_cse_id = ''
        for line in open(env_path, encoding='utf-8', errors='ignore'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k, v = k.strip(), v.strip().strip('"\'')
                if not v or v in ['YOUR_GEMINI_API_KEY_HERE', 'your_key_here']:
                    continue
                if k == 'GEMINI_API_KEY':
                    found_keys.setdefault(('gemini', v), []).append(env_path)
                elif k == 'OPENAI_API_KEY':
                    found_keys.setdefault(('openai', v), []).append(env_path)
                elif k == 'SERPAPI_KEY':
                    found_keys.setdefault(('serpapi', v), []).append(env_path)
                elif k == 'GOOGLE_SEARCH_API_KEY':
                    current_cse_key = v
                elif k == 'GOOGLE_CSE_ID':
                    current_cse_id = v
                elif 'FILE' in k and v.endswith('.json'):
                    p = Path(env_path).parent / v
                    if p.exists():
                        credential_files.append(p)
        if current_cse_key and current_cse_id:
            cse_pairs.append((current_cse_key, current_cse_id, env_path))

    # 2. Scan text key files
    for txt_path in glob.glob(r"F:\Code by Akshat\**\*key*.txt", recursive=True):
        if any(x in txt_path for x in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
            continue
        if not os.path.isfile(txt_path):
            continue
        v = open(txt_path, encoding='utf-8', errors='ignore').read().strip()
        if not v or v == 'YOUR_GEMINI_API_KEY_HERE':
            continue
        if 'gemini' in txt_path.lower():
            found_keys.setdefault(('gemini', v), []).append(txt_path)
        elif 'openai' in txt_path.lower():
            found_keys.setdefault(('openai', v), []).append(txt_path)

    # 3. Check Windows Environment
    if os.environ.get('GEMINI_API_KEY'):
        v = os.environ['GEMINI_API_KEY'].strip()
        found_keys.setdefault(('gemini', v), []).append('Windows User Environment')
    if os.environ.get('OPENAI_API_KEY'):
        v = os.environ['OPENAI_API_KEY'].strip()
        found_keys.setdefault(('openai', v), []).append('Windows User Environment')

    # 4. Scan CFA Encrypted Key Store (ai_credentials.b64)
    import base64
    cfa_b64_paths = [
        r"D:\TcsQET\qet-react-ui\keys\ai_credentials.b64",
        r"D:\TcsQET\keys\ai_credentials.b64"
    ]
    for b64_p in cfa_b64_paths:
        if os.path.exists(b64_p):
            try:
                raw_bytes = open(b64_p, 'rb').read()
                data = json.loads(base64.b64decode(raw_bytes).decode('utf-8'))
                for gk in data.get('gemini', []):
                    if gk and gk.strip():
                        found_keys.setdefault(('gemini', gk.strip()), []).append(f"CFA Encrypted Store: {b64_p}")
                for ok in data.get('gpt', []):
                    if ok and ok.strip():
                        found_keys.setdefault(('openai', ok.strip()), []).append(f"CFA Encrypted Store: {b64_p}")
            except Exception as e:
                print(f"[!] Warning: Failed to read {b64_p}: {e}")

    # 5. Scan D:\TcsQET for additional key files
    for txt_path in glob.glob(r"D:\TcsQET\**\*key*.txt", recursive=True):
        if any(x in txt_path for x in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
            continue
        if not os.path.isfile(txt_path):
            continue
        try:
            v = open(txt_path, encoding='utf-8', errors='ignore').read().strip()
            if not v or v == 'YOUR_GEMINI_API_KEY_HERE':
                continue
            if 'gemini' in txt_path.lower():
                found_keys.setdefault(('gemini', v), []).append(txt_path)
            elif 'openai' in txt_path.lower():
                found_keys.setdefault(('openai', v), []).append(txt_path)
        except Exception:
            pass

    # Also scan for any google service account json files
    for json_file in glob.glob(r"F:\Code by Akshat\**\*credential*.json", recursive=True):
        if any(x in json_file for x in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
            continue
        credential_files.append(Path(json_file))
    for json_file in glob.glob(r"F:\Code by Akshat\**\*service_account*.json", recursive=True):
        if any(x in json_file for x in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
            continue
        credential_files.append(Path(json_file))

    # Remove duplicates
    credential_files = list(set(credential_files))

    # Perform Tests
    print(f"Total Unique Keys & Credentials Identified: {len(found_keys) + len(cse_pairs) + len(credential_files)}\n")

    counter = 1

    # Test Gemini & OpenAI & SerpAPI
    for (service_type, key_val), locs in found_keys.items():
        print(f"[{counter}] Service: {service_type.upper()}")
        print(f"    Key:       {mask_key(key_val)}")
        print(f"    Locations: {len(locs)} files/locations")
        for loc in locs[:3]:
            print(f"      • {loc}")
        if len(locs) > 3:
            print(f"      • ...and {len(locs) - 3} more")

        if service_type == 'gemini':
            res = check_gemini_key(key_val)
        elif service_type == 'openai':
            res = check_openai_key(key_val)
        elif service_type == 'serpapi':
            res = check_serpapi_key(key_val)
        else:
            res = {'working': False, 'status_detail': 'Unknown service', 'account_info': {}}

        icon = "✅ WORKING" if res['working'] else "❌ NOT WORKING"
        print(f"    Status:    {icon} -> {res['status_detail']}")
        if res['account_info']:
            print(f"    Account Info:")
            for ak, av in res['account_info'].items():
                print(f"      - {ak}: {av}")
        print("-" * 80)
        counter += 1

    # Test Google CSE
    for cse_key, cse_id, loc in cse_pairs:
        print(f"[{counter}] Service: GOOGLE CUSTOM SEARCH (CSE)")
        print(f"    API Key:   {mask_key(cse_key)}")
        print(f"    CSE ID:    {cse_id}")
        print(f"    Location:  {loc}")
        res = check_google_cse(cse_key, cse_id)
        icon = "✅ WORKING" if res['working'] else "❌ NOT WORKING"
        print(f"    Status:    {icon} -> {res['status_detail']}")
        print("-" * 80)
        counter += 1

    # Inspect Credential files
    for cred_file in credential_files:
        if not cred_file.exists():
            continue
        print(f"[{counter}] Service: GOOGLE CREDENTIALS JSON FILE")
        print(f"    File:      {cred_file}")
        res = check_service_account_file(cred_file)
        icon = "✅ VALID FILE" if res['working'] else "❌ CORRUPTED / INVALID"
        print(f"    Status:    {icon} -> {res['status_detail']}")
        if res['account_info']:
            print(f"    Account Info:")
            for ak, av in res['account_info'].items():
                print(f"      - {ak}: {av}")
        print("-" * 80)
        counter += 1

    print("\n[Audit Complete]")


if __name__ == "__main__":
    main()
