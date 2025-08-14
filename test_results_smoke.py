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

def click_if_exists(driver, by, sel, wait=5):
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

        # "Search" / "Search for Jobs" butonuna bas (filtresiz)
        if not click_if_exists(driver, By.ID, "advancedSearchFooterInterface.searchAction", wait=4):
            click_if_exists(driver, By.XPATH, "//button[contains(.,'Search for Jobs') or contains(.,'Search')]", wait=6)

        # Sonuçlar görünene kadar bekle
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'jobdetail.ftl')] | //div[contains(@id,'requisitionListInterface')]")
            )
        )
        time.sleep(2)

        # İlk 10 ilanı yazdır
        anchors = driver.find_elements(By.XPATH, "//a[contains(@href,'jobdetail.ftl')]")
        print(f"Bulunan anchor sayısı: {len(anchors)}")
        for i, a in enumerate(anchors[:3], 1):
            title = (a.text or a.get_attribute("title") or "").strip() or "(No title)"
            href = a.get_attribute("href")
            print(f"{i:02d}. {title}\n    {href}")

        driver.save_screenshot("search_results.png")
        print("Screenshot kaydedildi: search_results.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()