import asyncio
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        # 1. Homepage Verification
        print("Checking Homepage...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Test 3D Concierge WebGL Canvas
        concierge_canvas = await page.query_selector("#char3dWebGLCanvas")
        print("Concierge 3D WebGL Canvas found:", concierge_canvas is not None)
        
        # Simulate Mouse Move over page to test 3D Character reactivity
        await page.mouse.move(200, 300)
        await page.wait_for_timeout(500)
        await page.mouse.move(1200, 700)
        await page.wait_for_timeout(800)
        await page.screenshot(path="verify_home_3d_character.png")
        print("Saved verify_home_3d_character.png")

        # Test Language Switcher to Hindi
        print("Testing Language switch to Hindi...")
        await page.click(".lang-pill-btn:has-text('हिन्दी')")
        await page.wait_for_timeout(1000)
        menu_text = await page.inner_text("#nav-menu-trigger .am-nav__menu-label")
        print("Hindi Menu label:", menu_text)
        await page.screenshot(path="verify_home_hindi.png")
        print("Saved verify_home_hindi.png")

        # Switch back to English
        await page.click(".lang-pill-btn:has-text('EN')")
        await page.wait_for_timeout(1000)

        # Scroll to Curated Lookbook Showcase on Home
        await page.evaluate("document.querySelector('#home-gallery-showcase')?.scrollIntoView({ behavior: 'smooth' })")
        await page.wait_for_timeout(1200)
        await page.screenshot(path="verify_home_showcase.png")
        print("Saved verify_home_showcase.png")

        # Scroll to Sinha Crest in Home Footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="verify_home_sinha_crest.png")
        print("Saved verify_home_sinha_crest.png")

        # 2. Gallery Page Verification
        print("\nChecking Gallery Page...")
        await page.goto("http://127.0.0.1:8000/gallery/", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        
        # Vertical column albums
        albums_count = await page.locator(".cinema-album-item").count()
        print(f"Total Albums in Vertical Sidebar: {albums_count}")
        
        # Horizontal line items for active album
        filmstrip_count = await page.locator(".filmstrip-card").count()
        print(f"Total Photos/Videos in Horizontal Filmstrip for Kuhu: {filmstrip_count}")
        await page.screenshot(path="verify_gallery_stage.png")
        print("Saved verify_gallery_stage.png")

        # Switch to an album with an Instagram Reel (e.g. Royal Crimson or Maroon Velvet)
        print("Switching to Royal Crimson...")
        await page.click("text=Royal Crimson — Traditional Rajasthani")
        await page.wait_for_timeout(1000)
        crimson_items = await page.locator(".filmstrip-card").count()
        print(f"Total Photos/Videos in Horizontal Filmstrip for Royal Crimson: {crimson_items}")

        # Click the Reel card in Royal Crimson
        reel_card = page.locator(".filmstrip-card:has-text('Reel')").first
        if await reel_card.count() > 0:
            print("Clicking Instagram Reel card in filmstrip...")
            await reel_card.click()
            await page.wait_for_timeout(1500)
            
        await page.screenshot(path="verify_gallery_reel.png")
        print("Saved verify_gallery_reel.png")

        # Scroll down to Sinha Family Group Crest in Gallery Footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(800)
        await page.screenshot(path="verify_gallery_sinha_crest.png")
        print("Saved verify_gallery_sinha_crest.png")

        await browser.close()
        print("\nAll Playwright verification tests finished successfully!")

asyncio.run(run())
