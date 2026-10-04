import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test 1: Homepage & AI Character & Curated Lookbook
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        print("Navigating to Homepage http://127.0.0.1:8000/ ...")
        await page.goto("http://127.0.0.1:8000/", wait_until="load")
        # Wait 3.8s for preloader and AI entrance to fully complete
        await page.wait_for_timeout(3800)

        # 1. AI character 3D gaze test
        print("Testing 3D AI Concierge movements...")
        toggle = await page.query_selector("#chat-toggle")
        
        # Cursor right
        await page.mouse.move(1350, 400)
        await page.wait_for_timeout(800)
        await toggle.screenshot(path="verify_ai_look_right.png")
        print("Saved verify_ai_look_right.png")

        # Cursor left
        await page.mouse.move(100, 400)
        await page.wait_for_timeout(800)
        await toggle.screenshot(path="verify_ai_look_left.png")
        print("Saved verify_ai_look_left.png")

        # 2. Scroll to Curated Lookbook & Cinema Reels
        print("Scrolling to Curated Lookbook & Cinema Reels on homepage...")
        showcase = await page.query_selector("#gallery-showcase")
        await showcase.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)
        
        # Check initial scroll position of track
        track = await page.query_selector("#homeGalleryTrack")
        initial_scroll = await track.evaluate("el => el.scrollLeft")
        
        # Wait 1.5 seconds to verify auto-glide in action
        await page.wait_for_timeout(1500)
        glided_scroll = await track.evaluate("el => el.scrollLeft")
        print(f"Auto-glide track position: {initial_scroll} -> {glided_scroll} (Moved: {glided_scroll > initial_scroll})")
        
        await page.screenshot(path="verify_home_showcase_animated.png", clip=await showcase.bounding_box())
        print("Saved verify_home_showcase_animated.png")

        # Test 2: Gallery Page Cinema Studio
        print("\nNavigating to 4K Cinema Studio http://127.0.0.1:8000/gallery/ ...")
        await page.goto("http://127.0.0.1:8000/gallery/", wait_until="load")
        await page.wait_for_timeout(2000)

        # 1. Kuhu (Bengali bride) default selection check
        viewport = await page.query_selector("#cinemaViewport")
        dock = await page.query_selector("#cinemaDetailsDock")
        
        # Verify NO text inside viewport
        text_inside_viewport = await viewport.query_selector(".cinema-details-dock, .cinema-hero-typography")
        print(f"Text inside viewport? {text_inside_viewport is not None} (MUST BE FALSE for zero overlap)")

        # Verify details dock is outside and contains correct details
        eyebrow = await dock.query_selector("#cinemaEyebrow")
        title = await dock.query_selector("#cinemaCraftH")
        client = await dock.query_selector("#cinemaBridesH")
        ig_badge = await dock.query_selector("#cinemaIgLinkBadge")
        book_btn = await dock.query_selector("#cinemaBookBtn")

        print("Cinema Details Dock contents:")
        print(f"  Eyebrow: {(await eyebrow.inner_text()).encode('ascii', 'ignore').decode('ascii')}")
        print(f"  Title: {(await title.inner_text()).encode('ascii', 'ignore').decode('ascii')}")
        print(f"  Client: {(await client.inner_text()).encode('ascii', 'ignore').decode('ascii')}")
        print(f"  Instagram Badge Visible: {await ig_badge.is_visible()}")
        print(f"  Instagram URL: {await ig_badge.get_attribute('href')}")
        btn_text = (await book_btn.inner_text()).encode('ascii', 'ignore').decode('ascii')
        print(f"  Booking Button: {btn_text}")

        # Take screenshot of whole cinema stage (viewport + details dock + filmstrip)
        main_stage = await page.query_selector(".cinema-main-stage")
        await main_stage.screenshot(path="verify_gallery_no_overlap_kuhu.png")
        print("Saved verify_gallery_no_overlap_kuhu.png")

        # 2. Click play orb on Kuhu Reel using page.evaluate to trigger Instagram Reel embed smoothly
        play_orb = await page.query_selector("#cinemaPlayTrigger")
        if await play_orb.is_visible():
            print("Clicking 24K gold play orb to trigger Instagram Reel embed...")
            await page.evaluate("document.getElementById('cinemaPlayTrigger').click()")
            await page.wait_for_timeout(2000)
            
            # Check if Instagram iframe is loaded
            ig_wrap = await page.query_selector("#cinemaIgEmbedWrap")
            ig_iframe = await page.query_selector("#cinemaIgIframe")
            iframe_src = await ig_iframe.get_attribute("src")
            print(f"Instagram Reel iframe visible: {await ig_wrap.is_visible()}")
            print(f"Instagram Reel iframe src: {iframe_src}")
            
            await main_stage.screenshot(path="verify_gallery_kuhu_reel_playing.png")
            print("Saved verify_gallery_kuhu_reel_playing.png")

        # 3. Select Imperial Fuchsia & Emerald (Reel album)
        print("\nSelecting Imperial Fuchsia & Emerald album...")
        await page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('.cinema-album-item'));
            const target = items.find(el => el.textContent.includes('Fuchsia') || el.textContent.includes('Emerald'));
            if (target) target.click();
        }""")
        
        await page.wait_for_timeout(1500)
        await main_stage.screenshot(path="verify_gallery_fuchsia_no_overlap.png")
        print("Saved verify_gallery_fuchsia_no_overlap.png")

        await browser.close()
        print("\nAll Playwright verifications completed successfully!")

asyncio.run(verify())
