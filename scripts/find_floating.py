import re

for fname in [r'django\core\templates\core\base.html', r'django\core\templates\core\home.html']:
    print(f'=== {fname} ===')
    with open(rf'f:\Code by Akshat\Anshita\anshitamakeover aiarena\workspace-01a06312-9f47-7052-a276-d661b1051b1c\{fname}', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if any(w in line.lower() for w in ['floating', 'cart-btn', 'cart_btn', 'cart-toggle', 'ai-btn', 'ai-trigger', 'ai_btn', 'ai concierge', 'chat-toggle', 'whatsapp-float', 'wa-btn', 'btn-wa', 'openchatbot', 'togglecart']):
                if ('class=' in line or 'id=' in line or '<button' in line or '<a ' in line) and len(line.strip()) < 140:
                    print(f'{i}: {line.strip()}')
