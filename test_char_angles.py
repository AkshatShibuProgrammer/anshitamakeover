import asyncio
from playwright.async_api import async_playwright

async def test_3d_avatar():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        await page.wait_for_timeout(2000)
        
        toggle = await page.query_selector("#chat-toggle")
        
        # Test 1: Center
        await page.mouse.move(720, 450)
        await page.wait_for_timeout(500)
        await toggle.screenshot(path="test_char_center.png")
        print("Captured test_char_center.png")
        
        # Test 2: Look Far Right
        await page.mouse.move(1400, 300)
        await page.wait_for_timeout(600)
        await toggle.screenshot(path="test_char_right.png")
        print("Captured test_char_right.png")

        # Test 3: Look Far Left
        await page.mouse.move(50, 300)
        await page.wait_for_timeout(600)
        await toggle.screenshot(path="test_char_left.png")
        print("Captured test_char_left.png")
        
        await browser.close()

asyncio.run(test_3d_avatar())
