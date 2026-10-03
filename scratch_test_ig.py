from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    
    html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #0b0307; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: sans-serif; }
        .reel-stage { width: 420px; height: 740px; background: #000; border-radius: 20px; overflow: hidden; border: 2px solid #d4af37; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <div class="reel-stage">
        <iframe src="https://www.instagram.com/reel/Dap4JkvKL1E/embed/" allowfullscreen frameborder="0"></iframe>
    </div>
</body>
</html>"""
    page.set_content(html)
    page.wait_for_timeout(3500)
    page.screenshot(path="test_ig_embed_740.png")
    browser.close()
print("Saved test_ig_embed_740.png")
