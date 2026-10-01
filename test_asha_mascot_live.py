import asyncio
from playwright.async_api import async_playwright

async def verify_asha():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Navigating to Homepage http://127.0.0.1:8000/ ...")
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        
        # Wait for royal entrance and WebGL initialization
        print("Waiting for Asha concierge entrance and 3D WebGL render...")
        await page.wait_for_timeout(3500)
        
        # Query #chat-toggle and #ashaMascotCanvas
        toggle = await page.query_selector("#chat-toggle")
        canvas = await page.query_selector("#ashaMascotCanvas")
        
        assert toggle is not None, "Error: #chat-toggle not found!"
        assert canvas is not None, "Error: #ashaMascotCanvas not found!"
        
        print("Found Asha 3D canvas and concierge toggle!")
        
        # Move cursor to top-left to test gaze tracking
        print("Simulating mouse move to top-left (200, 150)...")
        await page.mouse.move(200, 150)
        await page.wait_for_timeout(600)
        
        # Capture close-up of Asha looking top-left
        toggle_box = await toggle.bounding_box()
        if toggle_box:
            expanded_box = {
                "x": max(0, min(1440 - 150, toggle_box["x"] - 25)),
                "y": max(0, min(900 - 150, toggle_box["y"] - 25)),
                "width": min(toggle_box["width"] + 50, 1440),
                "height": min(toggle_box["height"] + 50, 900)
            }
            await page.screenshot(path="verify_asha_gaze_top_left.png", clip=expanded_box)
            print("Captured verify_asha_gaze_top_left.png")
            
            # Move cursor directly over Asha to trigger hover excitement bounce
            print("Hovering cursor over Asha toggle...")
            await page.mouse.move(toggle_box["x"] + toggle_box["width"] / 2, toggle_box["y"] + toggle_box["height"] / 2)
            await page.wait_for_timeout(700)
            await page.screenshot(path="verify_asha_hover_bounce.png", clip=expanded_box)
            print("Captured verify_asha_hover_bounce.png")
        else:
            print("Warning: toggle_box returned None, skipping clip screenshots")

        # Full screen screenshot showing Asha in context with speech bubble
        await page.screenshot(path="verify_asha_full_screen.png")
        print("Captured verify_asha_full_screen.png")
        
        await browser.close()
        print("Asha 3D verification complete!")

if __name__ == "__main__":
    asyncio.run(verify_asha())
