import sys

def run():
    with open('django/core/templates/core/home.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    head_part = lines[:778] # includes {% block content %}

    clean_block_content = [
        "<!-- Modular Home Editorial CSS (SPEC-019 TSK-19-06) -->\n",
        "<link rel=\"stylesheet\" href=\"{% static 'core/css/modules/home_editorial.css' %}\">\n\n",
        "<!-- SECTION 1: HERO SHOWCASE COMPONENT (SPEC-019 TSK-19-02) -->\n",
        "{% include 'components/hero_showcase.html' %}\n\n",
        "<!-- Subtle luxury divider -->\n",
        "<div style=\"height: 1px; width: 100%; max-width: 1200px; margin: 40px auto; background: radial-gradient(circle, rgba(212,175,55,0.3) 0%, transparent 70%);\"></div>\n\n"
    ]

    body_part = lines[2727:3352]
    tail_part = lines[3388:]

    new_lines = head_part + clean_block_content + body_part + tail_part

    with open('django/core/templates/core/home.html', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"Done! Old length: {len(lines)} lines -> New length: {len(new_lines)} lines")

if __name__ == '__main__':
    run()
