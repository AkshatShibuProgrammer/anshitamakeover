import asyncio
from playwright.async_api import async_playwright

async def test_motion():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        await page.wait_for_timeout(2000)
        
        toggle = await page.query_selector("#chat-toggle")
        
        # 1. Mouse at top right
        await page.mouse.move(1350, 100)
        await page.wait_for_timeout(700)
        await toggle.screenshot(path="char_look_top_right.png")
        print("Captured char_look_top_right.png")
        
        # 2. Mouse at center
        await page.mouse.move(720, 450)
        await page.wait_for_timeout(700)
        await toggle.screenshot(path="char_look_center.png")
        print("Captured char_look_center.png")

        # 3. Trigger wink
        await page.evaluate("window.triggerCharWink && window.triggerCharWink()")
        await page.wait_for_timeout(200)
        await toggle.screenshot(path="char_wink.png")
        print("Captured char_wink.png")

        await browser.close()

asyncio.run(test_motion())
