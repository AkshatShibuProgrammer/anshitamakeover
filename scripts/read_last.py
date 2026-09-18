import json

log_path = r'C:\Users\Aksha\.gemini\antigravity-ide\brain\bae71adb-aa2a-4003-a463-e3b600c94f71\.system_generated\logs\transcript.jsonl'
with open(log_path, 'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f]

import sys
sys.stdout.reconfigure(encoding='utf-8')

for item in lines:
    idx = item.get('step_index')
    if idx and 3920 <= idx <= 3940:
        source = item.get('source')
        stype = item.get('type')
        content = item.get('content') or ''
        tool_calls = item.get('tool_calls') or []
        print(f"Step {idx}: {source} | {stype}")
        if tool_calls:
            print("Tool calls:", [tc.get('name') for tc in tool_calls])
        if content.strip():
            print(content[:400])
        print("-" * 40)
