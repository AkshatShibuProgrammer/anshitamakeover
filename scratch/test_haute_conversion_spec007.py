from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, os, sys
sys.stdout.reconfigure(encoding='utf-8')

def test_spec_007():
    os.makedirs('scratch', exist_ok=True)
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--enable-webgl')
    opts.add_argument('--window-size=1440,950')

    driver = webdriver.Chrome(options=opts)
    try:
        print("Navigating to http://127.0.0.1:8000/ ...")
        driver.get('http://127.0.0.1:8000/')
        time.sleep(2.5)

        # 1. Verify Desktop Inline WhatsApp CTA in Hero
        inline_wa = driver.find_element(By.CSS_SELECTOR, '.btn-whatsapp-inline')
        wa_href = inline_wa.get_attribute('href')
        print(f"Inline WhatsApp CTA found: href={wa_href}")
        assert 'wa.me/917879223442' in wa_href, "Error: WhatsApp number missing in inline CTA!"
        assert 'utm_medium=whatsapp_cta' in wa_href, "Error: UTM tag missing in inline CTA!"

        # 2. Verify Floating WhatsApp FAB
        fab = driver.find_element(By.ID, 'whatsapp-fab')
        fab_href = fab.get_attribute('href')
        print(f"Floating WhatsApp FAB found: href={fab_href}")
        assert 'wa.me/917879223442' in fab_href, "Error: WhatsApp number missing in FAB!"
        pulse_ring = fab.find_element(By.CSS_SELECTOR, '.fab-pulse-ring')
        assert pulse_ring is not None, "Error: Pulse ring missing in WhatsApp FAB!"

        driver.save_screenshot('scratch/verify_whatsapp_fab.png')
        print("Saved scratch/verify_whatsapp_fab.png")

        # 3. Verify Dual-Direction Marquee Strip
        marquee = driver.find_element(By.CSS_SELECTOR, '.marquee-band')
        fwd_track = marquee.find_element(By.CSS_SELECTOR, '.marquee-fwd')
        rev_track = marquee.find_element(By.CSS_SELECTOR, '.marquee-rev')
        assert fwd_track is not None and rev_track is not None, "Error: Marquee tracks missing!"
        print(f"Marquee tracks verified: fwd items={len(fwd_track.find_elements(By.CSS_SELECTOR, '.mq-item'))}, rev items={len(rev_track.find_elements(By.CSS_SELECTOR, '.mq-item'))}")

        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", marquee)
        time.sleep(1)
        driver.save_screenshot('scratch/verify_marquee_strip.png')
        print("Saved scratch/verify_marquee_strip.png")

        # 4. Verify Metric Counters Band (1200+ Brides, 15 Cities, 12+ Years)
        metrics_band = driver.find_element(By.ID, 'metrics-band')
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", metrics_band)
        time.sleep(3.5) # wait for countUp to reach final targets
        m_brides = driver.find_element(By.ID, 'metric-brides').text
        m_cities = driver.find_element(By.ID, 'metric-cities').text
        m_years = driver.find_element(By.ID, 'metric-years').text
        print(f"Metric counters: Brides={m_brides}, Cities={m_cities}, Years={m_years}")
        assert "1200" in m_brides, f"Expected 1200 in {m_brides}"
        assert "15" in m_cities, f"Expected 15 in {m_cities}"
        assert "12" in m_years, f"Expected 12 in {m_years}"

        driver.save_screenshot('scratch/verify_metric_counters.png')
        print("Saved scratch/verify_metric_counters.png")

        print("ALL SPEC-007 HAUTE CONVERSION ACCEPTANCE CRITERIA VERIFIED!")
    finally:
        driver.quit()

if __name__ == '__main__':
    test_spec_007()
