import urllib.request
import re
import os

url = 'https://www.instagram.com/p/DNAFlVSoybm/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'https://[^\"\'\s]+?(?:cdninstagram|fbcdn)[^\"\'\s]+', html)
except Exception as e:
    print("Error fetching page:", e)
    matches = []

out_dir = 'core/static/core/images/curated'
os.makedirs(out_dir, exist_ok=True)

downloaded = 0
for idx, m in enumerate(set(matches)):
    clean = m.replace('\\u0026', '&').replace('\\', '')
    if 'jpg' in clean and ('scontent' in clean or 'cdninstagram' in clean):
        save_path = os.path.join(out_dir, f'royal_bride_raw_{downloaded}.jpg')
        try:
            req2 = urllib.request.Request(clean, headers=headers)
            with urllib.request.urlopen(req2) as img_resp, open(save_path, 'wb') as out_f:
                out_f.write(img_resp.read())
            sz = os.path.getsize(save_path)
            if sz > 20000: # actual image
                print(f"Downloaded [{downloaded}] {save_path}: size={sz} bytes")
                downloaded += 1
                if downloaded >= 8:
                    break
            else:
                os.remove(save_path)
        except Exception as err:
            pass
