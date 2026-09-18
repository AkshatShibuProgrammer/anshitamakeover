from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={'width': 390, 'height': 844})
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('anshita_preloader_seen', 'true');")
    page.goto('http://127.0.0.1:8002/')
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    print("Nav visible:", page.locator("#mnav").is_visible())
    trigger = page.locator("#nav-menu-trigger")
    print("Trigger visible:", trigger.is_visible())
    print("Preloader skipped class on html:", "preloader-skipped" in (page.locator("html").get_attribute("class") or ""))
    print("Preloader display:", page.locator("#preloader").evaluate("el => window.getComputedStyle(el).display"))
    
    trigger.click()
    page.wait_for_timeout(500)
    drawer = page.locator("#side-drawer")
    print("Drawer class after click:", drawer.get_attribute("class"))
    b.close()
