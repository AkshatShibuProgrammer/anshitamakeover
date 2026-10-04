import asyncio
from playwright.async_api import async_playwright

async def test_char():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        await page.wait_for_timeout(2000)
        
        # Move mouse near bottom left
        await page.mouse.move(100, 800)
        await page.wait_for_timeout(500)
        
        # Take closeup screenshot of #chat-toggle
        toggle = await page.query_selector("#chat-toggle")
        if toggle:
            await toggle.screenshot(path="toggle_closeup.png")
            print("Captured toggle_closeup.png")
            
        await browser.close()

asyncio.run(test_char())
