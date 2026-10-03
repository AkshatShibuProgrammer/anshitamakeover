import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # 1. Desktop Test (1280x800)
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8000/', wait_until='networkidle')
        await page.wait_for_timeout(800)
        
        enter_btn = await page.query_selector('.curtain-enter-btn')
        if enter_btn:
            try:
                await enter_btn.click()
                await page.wait_for_timeout(1000)
            except Exception as e:
                print('Enter note:', e)
                
        # Scroll to gallery
        await page.evaluate('jumpToMorphSlide(0)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='evagher_desktop_look0.png')
        
        # Morph to Look 2 (Fuchsia Palace)
        await page.evaluate('jumpToMorphSlide(2)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='evagher_desktop_look2.png')

        # Morph to Look 5 (Bengali Heritage)
        await page.evaluate('jumpToMorphSlide(5)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='evagher_desktop_look5.png')
        
        # Test Reverse Morph: back to Look 1 (Christian Ivory)
        await page.evaluate('jumpToMorphSlide(1)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='evagher_desktop_look1_reverse.png')
        
        await page.close()
        
        # 2. Mobile Viewport Test (390x844)
        mob_page = await browser.new_page(viewport={'width': 390, 'height': 844})
        await mob_page.goto('http://127.0.0.1:8000/', wait_until='networkidle')
        await mob_page.wait_for_timeout(800)
        
        mob_enter = await mob_page.query_selector('.curtain-enter-btn')
        if mob_enter:
            try:
                await mob_enter.click()
                await mob_page.wait_for_timeout(1000)
            except Exception as e:
                print('Mob enter note:', e)
                
        await mob_page.evaluate('jumpToMorphSlide(0)')
        await mob_page.wait_for_timeout(1000)
        await mob_page.screenshot(path='evagher_mobile_look0.png')
        
        # Mobile step next
        await mob_page.evaluate('stepMorphSlide(1)')
        await mob_page.wait_for_timeout(1000)
        await mob_page.screenshot(path='evagher_mobile_look1.png')
        
        await browser.close()
        print('All live Evagher scroll-morph checks completed')

asyncio.run(run())
