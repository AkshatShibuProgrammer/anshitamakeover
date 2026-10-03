from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, os

opt = Options()
opt.add_argument('--headless=new')
opt.add_argument('--no-sandbox')
opt.add_argument('--window-size=1600,1000')
opt.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(options=opt)
driver.get('file:///F:/Code%20by%20Akshat/Anshita/anshitamakeover%20aiarena/workspace-01a06312-9f47-7052-a276-d661b1051b1c/characters_showcase.html')
time.sleep(3)

time.sleep(2)
out_path = os.path.join('scratch', 'characters_showcase_full_ui.png')
driver.save_screenshot(out_path)
print('Saved full UI screenshot ->', out_path, 'size:', os.path.getsize(out_path))
driver.quit()
