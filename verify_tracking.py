import asyncio
from playwright.async_api import async_playwright
from PIL import Image

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8000/', wait_until='networkidle')
        await page.wait_for_timeout(800)
        
        # Check if curtain is visible and click Enter Studio
        enter_btn = await page.query_selector('.curtain-enter-btn, button:has-text("ENTER STUDIO")')
        if enter_btn:
            try:
                await enter_btn.click()
                await page.wait_for_timeout(1000)
            except Exception as e:
                print('Curtain click note:', e)
        
        # Test 1: mouse at top-right (1200, 100)
        await page.mouse.move(1200, 100)
        await page.wait_for_timeout(600)
        await page.screenshot(path='view_topright.png')
        
        # Test 2: mouse at top-left (100, 100)
        await page.mouse.move(100, 100)
        await page.wait_for_timeout(600)
        await page.screenshot(path='view_topleft.png')
        
        # Test 3: mouse near toggle (70, 720)
        await page.mouse.move(70, 720)
        await page.wait_for_timeout(600)
        await page.screenshot(path='view_near.png')
        
        for name in ['view_topright', 'view_topleft', 'view_near']:
            img = Image.open(f'{name}.png')
            crop = img.crop((15, 690, 95, 785))
            crop.save(f'{name}_toggle.png')
            print(f'Saved {name}_toggle.png')
            
        await browser.close()

asyncio.run(run())
