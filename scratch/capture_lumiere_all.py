from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opt = Options()
opt.add_argument('--headless=new')
opt.add_argument('--window-size=1600,1000')
driver = webdriver.Chrome(options=opt)
driver.get('file:///f:/Code%20by%20Akshat/Anshita/anshitamakeover%20aiarena/workspace-01a06312-9f47-7052-a276-d661b1051b1c/characters_lumiere.html')
time.sleep(3)

chars = ['asha', 'mochi', 'noor', 'tara', 'gia']
for c in chars:
    driver.execute_script(f"""
        var p = document.querySelector('.pill[data-id="{c}"]');
        if (p) p.click();
    """)
    time.sleep(2)
    path = f'scratch/lumiere_{c}.png'
    driver.save_screenshot(path)
    print('Captured', c, 'to', path)

driver.quit()
