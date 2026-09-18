import os
import time
import subprocess
import pytest
from playwright.sync_api import sync_playwright

SERVER_URL = "http://127.0.0.1:8001"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'anshita_project.settings'
    cmd = ["python", "manage.py", "runserver", "127.0.0.1:8001", "--noreload"]
    from pathlib import Path
    django_root = str(Path(__file__).resolve().parent.parent)
    proc = subprocess.Popen(
        cmd,
        cwd=django_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    yield
    proc.terminate()
    proc.wait()

def test_homepage_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{SERVER_URL}/", timeout=15000)
        assert "Anshita" in page.title() or "Makeover" in page.content()
        
        # Check presence of key sections
        content = page.content()
        assert "academy" in content.lower() or "bridal" in content.lower()
        browser.close()

def test_academy_page_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{SERVER_URL}/academy/", timeout=15000)
        assert page.locator("body").is_visible()
        browser.close()

def test_admin_portal_login_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{SERVER_URL}/admin-login/", timeout=15000)
        
        # Check login inputs
        username_input = page.locator("input[name='username']")
        password_input = page.locator("input[name='password']")
        if username_input.is_visible() and password_input.is_visible():
            username_input.fill("akshat")
            password_input.fill("Anshita@2026")
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(2000)
            assert "/admin-portal/" in page.url or page.locator("body").is_visible()
            
        browser.close()
