# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

URL = "https://nato.taleo.net/careersection/2/moresearch.ftl"

def init_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,1000")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def click_if_exists(driver, by, sel, wait=4):
    try:
        el = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((by, sel)))
        el.click()
        return True
    except Exception:
        return False

def main():
    driver = init_driver()
    try:
        driver.get(URL)

        # Çerez banner'ı varsa kapat
        for sel in [(By.ID, "onetrust-accept-btn-handler"),
                    (By.CSS_SELECTOR, "button[aria-label*='Accept'], button[title*='Accept']")]:
            if click_if_exists(driver, *sel, wait=2): break

        # Posting Date panelini görünür yap
        # Bazı temalarda sekme/label tıklamak gerekebiliyor
        for sel in [
            (By.XPATH, "//label[@for='advancedSearchInterface.postedDate' and contains(.,'Posting Date')]"),
            (By.ID, "advancedSearchInterface.postedDateTab"),
        ]:
            try:
                el = driver.find_element(*sel)
                driver.execute_script("arguments[0].click();", el)
                break
            except Exception:
                pass

        # Paneli bul ve içindeki label'ları oku
        panel = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "advancedSearchInterface.postedDate"))
        )
        time.sleep(1)
        labels = panel.find_elements(By.CSS_SELECTOR, "label.searchLookuptext")
        texts = [l.text.strip() for l in labels if l.text.strip()]
        print("Posting Date seçenekleri:", ", ".join(texts) if texts else "(bulunamadı)")

        # Ekran görüntüsü
        driver.save_screenshot("posting_date_panel.png")
        print("Screenshot kaydedildi: posting_date_panel.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()