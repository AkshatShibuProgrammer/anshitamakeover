import asyncio
from playwright.async_api import async_playwright

async def inspect_dom():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        await page.wait_for_timeout(2000)
        
        html = await page.evaluate("document.querySelector('#chat-toggle').outerHTML")
        print("CHAT TOGGLE HTML:\n", html)
        
        # Check computed styles of #char3dStage and #char3dWebGLCanvas
        styles = await page.evaluate("""() => {
            const s = document.querySelector('#char3dStage');
            const c = document.querySelector('#char3dWebGLCanvas');
            return {
                stageRect: s ? s.getBoundingClientRect() : null,
                canvasRect: c ? c.getBoundingClientRect() : null,
                canvasWidth: c ? c.width : null,
                canvasHeight: c ? c.height : null
            };
        }""")
        print("STYLES:\n", styles)
        await browser.close()

asyncio.run(inspect_dom())
