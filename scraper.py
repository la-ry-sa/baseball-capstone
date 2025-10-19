# Scrapes yearly MLB statistics (Batting, Pitching, Fielding, Standings, etc.)
# from Baseball-Almanac and saves each dataset as a CSV file.

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#  SETUP
options = Options()
options.add_argument("--headless=new")          
options.add_argument("--disable-gpu")           
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--blink-settings=imagesEnabled=false")  
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/126.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#  STEP 1 — COLLECT YEAR LINKS
#  Smaller range for performance — can be adjusted as needed.

driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'yr') and contains(@href, 'a.shtml')]"))
)

links = driver.find_elements(By.XPATH, "//a[contains(@href, 'yr') and contains(@href, 'a.shtml')]")
years = [int(link.text) for link in links if link.text.isdigit() and 2000 <= int(link.text) <= 2025]
print(f"Found {len(years)} years: {years[:5]} ... {years[-5:]}")

#  STEP 2 — SCRAPE EACH YEAR

for year in years:
    url = f"https://www.baseball-almanac.com/yearly/yr{year}a.shtml"
    print(f"\n📅 Fetching {year}: {url}")
    driver.get(url)
    time.sleep(1)

    try:
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        time.sleep(1)

        tables = pd.read_html(driver.page_source)
        print(f"   Found {len(tables)} tables")

        for i, table in enumerate(tables):
            # Inspect first few rows to determine category
            text_preview = " ".join(table.astype(str).head(4).stack().tolist()).lower()

            if "pitching" in text_preview:
                category = "pitching"
            elif "batting" in text_preview:
                category = "batting"
            elif "fielding" in text_preview:
                category = "fielding"
            elif "team" in text_preview and "standings" in text_preview:
                category = "standings"
            else:
                category = f"misc_{i+1}"

            filename = f"data/{category}_{year}.csv"
            table.to_csv(filename, index=False)
            print(f"   ✅ Saved {filename} ({len(table)} rows)")

    except Exception as e:
        print(f"   ❌ {year} failed — {e}")
        with open("scrape_errors.log", "a") as log:
            log.write(f"{year} FAILED: {e}\n")

driver.quit()
print("\n Done.")
