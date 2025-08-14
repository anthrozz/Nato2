# file: taleo_yesterday_test.py
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
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(90)
    return driver

def click_if_exists(driver, by, selector, wait=4):
    try:
        el = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((by, selector)))
        el.click()
        return True
    except Exception:
        return False

def set_posting_date_yesterday(driver):
    """
    Yesterday = value='com.taleo.careersection.entity.lookup.PostedDate__2'
    Today     = value='com.taleo.careersection.entity.lookup.PostedDate__1'
    """
    # Çerez banner'ı varsa kabul et
    for sel in [
        (By.ID, "onetrust-accept-btn-handler"),
        (By.CSS_SELECTOR, "button[aria-label*='Accept'], button[title*='Accept']"),
    ]:
        if click_if_exists(driver, *sel, wait=2):
            break

    # "Posting Date" alanı bazen sekme/accordion içinde olabilir; açmayı dene
    for sel in [
        (By.XPATH, "//label[@for='advancedSearchInterface.postedDate' and contains(.,'Posting Date')]"),
        (By.XPATH, "//li[@id='advancedSearchInterface.postedDateTab']"),
    ]:
        try:
            el = driver.find_element(*sel)
            driver.execute_script("arguments[0].click();", el)
            break
        except Exception:
            pass

    # YESTERDAY radio input'unu tıkla
    radio_selectors = [
        (By.CSS_SELECTOR, "input[name='postedDate'][value='com.taleo.careersection.entity.lookup.PostedDate__2']"),
        (By.XPATH, "//div[@id='advancedSearchInterface.postedDate']//label[normalize-space()='Yesterday']/preceding-sibling::input[@type='radio']"),
        (By.XPATH, "//input[@name='postedDate' and contains(@value,'PostedDate__2')]"),
    ]
    clicked = False
    for sel in radio_selectors:
        try:
            el = WebDriverWait(driver, 8).until(EC.presence_of_element_located(sel))
            driver.execute_script("arguments[0].click();", el)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        raise RuntimeError("Yesterday seçeneği bulunamadı (radio).")

    # Aramayı başlat: 'Search for Jobs' / 'Search' / submit butonları
    search_clicked = False
    for sel in [
        (By.ID, "advancedSearchFooterInterface.searchAction"),
        (By.XPATH, "//button[contains(.,'Search for Jobs') or contains(.,'Search') or contains(.,'Ara')]"),
        (By.CSS_SELECTOR, "input[type='submit'][value*='Search']"),
    ]:
        if click_if_exists(driver, *sel, wait=5):
            search_clicked = True
            break
    if not search_clicked:
        # Bazı temalarda form submit çalışabilir:
        driver.execute_script("document.querySelector('form').submit();")
    # Sonuçların yüklenmesi için kısa bekleme
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href,'jobdetail.ftl')] | //table | //div[contains(@id,'requisitionListInterface')]")
        )
    )
    time.sleep(2)

def scrape_results(driver, max_items=50):
    jobs = []
    # Yaygın link paterni
    anchors = driver.find_elements(By.XPATH, "//a[contains(@href,'jobdetail.ftl') and (contains(@href,'job=') or contains(@href,'Job='))]")
    for a in anchors[:max_items]:
        title = (a.text or "").strip()
        href = a.get_attribute("href")
        if not href:
            continue
        if not title:
            # Bazı temalarda başlık üstteki span'da olabilir
            title = a.get_attribute("title") or "(No title)"
        jobs.append((title, href))
    return jobs

def main():
    driver = init_driver()
    try:
        driver.get(URL)
        set_posting_date_yesterday(driver)
        jobs = scrape_results(driver)
        if not jobs:
            print("Dün yayınlanan ilan bulunamadı veya liste boş döndü.")
        else:
            print(f"Dün yayınlanan ilanlar (toplam {len(jobs)}):")
            for i, (title, href) in enumerate(jobs, 1):
                print(f"{i:02d}. {title}\n    {href}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()