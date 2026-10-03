from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1600,1000')
driver = webdriver.Chrome(options=chrome_options)

url = 'file:///f:/Code%20by%20Akshat/Anshita/anshitamakeover%20aiarena/workspace-01a06312-9f47-7052-a276-d661b1051b1c/characters_aurelle.html'
driver.get(url)
time.sleep(3)

os.makedirs('scratch', exist_ok=True)
characters = ['asha', 'mochi', 'noor', 'tara', 'gia']
for char in characters:
    driver.execute_script(f"""
        const pill = document.querySelector('.character-pill[data-character="{char}"]');
        if (pill) pill.click();
    """)
    time.sleep(2.0)
    # Ensure transition curtain has completely dissolved
    driver.execute_script("""
        const cur = document.getElementById('transition');
        if (cur) cur.style.opacity = '0';
    """)
    time.sleep(0.3)
    path = f'scratch/aurelle_cute_{char}.png'
    driver.save_screenshot(path)
    print(f'Captured {char} to {path}')

driver.quit()
