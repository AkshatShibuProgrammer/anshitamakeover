import base64
import json
import requests
import time

def test_all():
    path = r'D:\TcsQET\qet-react-ui\keys\ai_credentials.b64'
    with open(path, 'rb') as f:
        raw = f.read()

    data = json.loads(base64.b64decode(raw).decode('utf-8'))
    gemini_keys = data.get('gemini', [])
    gpt_keys = data.get('gpt', [])

    print(f"Loaded from {path}:")
    print(f"Gemini keys: {len(gemini_keys)}")
    print(f"GPT keys: {len(gpt_keys)}\n")

    results = []

    print("=" * 65)
    print("  TESTING GEMINI KEYS (Google Generative Language API)")
    print("=" * 65)

    for idx, key in enumerate(gemini_keys):
        masked = key[:10] + "..." + key[-6:]
        print(f"\n[{idx+1}/{len(gemini_keys)}] Key: {masked}")
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        try:
            t0 = time.time()
            r = requests.get(list_url, timeout=12)
            dt = time.time() - t0

            if r.status_code == 200:
                models = r.json().get('models', [])
                gen_count = sum(1 for m in models if 'generateContent' in m.get('supportedGenerationMethods', []))
                print(f"   --> ListModels: HTTP 200 OK ({dt:.2f}s) | Models: {len(models)} (Gen: {gen_count})")
                
                # Test generation with gemini-2.5-flash
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": "Reply with single word: WORKING"}]}]}
                rg = requests.post(gen_url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
                if rg.status_code == 200:
                    cand = rg.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                    print(f"   --> Live Inference: HTTP 200 OK! Response: '{cand}'")
                    results.append({"provider": "Gemini", "index": idx+1, "key": masked, "status": "ACTIVE_WORKING", "detail": f"200 OK, {len(models)} models, inference OK"})
                else:
                    print(f"   --> Live Inference: HTTP {rg.status_code} - {rg.text[:120]}")
                    results.append({"provider": "Gemini", "index": idx+1, "key": masked, "status": "PARTIAL", "detail": f"List 200, Gen {rg.status_code}"})
            else:
                err = r.json().get('error', {})
                msg = err.get('message', r.text[:80])
                status = err.get('status', str(r.status_code))
                print(f"   --> FAILED: HTTP {r.status_code} ({status}): {msg[:90]}")
                results.append({"provider": "Gemini", "index": idx+1, "key": masked, "status": "FAILED", "detail": f"HTTP {r.status_code}: {status}"})
        except Exception as e:
            print(f"   --> Exception: {e}")
            results.append({"provider": "Gemini", "index": idx+1, "key": masked, "status": "ERROR", "detail": str(e)})

    print("\n" + "=" * 65)
    print("  TESTING OPENAI / GPT KEYS")
    print("=" * 65)

    for idx, key in enumerate(gpt_keys):
        masked = key[:10] + "..." + key[-6:]
        print(f"\n[{idx+1}/{len(gpt_keys)}] Key: {masked}")
        headers = {"Authorization": f"Bearer {key}"}
        try:
            r = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=12)
            if r.status_code == 200:
                models = [m['id'] for m in r.json().get('data', [])]
                print(f"   --> ListModels: HTTP 200 OK | Models: {len(models)}")
                results.append({"provider": "OpenAI", "index": idx+1, "key": masked, "status": "ACTIVE_WORKING", "detail": f"200 OK, {len(models)} models"})
            else:
                err_msg = r.json().get('error', {}).get('message', r.text[:80])
                print(f"   --> FAILED: HTTP {r.status_code} - {err_msg}")
                results.append({"provider": "OpenAI", "index": idx+1, "key": masked, "status": "FAILED", "detail": f"HTTP {r.status_code}: {err_msg[:60]}"})
        except Exception as e:
            print(f"   --> Exception: {e}")
            results.append({"provider": "OpenAI", "index": idx+1, "key": masked, "status": "ERROR", "detail": str(e)})

    print("\n" + "=" * 65)
    print("  FINAL SUMMARY MATRIX")
    print("=" * 65)
    for res in results:
        print(f"[{res['status']:<15}] {res['provider']:<7} #{res['index']} | {res['key']} | {res['detail']}")

if __name__ == '__main__':
    test_all()
