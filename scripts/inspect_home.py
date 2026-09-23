with open(r'f:\Code by Akshat\Anshita\anshitamakeover aiarena\workspace-01a06312-9f47-7052-a276-d661b1051b1c\django\core\templates\core\home.html', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'id="packages"' in line or 'packages_bridal' in line or 'packages_other' in line:
            print(f"Line {i}: {line.strip()[:100]}")
