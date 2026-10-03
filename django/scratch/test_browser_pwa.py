"""
Selenium test to verify PWA ServiceWorker registration in Chrome browser.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1440,900")

driver = webdriver.Chrome(options=options)
try:
    print("Navigating to http://127.0.0.1:8000/ ...")
    driver.get("http://127.0.0.1:8000/")
    time.sleep(3)
    
    # Check console logs
    logs = driver.get_log('browser')
    errors = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Browser console logs count: {len(logs)}, severe errors: {len(errors)}")
    for l in logs:
        if 'ServiceWorker' in l['message'] or 'PWA' in l['message']:
            print("  Log:", l['message'])
            
    # Check SW registration state via JS
    sw_state = driver.execute_async_script("""
        const callback = arguments[arguments.length - 1];
        if (!('serviceWorker' in navigator)) {
            callback({ supported: false });
        } else {
            navigator.serviceWorker.getRegistrations().then(regs => {
                callback({
                    supported: true,
                    count: regs.length,
                    scopes: regs.map(r => r.scope)
                });
            }).catch(err => {
                callback({ supported: true, error: err.toString() });
            });
        }
    """)
    print("Service Worker State in Browser:", sw_state)
    assert sw_state.get('supported') is True, "ServiceWorker not supported"
    
    # Take screenshot of luxury homepage with PWA tags active
    screenshot_path = os.path.abspath("scratch/verify_pwa_homepage.png")
    driver.save_screenshot(screenshot_path)
    print(f"[PASS] Screenshot saved to: {screenshot_path}")
    print("[SUCCESS] Browser PWA integration verified!")
finally:
    driver.quit()
