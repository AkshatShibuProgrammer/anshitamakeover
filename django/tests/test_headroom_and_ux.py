import os
import time
import subprocess
import pytest
from playwright.sync_api import sync_playwright

SERVER_URL = "http://127.0.0.1:8002"

@pytest.fixture(scope="session", autouse=True)
def run_server():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'anshita_project.settings'
    cmd = ["python", "manage.py", "runserver", "127.0.0.1:8002", "--noreload"]
    from pathlib import Path
    django_root = str(Path(__file__).resolve().parent.parent)
    proc = subprocess.Popen(
        cmd,
        cwd=django_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(4)
    yield
    proc.terminate()
    proc.wait()

def test_headroom_scroll_behavior():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        # Set session storage to bypass preloader animation immediately
        page = context.new_page()
        page.add_init_script("sessionStorage.setItem('anshita_preloader_seen', 'true');")
        page.goto(f"{SERVER_URL}/", timeout=25000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)

        nav = page.locator("#mnav")
        assert nav.is_visible()

        # Scroll down
        page.evaluate("window.scrollTo(0, 700)")
        page.wait_for_timeout(800)

        # Check classes or style
        nav_class = nav.get_attribute("class") or ""
        assert "headroom" in nav_class or "scrolled" in nav_class

        # Scroll up
        page.evaluate("window.scrollTo(0, 200)")
        page.wait_for_timeout(800)

        nav_class_up = nav.get_attribute("class") or ""
        assert "headroom--pinned" in nav_class_up or "headroom" in nav_class_up

        browser.close()

def test_mobile_viewport_responsiveness():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 390, "height": 844})
        page = context.new_page()
        page.add_init_script("sessionStorage.setItem('anshita_preloader_seen', 'true');")
        page.goto(f"{SERVER_URL}/", timeout=25000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)

        menu_trigger = page.locator("#nav-menu-trigger")
        assert menu_trigger.is_visible()

        menu_trigger.click()
        page.wait_for_timeout(600)
        side_drawer = page.locator("#side-drawer")
        assert "open" in (side_drawer.get_attribute("class") or "")

        page.locator(".side-drawer-close").click()
        page.wait_for_timeout(600)
        assert "open" not in (side_drawer.get_attribute("class") or "")

        browser.close()
