import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r'C:\Users\Aksha\.gemini\antigravity-ide\brain\bae71adb-aa2a-4003-a463-e3b600c94f71\.system_generated\logs\transcript.jsonl'
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        content = item.get('content') or ''
        if 'anshitamakeover21' in content and item.get('type') in ['SUBAGENT_COMPLETED', 'PLANNER_RESPONSE']:
            print(f"Step {item.get('step_index')}: {item.get('type')}")
            print(content[:1000])
            print("="*40)
