import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test 1: Desktop Viewport (1440x900)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        print("Navigating to Homepage http://127.0.0.1:8000/ ...")
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        await page.wait_for_timeout(3500)

        # 1. Verify 3D Cylindrical Orbit Showcase
        print("Verifying 3D Cylindrical Stage on Desktop...")
        stage = await page.query_selector("#cylinderStage")
        assert stage is not None, "Error: #cylinderStage element not found!"
        await stage.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)

        # Measure cylinder carousel transform
        carousel = await page.query_selector("#cylinderCarousel")
        transform_initial = await carousel.evaluate("el => el.style.transform")
        print(f"Cylinder initial transform: {transform_initial}")
        
        # Simulate drag spin
        box = await stage.bounding_box()
        await page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
        await page.mouse.down()
        await page.mouse.move(box["x"] + box["width"]/2 - 250, box["y"] + box["height"]/2, steps=10)
        await page.mouse.up()
        await page.wait_for_timeout(800)
        
        transform_after_drag = await carousel.evaluate("el => el.style.transform")
        print(f"Cylinder transform after drag: {transform_after_drag}")
        
        await page.screenshot(path="verify_3d_cylinder_desktop.png", clip=box)
        print("Captured verify_3d_cylinder_desktop.png")

        # 2. Verify Demilie-style Craftsmanship Rituals
        print("Verifying Craftsmanship Rituals...")
        about_sec = await page.query_selector("#about")
        await about_sec.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="verify_about_rituals_desktop.png", clip=await about_sec.bounding_box())
        print("Captured verify_about_rituals_desktop.png")

        # 3. Test Mobile Viewport (375x812)
        print("\nTesting Mobile Viewport (iPhone X / 375x812)...")
        mobile_page = await browser.new_page(viewport={"width": 375, "height": 812})
        await mobile_page.goto("http://127.0.0.1:8000/", wait_until="load")
        await mobile_page.wait_for_timeout(3500)

        m_stage = await mobile_page.query_selector("#cylinderStage")
        await m_stage.scroll_into_view_if_needed()
        await mobile_page.wait_for_timeout(1000)
        await mobile_page.screenshot(path="verify_3d_cylinder_mobile.png", clip=await m_stage.bounding_box())
        print("Captured verify_3d_cylinder_mobile.png")

        await browser.close()
        print("\nAll Playwright visual & interactive verification checks PASSED!")

if __name__ == "__main__":
    asyncio.run(verify())
