from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time, os, sys
sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    os.makedirs('scratch', exist_ok=True)
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--enable-webgl')
    opts.add_argument('--window-size=1400,950')

    driver = webdriver.Chrome(options=opts)
    try:
        print("Navigating to http://127.0.0.1:8000/ ...")
        driver.get('http://127.0.0.1:8000/')
        time.sleep(3)

        # 1. Verify chat toggle wrap exists and mascot canvas
        toggle_wrap = driver.find_element(By.ID, 'chat-toggle-wrap')
        asha_canvas = driver.find_element(By.ID, 'ashaMascotCanvas')
        bunny_canvas = driver.find_element(By.ID, 'bunnyMascotCanvas')
        print(f"Canvas check: Asha={asha_canvas.is_displayed()}, Bunny={bunny_canvas.is_displayed()}")

        # 2. Open chat
        chat_toggle_btn = driver.find_element(By.ID, 'chat-toggle')
        driver.execute_script("arguments[0].click();", chat_toggle_btn)
        time.sleep(1)

        # Verify speech bubble is NOT visible while chat is open
        bubble = driver.find_element(By.ID, 'chat-speech-bubble')
        is_bubble_active = 'active' in (bubble.get_attribute('class') or '')
        body_has_chat_open = 'chat-is-open' in (driver.find_element(By.TAG_NAME, 'body').get_attribute('class') or '')
        print(f"Chat open verification: body_has_chat_open={body_has_chat_open}, bubble_active={is_bubble_active}")
        assert body_has_chat_open, "Error: body should have chat-is-open class!"

        # 3. Test Character Switcher button (switch from Asha to Bunny)
        char_toggle_btn = driver.find_element(By.ID, 'chat-char-toggle-btn')
        driver.execute_script("arguments[0].click();", char_toggle_btn)
        time.sleep(1)
        char_name = driver.find_element(By.ID, 'conciergeCharName').text
        print(f"After character switch: {char_name}")
        assert "Bunny" in char_name, f"Expected Bunny in {char_name}"

        # 4. Test Greeting 'राम राम' -> triggers ram_ram emotion
        inp = driver.find_element(By.ID, 'chat-inp')
        inp.send_keys("राम राम जी")
        inp.send_keys(Keys.ENTER)
        time.sleep(1.5)

        mood_badge = driver.find_element(By.ID, 'ashaLiveMoodBadge')
        print(f"Mood after 'राम राम जी': {mood_badge.text}")
        assert "राम राम" in mood_badge.text, f"Expected ram_ram in {mood_badge.text}"

        # Capture screenshot of chat with Bunny and Ram Ram
        driver.save_screenshot('scratch/chat_bunny_ram_ram.png')

        # 5. Test Discount Query -> triggers thinking / coupon
        inp.send_keys("Any discount or coupon code?")
        inp.send_keys(Keys.ENTER)
        time.sleep(1.5)
        print(f"Mood after coupon query: {mood_badge.text}")

        # 6. Test Deal Confirmation -> triggers celebrating
        inp.send_keys("yes I want to book this bridal package")
        inp.send_keys(Keys.ENTER)
        time.sleep(1.5)
        print(f"Mood after booking query: {mood_badge.text}")

        driver.save_screenshot('scratch/chat_bunny_deal_done.png')

        # 7. Switch back to Asha
        driver.execute_script("arguments[0].click();", char_toggle_btn)
        time.sleep(1)
        char_name2 = driver.find_element(By.ID, 'conciergeCharName').text
        print(f"Switched back to: {char_name2}")
        assert "Asha" in char_name2, f"Expected Asha in {char_name2}"

        # 8. Close chat -> verify closing chat restores state
        close_btn = driver.find_element(By.CSS_SELECTOR, '.chat-close-btn')
        driver.execute_script("arguments[0].click();", close_btn)
        time.sleep(1)
        body_has_chat_open_closed = 'chat-is-open' in (driver.find_element(By.TAG_NAME, 'body').get_attribute('class') or '')
        print(f"Chat closed verification: body_has_chat_open={body_has_chat_open_closed}")
        assert not body_has_chat_open_closed, "Error: chat should be closed!"

        print("ALL CHARACTER & CHAT EMOTION TESTS PASSED!")
    finally:
        driver.quit()

if __name__ == '__main__':
    run_tests()
